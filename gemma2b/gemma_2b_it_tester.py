
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "c:/personal/_gemma/model/gemma-2b-it"  # local folder

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# Example inference
inputs = tokenizer("Hello from my local Gemma 2B!", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

print("\nNext question:\n")
#example 2
inputs = tokenizer("Write a poem about the sea.", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))