from ninja import Schema
from typing import Optional, Dict


class GetCodeRequest(Schema):
    phone_number: str


class SendSmsMsgRequest(Schema):
    phone_number: str
    sms_msg: str


class ResponseSchema(Schema):
    err_code: int
    message: str
    data: Optional[Dict] = None

class GetSmsMsgRequest(Schema):
    phone_number: str
