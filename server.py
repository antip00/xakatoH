from fastapi import FastAPI
from fastapi import Depends
from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException


SECRET = 'тигры арр'
manager = LoginManager(SECRET, token_url='/auth/token')


app = FastAPI()

fake_db = {'johndoe@e.mail': {'password': 'hunter2'}}


@manager.user_loader()
def load_user(email: str):
    user = fake_db.get(email)
    return user


@app.post('/auth/token')
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = load_user(email)
    if not user:
        raise InvalidCredentialsException

    elif password != user['password']:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=email)
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get('/protected')
def protected_route(user=Depends(manager)):
    return {"hello": "world"}
