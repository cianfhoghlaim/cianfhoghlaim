import os
from huggingface_hub import login
from transformers import AutoProcessor, AutoModelForImageTextToText, TrainingArguments, DataCollatorForLanguageModeling
from src.datasets.visual_question_answering.vqa_dataset_loader import VQADataset
from src.finetuning_scripts.vqa_finetune.trainers import VQATrainer
from src.finetuning_scripts.vqa_finetune.trainers import compute_metrics
if __name__ == "__main__":
    login(token=os.environ["HF_TOKEN"])
    # Load model directly
    processor = AutoProcessor.from_pretrained("google/paligemma-3b-pt-224")
    model = AutoModelForImageTextToText.from_pretrained("google/paligemma-3b-pt-224")

    # Create VQA dataset
    train_dataset = VQADataset(
        question_csv_path="tests/full_data/vqa-ukrainian/train_questions.csv",
        json_path="tests/full_data/vqa-ukrainian/train_annotations.json",
        base_img_dir="tests/full_data/ImagesDataset",
        processor=processor
    )
    # TODO - Create eval dataset
    eval_dataset = VQADataset(
        question_csv_path="tests/full_data/vqa-ukrainian/train_questions.csv",
        json_path="tests/full_data/vqa-ukrainian/train_annotations.json",
        base_img_dir="tests/full_data/ImagesDataset",
        processor=processor
    )
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./paligemma-vqa-ukrainian",
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=5e-5,
        push_to_hub=False,
        logging_dir="./logs",
        fp16=True,  # Enable mixed precision training
        gradient_accumulation_steps=1,  # Accumulate gradients to simulate larger batch size
    )

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=processor.tokenizer,
        mlm=False
    )

    # Initialize trainer
    trainer = VQATrainer(
        vqa_processor=processor,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        compute_metrics=compute_metrics
    )
    train_dataloader = trainer.get_train_dataloader()
    print(f"Total dataset size: {len(train_dataset)}")
    print(f"Batch size from args: {training_args.per_device_train_batch_size}")
    print(f"Gradient accumulation steps: {training_args.gradient_accumulation_steps}")
    print(f"Expected steps per epoch: {len(train_dataset) // training_args.per_device_train_batch_size}")

    # You can also check the dataloader directly

    print(f"Actual batches in dataloader: {len(train_dataloader)}")

    # Start training
    trainer.train()

    # Save the model
    trainer.save_model("./paligemma-vqa-ukrainian-final")
