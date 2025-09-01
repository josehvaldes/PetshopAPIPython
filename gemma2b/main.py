
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "c:/personal/_gemma/model/gemma-2b-it"  # local folder

tokenizer = AutoTokenizer.from_pretrained(model_path)

messages = [
    {"role": "user", "content": "Hello from my local Gemma 2B!"},
    {"role": "assistant", "content": "Helpful assistant message."}    
]

# --- Safe apply_chat_template with fallback ---
def build_prompt(messages):
    """Try to use chat_template; fallback to manual prompt if missing."""
    if getattr(tokenizer, "chat_template", None):
        # Model has a chat template
        print("Using chat template")
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    else:
        # Manual fallback for base models
        print("Falling back to manual prompt")
        prompt_parts = []
        for m in messages:
            role = m["role"].capitalize()
            prompt_parts.append(f"{role}: {m['content']}")
        prompt_parts.append("Assistant:")  # generation cue
        return "\n".join(prompt_parts)

prompt = build_prompt(messages)
print("Final prompt:\n", prompt)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
print(f"Model loaded on device: {model.device}")

# Tokenize and generate
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
print(f"Input tokens: {inputs['input_ids'].shape}")
print("Generating...")
outputs = model.generate(**inputs, max_new_tokens=150)
print("Generation complete.\n")
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
print("Done:\n")
