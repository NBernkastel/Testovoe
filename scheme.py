from typing import Union

from pydantic import BaseModel


class FormElement(BaseModel):
    question: str
    answer: Union[str, dict[str, bool], bool]


class FormBody(BaseModel):
    form: list[FormElement]


class User(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str