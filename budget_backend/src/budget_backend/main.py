from datetime import datetime, timezone
import os
import base64
import boto3
import jwt
import hashlib
import hmac
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


class Config:
    DB_USER = os.getenv('DB_USER', 'user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_HOST = os.getenv('DB_HOST', 'rds-instance.amazonaws.com')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'budget_db')
    COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
    COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
    COGNITO_CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET')
    COGNITO_REGION = os.getenv('COGNITO_REGION')
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}'


class Database:
    engine = sql.create_engine(f'{Config.DATABASE_URL}/{Config.DB_NAME}')
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base = declarative_base()

    @staticmethod
    def create_database():
        temp_engine = sql.create_engine(f'{Config.DATABASE_URL}/postgres')
        with temp_engine.connect() as conn:
            conn.execute(sql.text('COMMIT'))
            result = conn.execute(
                sql.text(
                    "SELECT 1 FROM pg_database WHERE datname='{0}'".format(
                        Config.DB_NAME
                    )
                )
            )
            if not result.fetchone():
                conn.execute(sql.text(f'CREATE DATABASE {Config.DB_NAME}'))
        temp_engine.dispose()


Database.create_database()
Database.Base.metadata.create_all(bind=Database.engine)


class CognitoAuth:
    auth_scheme = HTTPBearer()
    cognito_client = boto3.client(
        'cognito-idp',
        region_name=Config.COGNITO_REGION,
    )

    @staticmethod
    def compute_secret_hash(username: str) -> str:
        message = (username + Config.COGNITO_CLIENT_ID).encode('utf-8')
        secret = Config.COGNITO_CLIENT_SECRET.encode('utf-8')
        dig = hmac.new(
            key=secret,
            msg=message,
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(dig).decode('utf-8')

    @staticmethod
    def verify_token(
        credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
    ):
        try:
            token = credentials.credentials
            decoded_token = jwt.decode(
                token,
                options={'verify_signature': False},
            )
            return decoded_token['cognito:username']
        except Exception:
            raise HTTPException(
                status_code=401,
                detail='Invalid or expired token',
            )


class BudgetEntry(Database.Base):
    __tablename__ = 'budget_entries'
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    date = sql.Column(sql.DateTime, default=datetime.now(timezone.utc))
    shop = sql.Column(sql.String, index=True)
    product = sql.Column(sql.String)
    amount = sql.Column(sql.Float)
    category = sql.Column(sql.String)
    person = sql.Column(sql.String)
    currency = sql.Column(sql.String)


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
        from_attributes = True


class BudgetService:

    @staticmethod
    def create_entry(db: Session, entry: BudgetEntrySchema) -> BudgetEntry:
        db_entry = BudgetEntry(**entry.model_dump())
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry

    @staticmethod
    def get_entries(db: Session) -> list[BudgetEntry]:
        return db.query(BudgetEntry).all()

    @staticmethod
    def update_entry(
        db: Session,
        entry_id: int,
        updated_entry: BudgetEntrySchema,
    ) -> BudgetEntry:
        entry = db.query(BudgetEntry).filter(
            BudgetEntry.id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail='Entry not found')
        for key, value in updated_entry.model_dump().items():
            setattr(entry, key, value)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def delete_entry(db: Session, entry_id: int):
        entry = db.query(BudgetEntry).filter(
            BudgetEntry.id == entry_id).first()
        if entry:
            db.delete(entry)
            db.commit()
        return {'message': 'Entry deleted'}


app = FastAPI()


def get_db():
    db = Database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AuthRequest(BaseModel):
    username: str
    password: str


@app.post('/auth/register')
def register_user(auth_request: AuthRequest):
    try:
        _ = CognitoAuth.cognito_client.sign_up(
            ClientId=Config.COGNITO_CLIENT_ID,
            SecretHash=CognitoAuth.compute_secret_hash(auth_request.username),
            Username=auth_request.username,
            Password=auth_request.password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': auth_request.username,
                }
            ]
        )
        return {'message': 'User registered, confirm the email in AWS Cognito'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/auth/login')
def login_user(auth_request: AuthRequest):
    try:
        response = CognitoAuth.cognito_client.initiate_auth(
            ClientId=Config.COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': auth_request.username,
                'PASSWORD': auth_request.password,
            }
        )
        return {'access_token': response['AuthenticationResult']['IdToken']}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(path='/entries/', response_model=list[BudgetEntrySchema])
def read_entries(
    db: Session = Depends(get_db),
    username: str = Depends(CognitoAuth.verify_token),
):
    return BudgetService.get_entries(db)


@app.post(path='/entries/')
def create_entry(
    entry: BudgetEntrySchema,
    db: Session = Depends(get_db),
    username: str = Depends(CognitoAuth.verify_token),
):
    return BudgetService.create_entry(db, entry)


@app.put(path='/entries/{entry_id}', response_model=BudgetEntrySchema)
def update_entry(
    entry_id: int,
    updated_entry: BudgetEntrySchema,
    db: Session = Depends(get_db),
    username: str = Depends(CognitoAuth.verify_token),
):
    return BudgetService.update_entry(db, entry_id, updated_entry)


@app.delete(path='/entries/{entry_id}')
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(CognitoAuth.verify_token),
):
    return BudgetService.delete_entry(db, entry_id)
