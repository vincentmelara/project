# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enrollment_predictor import process_enrollment_data, prepare_ai_context
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import torch
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="Enrollment Predictor API")

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend's URL if different
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic models
class EnrollmentData(BaseModel):
    year: int
    students: int
    type: str  # 'historical' or 'predicted'

class ComparisonRequest(BaseModel):
    prompt: str

class ComparisonResponse(BaseModel):
    text: str

class EnrollmentDataResponse(BaseModel):
    historical: list[EnrollmentData]
    predicted: list[EnrollmentData]
    ai_context: str

# Initialize GPT Neo Model and Tokenizer
@app.on_event("startup")
def load_model():
    global model, tokenizer, device
    try:
        logger.info("Loading GPT Neo 1.3B model...")
        tokenizer = GPT2Tokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B")
        model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-1.3B")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        logger.info("GPT Neo model loaded successfully.")

        # **Set pad_token_id to eos_token_id if not already set**
        if tokenizer.pad_token_id is None:
            if tokenizer.eos_token_id is not None:
                tokenizer.pad_token = tokenizer.eos_token
                model.config.pad_token_id = tokenizer.eos_token_id
                logger.info("Set pad_token_id to eos_token_id.")
            else:
                # If eos_token_id is also None, define a pad token manually
                tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                model.resize_token_embeddings(len(tokenizer))
                model.config.pad_token_id = tokenizer.eos_token_id  # Assuming eos_token_id exists
                logger.info("Added and set pad_token_id manually.")
    except Exception as e:
        logger.error(f"Error loading GPT Neo model: {e}")

# Endpoint to get processed enrollment data
@app.get("/api/enrollment-data", response_model=EnrollmentDataResponse)
def get_enrollment_data():
    try:
        # Historical records as per your data
        historical_records = [
            {"year": 2019, "students": 11047, "type": "historical"},
            {"year": 2020, "students": 11317, "type": "historical"},
            {"year": 2021, "students": 11491, "type": "historical"},
            {"year": 2022, "students": 11384, "type": "historical"},
            {"year": 2023, "students": 11407, "type": "historical"}
        ]

        # Predicted records from process_enrollment_data
        predicted_records = process_enrollment_data()

        combined_data = historical_records + predicted_records
        ai_context = prepare_ai_context(combined_data)

        return EnrollmentDataResponse(
            historical=historical_records,
            predicted=predicted_records,
            ai_context=ai_context
        )
    except Exception as e:
        logger.error(f"Error processing enrollment data: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing enrollment data.")

# Endpoint to generate AI comparison using GPT Neo
@app.post("/api/generate-comparison", response_model=ComparisonResponse)
def generate_comparison(request: ComparisonRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        # Encode the prompt with attention_mask
        encoding = tokenizer.encode_plus(
            prompt,
            return_tensors="pt",
            padding=True,  # Ensure padding is handled
            truncation=True,  # Truncate if prompt is too long
            max_length=1024,  # Adjust based on model's max context size
            return_attention_mask=True
        )

        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)

        # Generate a response using GPT Neo
        output = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=1500,  # Increased max_length to allow for detailed reports
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id  # Ensure pad_token_id is set
        )

        # Decode the generated response
        ai_response = tokenizer.decode(output[0], skip_special_tokens=True)

        # Optionally, remove the prompt from the response
        if ai_response.startswith(prompt):
            ai_response = ai_response[len(prompt):].strip()

        # Ensure the AI response is not empty
        if not ai_response:
            raise ValueError("AI response is empty.")

        return ComparisonResponse(text=ai_response)
    except Exception as e:
        logger.error(f"Error generating comparison: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the comparison.")
