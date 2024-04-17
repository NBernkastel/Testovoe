from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient

from auth import auth_user, hash_password, verify_password, generate_token
from congif import USERNAME, HOST, PORT, AUTH_SOURCE, PASSWORD
from scheme import FormBody, User, Token

uri = f"mongodb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{AUTH_SOURCE}"

client = MongoClient(uri)
db = client['database']
forms_collection = db['forms']
user_collection = db['user']
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post('/token')
def login(user: Annotated[OAuth2PasswordRequestForm, Depends()]):
    db_user = user_collection.find_one({"username": user.username})
    if db_user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if verify_password(db_user["password"].encode(), user.password):
        return Token(access_token=generate_token(db_user["username"]), token_type="bearer")
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@app.post('/reg')
async def register(user: User):
    if user_collection.find_one(user.username) is None:
        user.password = hash_password(user.password)
        user_collection.insert_one(user.dict())


@app.post('/form/add')
def form_add(form: FormBody, token: Annotated[str, Depends(oauth2_scheme)]):
    form = form.dict()
    form["user"] = auth_user(token)
    forms_collection.insert_one(form)
    return True


@app.get('/form/get')
def form_add(token: Annotated[str, Depends(oauth2_scheme)]):
    username = auth_user(token)
    forms = forms_collection.find({"user": username})
    res = []
    for form in forms:
        del form["_id"]
        res.append(form)
    return res
