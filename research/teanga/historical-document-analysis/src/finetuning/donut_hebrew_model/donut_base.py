import os
import torch
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from torch.utils.data import Dataset, DataLoader
from transformers import (
    DonutProcessor,
    VisionEncoderDecoderModel,
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    default_data_collator,
)
from transformers.modeling_outputs import Seq2SeqLMOutput
class HebrewDocumentModel(torch.nn.Module):
    def __init__(
        self,
        encoder_model_id: str = "naver-clova-ix/donut-base",
        decoder_model_id: str = "yam-peleg/Hebrew-Mistral-7B",
        low_cpu_mem_usage: bool = True,
        adapter_hidden_size: int = None,  # Optional intermediate size for large dime
    ):
        super().__init__()

        print("Initializing encoder from", encoder_model_id)
        # Load encoder from Donut
        donut_model = VisionEncoderDecoderModel.from_pretrained(
            encoder_model_id,
            low_cpu_mem_usage=low_cpu_mem_usage
        )
        self.encoder = donut_model.encoder
        self.encoder_hidden_size = self.encoder.config.hidden_size

        print("Initializing decoder from", decoder_model_id)
        # Load Hebrew language model as decoder - works with different model sizes
        self.decoder = AutoModelForCausalLM.from_pretrained(
            decoder_model_id,
            low_cpu_mem_usage=low_cpu_mem_usage,
        )
        self.decoder_hidden_size = self.decoder.config.hidden_size

        # Design adapter based on dimension differences
        print(f"Creating adapter from encoder ({self.encoder_hidden_size}) to decoder ({self.decoder_hidden_size})")
        self.create_adapter(adapter_hidden_size)

        # Set configuration
        self.config = self.decoder.config
        self.tokenizer = AutoTokenizer.from_pretrained("yam-peleg/Hebrew-Mistral-7B")

    def create_adapter(self, adapter_hidden_size=None):
        """
        Create an adapter network that bridges encoder and decoder dimensions.
        Automatically determines the best architecture based on dimensions.
        """
        # If dimensions match exactly, use identity mapping with minimal adjustment
        if self.encoder_hidden_size == self.decoder_hidden_size:
            self.adapter = torch.nn.Sequential(
                torch.nn.Linear(self.encoder_hidden_size, self.decoder_hidden_size),
                torch.nn.LayerNorm(self.decoder_hidden_size),
            )
            print("Using simple adapter (dimensions match)")
            return

        # For small dimension differences (less than 4x), use a direct mapping with nonlinearity
        ratio = max(self.encoder_hidden_size, self.decoder_hidden_size) / min(self.encoder_hidden_size,
                                                                              self.decoder_hidden_size)
        if ratio < 4:
            self.adapter = torch.nn.Sequential(
                torch.nn.Linear(self.encoder_hidden_size, self.decoder_hidden_size),
                torch.nn.GELU(),
                torch.nn.Linear(self.decoder_hidden_size, self.decoder_hidden_size),
                torch.nn.LayerNorm(self.decoder_hidden_size),
            )
            print("Using standard adapter (moderate dimension difference)")
            return

        # For large dimension differences, use a bottleneck or expansion architecture
        if adapter_hidden_size is None:
            # Calculate a reasonable intermediate size if not provided
            adapter_hidden_size = min(
                max(self.encoder_hidden_size, self.decoder_hidden_size),
                2 * min(self.encoder_hidden_size, self.decoder_hidden_size)
            )

        # Large dimension change requires more careful handling
        self.adapter = torch.nn.Sequential(
            torch.nn.Linear(self.encoder_hidden_size, adapter_hidden_size),
            torch.nn.GELU(),
            torch.nn.Linear(adapter_hidden_size, adapter_hidden_size),
            torch.nn.GELU(),
            torch.nn.Linear(adapter_hidden_size, self.decoder_hidden_size),
            torch.nn.LayerNorm(self.decoder_hidden_size),
        )
        print(f"Using advanced adapter with intermediate size {adapter_hidden_size} (large dimension difference)")

    def freeze_decoder_except_first_layers(self, num_unfrozen_layers: int = 2):
        """Freeze most of the decoder parameters except the first few layers"""
        # Freeze all parameters first
        for param in self.decoder.parameters():
            param.requires_grad = False

        # Unfreeze only the first few layers
        unfrozen_params = 0
        decoder_layers = None

        # Handle different decoder architectures
        if hasattr(self.decoder, 'model') and hasattr(self.decoder.model, 'layers'):
            # Mistral style
            decoder_layers = self.decoder.model.layers
        elif hasattr(self.decoder, 'encoder') and hasattr(self.decoder.encoder, 'layer'):
            # BERT style
            decoder_layers = self.decoder.encoder.layer
        elif hasattr(self.decoder, 'transformer') and hasattr(self.decoder.transformer, 'h'):
            # GPT style
            decoder_layers = self.decoder.transformer.h
        elif hasattr(self.decoder, 'layers'):
            # Direct layers
            decoder_layers = self.decoder.layers

        if decoder_layers is not None:
            # Unfreeze the specified number of layers
            for i in range(min(num_unfrozen_layers, len(decoder_layers))):
                for param in decoder_layers[i].parameters():
                    param.requires_grad = True
                    unfrozen_params += param.numel()

        # Always unfreeze the adapter
        for param in self.adapter.parameters():
            param.requires_grad = True
            unfrozen_params += param.numel()

        print(f"Unfrozen parameters: {unfrozen_params:,}")

    def forward(
            self,
            pixel_values: torch.Tensor,
            labels: Optional[torch.Tensor] = None,
            attention_mask: Optional[torch.Tensor] = None,
            decoder_attention_mask: Optional[torch.Tensor] = None,
            return_dict: bool = True,
    ) -> Union[Tuple, Seq2SeqLMOutput]:
        """Forward pass for training"""
        # Get encoder hidden states
        encoder_outputs = self.encoder(pixel_values).last_hidden_state

        # Apply adapter to match dimensions
        adapted_features = self.adapter(encoder_outputs)

        # Prepare decoder inputs
        batch_size = adapted_features.shape[0]
        seq_length = adapted_features.shape[1]

        # Create a causal mask for the decoder
        if decoder_attention_mask is None:
            decoder_attention_mask = torch.ones(batch_size, seq_length, device=adapted_features.device)

        # Forward through decoder - handle different model architectures
        if hasattr(self.decoder, 'forward') and 'inputs_embeds' in self.decoder.forward.__code__.co_varnames:
            # Standard decoder with inputs_embeds support
            outputs = self.decoder(
                inputs_embeds=adapted_features,
                attention_mask=decoder_attention_mask,
                labels=labels,
                return_dict=return_dict,
            )
        else:
            # Fall back to a more generic approach
            # This is a simplified version - may need customization for specific model architectures
            outputs = self.decoder(
                hidden_states=adapted_features,
                attention_mask=decoder_attention_mask,
                labels=labels,
                return_dict=return_dict,
            )

        return outputs

    def generate(
            self,
            pixel_values: torch.Tensor,
            max_length: int = 256,
            num_beams: int = 4,
            **kwargs
    ) -> torch.Tensor:
        """Generate text from image"""
        # Get encoder hidden states
        encoder_outputs = self.encoder(pixel_values).last_hidden_state
        if encoder_outputs.shape[1] > max_length:
            print(f"Testing mode: Restricting sequence length from {encoder_outputs.shape[1]} to {max_length}")
            encoder_outputs = encoder_outputs[:, :max_length :]
        # Apply adapter
        adapted_features = self.adapter(encoder_outputs)

        # Generate from decoder
        generated_ids = self.decoder.generate(
            inputs_embeds=adapted_features,
            max_length=max_length,
            num_beams=num_beams,
            **kwargs
        )

        return generated_ids