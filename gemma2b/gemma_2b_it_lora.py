from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
import torch

from transformers import BitsAndBytesConfig

# Tokenization function
def tokenize_function(example):
    prompt = example["instruction"] + "\n" + example["input"]
    tokenized = tokenizer(
        prompt,
        truncation=True,
        padding="max_length",
        max_length=256
    )
    tokenized["labels"] = tokenized["input_ids"]  # Self-supervised: input = target
    return tokenized


#not used for now
def tokenize_function_suppervised_traning(example):
    model_input = tokenizer(
        example["input"],
        truncation=True,
        padding="max_length",
        max_length=256
    )
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            example["output"],
            truncation=True,
            padding="max_length",
            max_length=256
        )
    model_input["labels"] = labels["input_ids"]
    return model_input



bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# Load base Gemma 2B model in 4-bit for VRAM efficiency
model_path = "/home/azureuser/model/gemma-2b-it/"  # local folder
custom_docs_path = "/home/azureuser/processed/"  # local folder

tokenizer = AutoTokenizer.from_pretrained(model_path)
print("Tokenizer loaded.")
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=bnb_config,
    device_map="auto",
    low_cpu_mem_usage=True #solve out of memory error (https://huggingface.co/docs/transformers/main/en/main_classes/model#transformers.PreTrainedModel.from_pretrained
)
print("Model loaded.")
# Define LoRA adapter configuration
lora_config = LoraConfig(
    r=16,                             # Rank of LoRA matrices
    lora_alpha=32,                    # Scaling factor
    target_modules=["q_proj", "v_proj"], # Which layers to adapt
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Attach LoRA adapter to the model

model = get_peft_model(model, lora_config)
print("LoRA adapter added to model.")
model.print_trainable_parameters()  # Verify only LoRA params are trainable

# Load your dataset (replace with your static corpus)
print(f"Loading dataset from: {custom_docs_path}")
dataset = load_dataset(custom_docs_path)

# train_data = dataset["train"].map(
#     lambda x: tokenizer(x["input"], truncation=True, padding="max_length", max_length=256),
#     batched=True
# )

train_data = dataset["train"].map(tokenize_function, batched=False)

# Training arguments
training_args = TrainingArguments(
    output_dir="./gemma2b-lora",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    num_train_epochs=3,
    logging_steps=10,
    save_strategy="epoch",
    fp16=True,
    optim="paged_adamw_8bit",
    save_steps=500,
    eval_strategy="no",  # since it's unsupervised
)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
    tokenizer=tokenizer
)

print("Starting LoRA adapter training...")
# Train the adapter
trainer.train()

print("Training finished.")
# Save adapter weights (small file, can be swapped in/out)
model.save_pretrained("./gemma2b-lora-adapter")

print("✅ LoRA adapter training complete!")
