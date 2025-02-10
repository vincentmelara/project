# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import GPTNeoForCausalLM, AutoTokenizer
import torch
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Custom LLM Server for Enrollment Predictor")

# Define the request body
class ComparisonRequest(BaseModel):
    prompt: str

# Define the response body
class ComparisonResponse(BaseModel):
    text: str

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the tokenizer and model at startup
@app.on_event("startup")
def load_model():
    global tokenizer, model
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B")
    model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-1.3B")
    model.eval()
    if torch.cuda.is_available():
        model.to("cuda")
    print("GPT-Neo-1.3B model loaded successfully.")

# Endpoint to generate comparison
@app.post("/generate-comparison/", response_model=ComparisonResponse)
def generate_comparison(request: ComparisonRequest):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Empty prompt provided.")

    # Debug: Log the received prompt
    print("Received Prompt:", prompt)

    # Encode the prompt
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.to("cuda") for k, v in inputs.items()}

    # Generate response
    try:
        output = model.generate(
            **inputs,
            max_length=300,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            num_return_sequences=1,
            # Define stop tokens if necessary
        )
        response_text = tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Debug: Log the generated response
        print("Generated Response:", response_text)
        
        return ComparisonResponse(text=response_text)
    except Exception as e:
        print("Error during AI response generation:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
