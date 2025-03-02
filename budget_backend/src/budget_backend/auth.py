import os

import base64
import hashlib
import hmac
import logging

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class Settings:
    COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
    COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
    COGNITO_REGION = os.getenv('COGNITO_REGION')
    COGNITO_CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET')
    

app = FastAPI()
cognito_client = boto3.client(
    'cognito-idp',
    region_name=Settings.COGNITO_REGION,
)


def compute_secret_hash(username: str) -> str:
    if not Settings.COGNITO_CLIENT_SECRET:
        raise ValueError('COGNITO_CLIENT_SECRET is missing')
    message = (username + str(Settings.COGNITO_CLIENT_ID)).encode('utf-8')
    secret = Settings.COGNITO_CLIENT_SECRET.encode('utf-8')
    dig = hmac.new(
        key=secret,
        msg=message,
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(dig).decode('utf-8')


class User(BaseModel):
    username: str
    password: str


@app.post('/auth/register')
def register(user: User):
    logger.info(f'Received register request for {user.username}')
    try:
        response = cognito_client.sign_up(
            ClientId=Settings.COGNITO_CLIENT_ID,
            SecretHash=compute_secret_hash(user.username),
            Username=user.username,
            Password=user.password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': user.username,
                },
            ]
        )
        logger.info(f'Cognito `sign_up` response: {response}')
        return {'message': 'User registered, confirm the email.'}
    except cognito_client.exceptions.UsernameExistsException:
        raise HTTPException(status_code=400, detail='User already exists')
    except Exception as exc:
        logger.error(f'Registration failed: {exc}')
        raise HTTPException(
            status_code=500,
            detail={'error': str(exc)},
        )


@app.post('/auth/confirm')
def confirm(user: User, confirmation_code: str):
    logger.info(f'Received confirm request for {user.username}')
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=Settings.COGNITO_CLIENT_ID,
            Username=user.username,
            ConfirmationCode=confirmation_code,
        )
        logger.info(f'Cognito `confirm_sign_up` response: {response}')
        return {'message': 'User confirmed'}
    except cognito_client.exceptions.CodeMismatchException:
        raise HTTPException(
            status_code=400,
            detail='Invalid confirmation code',
        )
    except Exception as exc:
        logger.error(f'Confirmation failed: {exc}')
        raise HTTPException(
            status_code=500,
            detail={'error': str(exc)},
        )


@app.post('/auth/login')
def login(user: User):
    logger.info(f'Received login request for {user.username}')
    try:
        response = cognito_client.initiate_auth(
            ClientId=Settings.COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': user.username,
                'PASSWORD': user.password,
                'SECRET_HASH': compute_secret_hash(user.username),
            }
        )
        logger.info(f'Cognito `initiate_auth` response: {response}')
        return {
            'access_token': response['AuthenticationResult']['AccessToken'],
        }
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(
            status_code=400,
            detail={'error': 'User not found'},
        )
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(
            status_code=401,
            detail={'error': 'Incorrect username or password'},
        )
    except Exception as exc:
        logger.error(f'Login failed: {exc}')
        raise HTTPException(
            status_code=500,
            detail={'error': str(exc)},
        )
