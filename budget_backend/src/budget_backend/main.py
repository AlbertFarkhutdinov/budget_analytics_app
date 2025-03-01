from datetime import datetime, timezone
import os

import boto3
import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()  # Load environment variables from .env

# Database settings
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_ENDPOINT = os.getenv('DB_ENDPOINT', 'rds-instance.amazonaws.com')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'budget_db')

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ENDPOINT}:{DB_PORT}'


# Ensure the database exists
def create_database():
    temp_engine = sql.create_engine(f'{DATABASE_URL}/postgres')
    with temp_engine.connect() as conn:
        conn.execute(sql.text("COMMIT"))
        result = conn.execute(
            sql.text(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
        )
        if not result.fetchone():
            conn.execute(sql.text(f'CREATE DATABASE {DB_NAME}'))
    temp_engine.dispose()


create_database()  # Ensure DB exists before connecting

engine = sql.create_engine(f'{DATABASE_URL}/{DB_NAME}')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# AWS Cognito settings
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
COGNITO_REGION = os.getenv('COGNITO_REGION')
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

auth_scheme = HTTPBearer()


class BudgetEntrySchema(BaseModel):
    id: int
    date: datetime
    shop: str
    product: str
    amount: float
    category: str
    person: str
    currency: str

    class Config:
        from_attributes = True  # Ensures compatibility with SQLAlchemy models


# Define the Budget model
class BudgetEntry(Base):
    __tablename__ = 'budget_entries'

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    shop = sql.Column(sql.String, index=True)
    product = sql.Column(sql.String)
    amount = sql.Column(sql.Float)
    category = sql.Column(sql.String)
    person = sql.Column(sql.String)
    currency = sql.Column(sql.String)


# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Authentication Models
class AuthRequest(BaseModel):
    username: str
    password: str


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
):
    try:
        token = credentials.credentials
        decoded_token = jwt.decode(token, options={'verify_signature': False})
        return decoded_token['cognito:username']
    except Exception as _:
        raise HTTPException(status_code=401, detail='Invalid or expired token')


# Authentication Endpoints
@app.post('/auth/register')
def register_user(auth_request: AuthRequest):
    try:
        response = cognito_client.sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=auth_request.username,
            Password=auth_request.password,
            UserAttributes=[{'Name': 'email', 'Value': auth_request.username}]
        )
        return {'message': 'User registered, confirm the email in AWS Cognito'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/auth/login')
def login_user(auth_request: AuthRequest):
    try:
        response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': auth_request.username,
                            'PASSWORD': auth_request.password}
        )
        return {'access_token': response['AuthenticationResult']['IdToken']}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/auth/verify')
def verify_user(token: str):
    try:
        decoded_token = jwt.decode(token, options={'verify_signature': False})
        return {'username': decoded_token['cognito:username']}
    except Exception as _:
        raise HTTPException(status_code=400, detail='Invalid token')


# Protected Budget Endpoints
@app.post('/entries/')
def create_entry(
    entry: BudgetEntrySchema,  # Accept Pydantic model for validation
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    db_entry = BudgetEntry(**entry.dict())  # Convert to SQLAlchemy model
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry  # SQLAlchemy model auto-converts to Pydantic


@app.get(path='/entries/', response_model=list[BudgetEntrySchema])
def read_entries(
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    entries = db.query(BudgetEntry).all()
    return entries  # Automatically converted to Pydantic model


@app.put('/entries/{entry_id}', response_model=BudgetEntrySchema)
def update_entry(
    entry_id: int,
    updated_entry: BudgetEntrySchema,  # Accept Pydantic model
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    entry = db.query(BudgetEntry).filter(BudgetEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    update_data = updated_entry.model_dump()  # Use `model_dump()` instead of `.dict()`

    for key, value in update_data.items():
        setattr(entry, key, value)

    db.commit()
    db.refresh(entry)
    return entry  # SQLAlchemy model will be converted to Pydantic automatically


@app.delete('/entries/{entry_id}')
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    entry = db.query(BudgetEntry).filter(BudgetEntry.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()
    return {'message': 'Entry deleted'}
