from pydantic import BaseModel
from typing import Optional
from decouple import config

CSRF_KEY = config('CSRF_KEY')

class CsrfSettings(BaseModel):
    secret_key: str = CSRF_KEY

class TradeInformation(BaseModel) :
    id: str
    trade: str
    book: str
    product: str


class TradeInformationBody(BaseModel) :
    trade: str
    book: str
    product: str


class SuccessMsg(BaseModel) :
    message: str

class UserInfo(BaseModel):
    id: Optional[str] = None
    email: str

class UserBody(BaseModel) :
    email: str
    password: str


class Csrf(BaseModel):
    csrf_token: str