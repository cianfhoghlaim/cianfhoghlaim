from transformers import Trainer
import torch
from transformers.models.clap.convert_clap_original_pytorch_to_hf import processor


class VQATrainer(Trainer):
    def __init__(self, vqa_processor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = vqa_processor

    def compute_loss(self, model, inputs, return_outputs=False,
                     num_items_in_batch=None):
        pass


def compute_metrics(eval_pred):
    predictions, labels = eval_pred

    # Decode predictions and labels
    pred_token_ids = torch.argmax(torch.tensor(predictions), dim=-1)
    pred_answers = processor.batch_decode(pred_token_ids)
    ref_answers = processor.batch_decode(labels)

    # Calculate VQA accuracy
    scores = []
    for pred, ref in zip(pred_answers, ref_answers):
        score = min(1.0 if pred == ref else 0.0, 1)
        scores.append(score)

    return {
        "vqa_accuracy": sum(scores) / len(scores)
    }