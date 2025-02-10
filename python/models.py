# models.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MailingInfo(Base):
    __tablename__ = 'mailing_info'

    id = Column(Integer, primary_key=True, index=True)
    mailing_city = Column(String)
    mailing_state_province = Column(String)
    mailing_zip_postal_code = Column(String)
    mailing_country = Column(String)
    start_term_year = Column(String)
