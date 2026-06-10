import torch
import traceback
import logging


def direct_model_inspection(provider):
    """
    Direct inspection of the model to understand the architecture and parameter flow.
    """
    logger = provider.logger
    model = provider.model

    logger.info("\n" + "=" * 80)
    logger.info("DIRECT MODEL ARCHITECTURE INSPECTION")
    logger.info("=" * 80)

    # 1. Show model type and basic info
    logger.info(f"Model type: {type(model).__name__}")
    logger.info(f"Model config type: {type(model.config).__name__}")

    if hasattr(model, 'config'):
        config_dict = model.config.to_dict()
        logger.info("Key config parameters:")
        for key in ['model_type', 'architectures', 'vision_config', 'text_config']:
            if key in config_dict:
                logger.info(f"  {key}: {config_dict[key]}")

    # 2. Show all top-level modules
    logger.info(f"\nTop-level modules:")
    for name, module in model.named_children():
        param_count = sum(p.numel() for p in module.parameters())
        trainable_count = sum(p.numel() for p in module.parameters() if p.requires_grad)
        logger.info(f"  {name}: {type(module).__name__} ({param_count:,} params, {trainable_count:,} trainable)")

    # 3. Check for specific multimodal components
    logger.info(f"\nLooking for multimodal components:")
    multimodal_components = []

    for name, module in model.named_modules():
        module_name_lower = name.lower()
        if any(keyword in module_name_lower for keyword in
               ['vision', 'siglip', 'visual', 'image', 'multimodal', 'cross']):
            param_count = sum(p.numel() for p in module.parameters())
            if param_count > 0:
                trainable_count = sum(p.numel() for p in module.parameters() if p.requires_grad)
                multimodal_components.append({
                    'name': name,
                    'type': type(module).__name__,
                    'params': param_count,
                    'trainable': trainable_count
                })

    if multimodal_components:
        logger.info("Found multimodal components:")
        for comp in multimodal_components[:10]:  # Show first 10
            status = "TRAINABLE" if comp['trainable'] > 0 else "FROZEN"
            logger.info(f"  {status}: {comp['name']} ({comp['type']}) - {comp['params']:,} params")
    else:
        logger.info("❌ NO multimodal components found - this might be a text-only model!")

    # 4. Test a simple forward pass to see what's actually used
    logger.info(f"\n" + "=" * 50)
    logger.info("TESTING SIMPLE FORWARD PASS")
    logger.info("=" * 50)

    try:
        device = next(model.parameters()).device

        # Create minimal input
        input_ids = torch.tensor([[1, 2, 3, 4, 5]], device=device)  # Simple token sequence
        attention_mask = torch.ones_like(input_ids)

        # Hook to track which parameters are actually used
        used_modules = set()

        def forward_hook(module, input, output):
            for name, param in model.named_parameters():
                if param is not None:
                    for p in module.parameters():
                        if p is param:
                            used_modules.add(name)
                            break

        # Register hooks on all modules
        hooks = []
        for name, module in model.named_modules():
            if len(list(module.parameters())) > 0:  # Only modules with parameters
                hook = module.register_forward_hook(forward_hook)
                hooks.append(hook)

        # Forward pass
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)

        # Remove hooks
        for hook in hooks:
            hook.remove()

        logger.info(
            f"Forward pass completed. Output keys: {list(outputs.keys()) if hasattr(outputs, 'keys') else 'No keys'}")

        if hasattr(outputs, 'logits'):
            logger.info(f"Logits shape: {outputs.logits.shape}")

        # Check which trainable parameters were actually used
        trainable_params = {name for name, param in model.named_parameters() if param.requires_grad}
        used_trainable = used_modules.intersection(trainable_params)
        unused_trainable = trainable_params - used_modules

        logger.info(f"\nParameter usage analysis:")
        logger.info(f"  Total trainable parameters: {len(trainable_params)}")
        logger.info(f"  Used trainable parameters: {len(used_trainable)}")
        logger.info(f"  Unused trainable parameters: {len(unused_trainable)}")

        if unused_trainable:
            logger.info("Unused trainable parameters (first 10):")
            for param in list(unused_trainable)[:10]:
                logger.info(f"    ❌ {param}")

        if used_trainable:
            logger.info("Used trainable parameters (first 10):")
            for param in list(used_trainable)[:10]:
                logger.info(f"    ✅ {param}")

        return len(used_trainable) > 0

    except Exception as e:
        logger.error(f"Error in forward pass test: {e}")
        return False


def fix_parameter_connection(provider):
    """
    Try to fix the parameter connection issue by ensuring the right components are trainable.
    """
    logger = provider.logger
    model = provider.model

    logger.info(f"\n" + "=" * 50)
    logger.info("FIXING PARAMETER CONNECTION")
    logger.info("=" * 50)

    # First, freeze everything
    for param in model.parameters():
        param.requires_grad = False

    # Strategy: Find the main language model components and unfreeze those
    # This ensures we have trainable parameters in the main forward path

    unfrozen_count = 0

    # 1. Unfreeze embedding layers (these are always in the forward path)
    for name, param in model.named_parameters():
        if 'embed' in name.lower() and 'pos' not in name.lower():  # Word embeddings, not positional
            param.requires_grad = True
            unfrozen_count += 1
            logger.info(f"✅ Unfroze embedding: {name}")

    # 2. Unfreeze the output layer (lm_head) - essential for generation
    for name, param in model.named_parameters():
        if 'lm_head' in name.lower() or ('head' in name.lower() and 'embed' not in name.lower()):
            param.requires_grad = True
            unfrozen_count += 1
            logger.info(f"✅ Unfroze output head: {name}")

    # 3. Unfreeze some transformer layers (guaranteed to be in forward path)
    layer_patterns = ['layers', 'layer', 'blocks', 'block']
    unfrozen_layers = 0
    max_layers = 3  # Start with just a few layers

    for name, param in model.named_parameters():
        if unfrozen_layers < max_layers:
            if any(pattern in name.lower() for pattern in layer_patterns):
                # Look for attention or MLP components in the last few layers
                if any(component in name.lower() for component in ['attention', 'mlp', 'feed_forward']):
                    param.requires_grad = True
                    unfrozen_count += 1
                    unfrozen_layers += 1
                    logger.info(f"✅ Unfroze transformer layer: {name}")

    # Report results
    final_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    final_total = sum(p.numel() for p in model.parameters())

    logger.info(f"\nConnection fix results:")
    logger.info(f"  Parameters unfrozen: {unfrozen_count}")
    logger.info(f"  Trainable parameters: {final_trainable:,}")
    logger.info(f"  Total parameters: {final_total:,}")
    logger.info(f"  Trainable ratio: {final_trainable / final_total:.4%}")

    return unfrozen_count > 0


def test_gradient_flow_simple(provider):
    """
    Very simple gradient test focusing on core language modeling.
    """
    logger = provider.logger
    model = provider.model

    logger.info(f"\n" + "=" * 40)
    logger.info("SIMPLE GRADIENT FLOW TEST")
    logger.info("=" * 40)

    try:
        model.train()
        device = next(model.parameters()).device

        # Create simple input
        input_ids = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]], device=device, dtype=torch.long)
        attention_mask = torch.ones_like(input_ids)

        logger.info(f"Input shape: {input_ids.shape}")

        # Forward pass
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)

        if hasattr(outputs, 'logits'):
            logits = outputs.logits
            logger.info(f"✅ Got logits: {logits.shape}")

            # Simple loss computation
            # Create labels by shifting input_ids
            labels = input_ids.clone()

            # Standard causal language modeling loss
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()

            loss_fn = torch.nn.CrossEntropyLoss()
            loss = loss_fn(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

            logger.info(f"✅ Computed loss: {loss.item():.6f}")
            logger.info(f"Loss requires_grad: {loss.requires_grad}")

            if loss.requires_grad:
                # Backward pass
                loss.backward()

                # Check gradients
                grad_count = 0
                for name, param in model.named_parameters():
                    if param.requires_grad and param.grad is not None:
                        grad_count += 1

                logger.info(f"✅ Parameters with gradients: {grad_count}")

                model.zero_grad()
                return grad_count > 0
            else:
                logger.error("❌ Loss does not require gradients!")
                return False

        else:
            logger.error("❌ No logits in output")
            return False

    except Exception as e:
        logger.error(f"❌ Simple gradient test failed: {e}")
        logger.error(traceback.format_exc())
        return False


def complete_diagnostic_and_fix(provider):
    """
    Complete diagnostic that should definitively identify and fix the issue.
    """
    logger = provider.logger

    logger.info("\n" + "=" * 80)
    logger.info("COMPLETE DIAGNOSTIC AND FIX")
    logger.info("=" * 80)

    # Step 1: Inspect model architecture
    logger.info("Step 1: Model architecture inspection")
    has_multimodal = direct_model_inspection(provider)

    # Step 2: Fix parameter connections
    logger.info("\nStep 2: Fix parameter connections")
    connection_fixed = fix_parameter_connection(provider)

    if not connection_fixed:
        logger.error("Failed to establish parameter connections")
        return False

    # Step 3: Test gradient flow
    logger.info("\nStep 3: Test gradient flow")
    gradients_work = test_gradient_flow_simple(provider)
    if gradients_work:
        logger.info("\n🎉 DIAGNOSTIC AND FIX SUCCESSFUL!")
        logger.info("The model should now work for training")
        return True
    else:
        logger.error("\n❌ DIAGNOSTIC AND FIX FAILED")
        logger.error("There may be a fundamental issue with the model architecture")
        return False


# Alternative: Patch the model to properly handle tied weights
def patch_model_for_tied_weights(model):
    """
    Patch the model to handle tied weights properly during saving.
    This is a more elegant solution that works at the model level.
    """
    original_state_dict = model.state_dict

    def patched_state_dict(self, *args, **kwargs):
        """Patched state_dict that handles tied weights."""
        state_dict = original_state_dict(*args, **kwargs)

        # Check for tied weights and handle them
        if hasattr(self, 'get_output_embeddings') and hasattr(self, 'get_input_embeddings'):
            output_embeddings = self.get_output_embeddings()
            input_embeddings = self.get_input_embeddings()

            if (output_embeddings is not None and input_embeddings is not None and
                    output_embeddings.weight is input_embeddings.weight):

                # Clone the tied weight for one of the references
                embed_key = None
                lm_head_key = None

                for key in state_dict.keys():
                    if 'embed_tokens.weight' in key:
                        embed_key = key
                    elif 'lm_head.weight' in key:
                        lm_head_key = key

                if embed_key and lm_head_key and embed_key in state_dict and lm_head_key in state_dict:
                    # Clone one of them to break the memory sharing
                    state_dict[lm_head_key] = state_dict[lm_head_key].clone()

        return state_dict

    # Patch the method
    model.state_dict = patched_state_dict.__get__(model, type(model))
    return model
