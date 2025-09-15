# %%
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import pipeline

model_path = "h:/ML_Models/_gemma/model/gemma-2b-it"  # local folder

tokenizer = AutoTokenizer.from_pretrained(model_path)

model = AutoModelForCausalLM.from_pretrained(model_path)
print("Model loaded.")


# %%
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512)
llm = HuggingFacePipeline(pipeline=pipe)
print("Pipeline loaded.")


prompt = PromptTemplate.from_template("Answer like a helpful agent: {question}")
chain = LLMChain(llm=llm, prompt=prompt)

response = chain.run("which dogs are good for apartments?")
print(response)
print("Response generated.")


