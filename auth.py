from datetime import datetime, timedelta
import bcrypt
import jwt
from fastapi import HTTPException
from jwt import encode, decode

from congif import SECRET_KEY


def auth_user(token: str):
    try:
        username = verify_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="wrong token")
    return username


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')


def verify_password(hashed_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)


def generate_token(username: str, del_time: int = 30) -> str:
    if not isinstance(username, str):
        raise ValueError("username should be string")
    expiration = datetime.utcnow() + timedelta(hours=del_time)
    payload = {
        'username': username,
        'exp': expiration
    }
    token: str = encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token: str) -> jwt.PyJWTError or str:
    try:
        payload = decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload['exp'] < datetime.utcnow().timestamp():
            raise jwt.ExpiredSignatureError("token expired")

    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        raise jwt.PyJWTError

    return payload['username']
