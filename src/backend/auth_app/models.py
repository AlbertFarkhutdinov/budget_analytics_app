from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserConfirm(BaseModel):
    username: str
    confirmation_code: str = ''
