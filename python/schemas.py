# schemas.py

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List
import re

class MailingInfoCreate(BaseModel):
    mailing_city: str = Field(..., min_length=1)
    mailing_state_province: str = Field(..., min_length=1)
    mailing_zip_postal_code: str = Field(..., min_length=1)
    mailing_country: str = Field(..., min_length=1)
    start_term_year: str = Field(..., min_length=1)

    @validator('start_term_year')
    def validate_start_term_year(cls, v):
        pattern = re.compile(r'^(Fall|Spring|Summer) \d{4}$')
        if not pattern.match(v):
            raise ValueError("start_term_year must match the pattern 'Fall 2023', 'Spring 2024', etc.")
        return v

class MailingInfoResponse(BaseModel):
    id: int
    mailing_city: str
    mailing_state_province: str
    mailing_zip_postal_code: str
    mailing_country: str
    start_term_year: str

    model_config = ConfigDict(from_attributes=True)

class MailingInfoListResponse(BaseModel):
    total: int
    records: List[MailingInfoResponse]

    model_config = ConfigDict(from_attributes=True)
