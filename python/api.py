# api.py

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO
from database import SessionLocal, engine
import models
import logging
from schemas import MailingInfoCreate, MailingInfoListResponse, MailingInfoResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Background task to process CSV
def process_csv(file_content: str, db_session_factory):
    try:
        db = db_session_factory()
        # Read CSV with all columns as strings and do not convert empty strings to NaN
        df = pd.read_csv(StringIO(file_content), dtype=str, keep_default_na=False)
        
        expected_columns = {
            'Mailing City',
            'Mailing State/Province',
            'Mailing Zip/Postal Code',
            'Mailing Country',
            'Start Term and Year'
        }
        if not expected_columns.issubset(df.columns):
            missing = expected_columns - set(df.columns)
            logger.error(f"Missing columns in CSV: {missing}")
            return {"status": "error", "detail": f"Missing columns: {', '.join(missing)}"}

        # Rename columns to match model fields
        column_mapping = {
            'Mailing City': 'mailing_city',
            'Mailing State/Province': 'mailing_state_province',
            'Mailing Zip/Postal Code': 'mailing_zip_postal_code',
            'Mailing Country': 'mailing_country',
            'Start Term and Year': 'start_term_year'
        }
        df.rename(columns=column_mapping, inplace=True)

        # Replace 'nan' strings with empty strings
        df.replace('nan', '', inplace=True)

        # Optionally, remove rows where required fields are empty
        df = df[df['mailing_zip_postal_code'].str.strip() != '']

        # Validate and prepare data
        records = []
        for index, row in df.iterrows():
            try:
                mailing_zip = row['mailing_zip_postal_code'].strip()
                if not mailing_zip:
                    logger.warning(f"Row {index} skipped: 'mailing_zip_postal_code' is empty.")
                    continue  # Skip rows with empty 'mailing_zip_postal_code'

                record = MailingInfoCreate(
                    mailing_city=row['mailing_city'].strip(),
                    mailing_state_province=row['mailing_state_province'].strip(),
                    mailing_zip_postal_code=mailing_zip,
                    mailing_country=row['mailing_country'].strip(),
                    start_term_year=row['start_term_year'].strip()
                )
                records.append(models.MailingInfo(**record.dict()))
            except Exception as e:
                logger.error(f"Error validating row {index}: {row.to_dict()} - {e}")
                continue  # Skip invalid rows

        if not records:
            logger.warning("No valid records to insert.")
            return {"status": "warning", "detail": "No valid records found in the CSV."}

        # Batch insert
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            db.bulk_save_objects(batch)
            db.commit()
            logger.info(f"Inserted batch {i//batch_size +1} with {len(batch)} records.")

        logger.info(f"Successfully inserted {len(records)} records.")
        return {"status": "success", "detail": f"Successfully inserted {len(records)} records."}

    except Exception as e:
        logger.exception("An error occurred while processing the CSV.")
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()

# POST /upload endpoint
@app.post("/upload")
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        logger.error("Invalid file type attempted for upload.")
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    try:
        content = await file.read()
        file_content = content.decode('utf-8')
        background_tasks.add_task(process_csv, file_content, SessionLocal)
        logger.info("CSV upload received and processing started.")
        return {"message": "Upload received and is being processed."}
    except Exception as e:
        logger.exception("An unexpected error occurred while uploading the CSV.")
        raise HTTPException(status_code=500, detail="An error occurred while uploading the file.")

# GET /mailing_info endpoint with pagination
@app.get("/mailing_info", response_model=MailingInfoListResponse)
def get_all_mailing_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve mailing information records with pagination.
    - **skip**: Number of records to skip.
    - **limit**: Maximum number of records to return.
    """
    try:
        total = db.query(models.MailingInfo).count()
        records = db.query(models.MailingInfo).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(records)} mailing_info records (skip={skip}, limit={limit}).")
        return MailingInfoListResponse(total=total, records=records)
    except Exception as e:
        logger.exception("An error occurred while fetching mailing_info records.")
        raise HTTPException(status_code=500, detail="An error occurred while fetching the records.")

# DELETE /mailing_info endpoint to delete all records
@app.delete("/mailing_info", response_model=dict)
def delete_all_mailing_info(db: Session = Depends(get_db)):
    """
    Delete all mailing information records.
    **Warning:** This action is irreversible.
    """
    try:
        deleted_count = db.query(models.MailingInfo).delete()
        db.commit()
        logger.info(f"Deleted {deleted_count} mailing_info records.")
        return {"message": f"Successfully deleted {deleted_count} records."}
    except Exception as e:
        logger.exception("An error occurred while deleting mailing_info records.")
        raise HTTPException(status_code=500, detail="An error occurred while deleting the records.")
