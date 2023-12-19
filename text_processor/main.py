from transformers import pipeline

# # For measuring the inference time.
import time

# import pandas as pd
from urllib.parse import unquote
from fastapi import FastAPI
import uvicorn


app = FastAPI()
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.get("/")
def read_root():
    return "Text summarization app"

@app.get("/")
def summarize(text: str):
  
  print(text)
  
  sum_text = summarizer(text, max_length=130, min_length=30, do_sample=False)
  
  return {"text": sum_text}
  
if __name__ == "__main__":
    print("test")
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)