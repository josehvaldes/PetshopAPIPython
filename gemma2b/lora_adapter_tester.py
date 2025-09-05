from peft import PeftModel
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "/home/azureuser/model/gemma-2b-it/"  # local folder

base_model = AutoModelForCausalLM.from_pretrained(model_path)
model = PeftModel.from_pretrained(base_model, "./gemma2b-lora-adapter")

tokenizer = AutoTokenizer.from_pretrained(model_path)

# Example inference
inputs = tokenizer("Hello from my local Gemma 2B - IT LoRA!", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

print("\nNext question:\n")
#example 2
inputs = tokenizer("¿cual es el origen del perro Dachshund?", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))