import json
import base64
import pandas as pd

from fastapi import FastAPI
from fastapi import Request
from fastapi import Depends
from fastapi_login import LoginManager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

db = pd.read_pickle("db.pkl")
notifications = dict()

SECRET = 'тигры арр'
manager = LoginManager(SECRET, token_url='/auth/token')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def check_index(room_name, date, time_id):
    contains_room_name = db["room_name"].str.contains(room_name)
    contains_date = db["date"].str.contains(date)
    contains_time_id = db["time_id"].str.contains(time_id)

    return contains_room_name.any() and contains_date.any() and contains_time_id.any(), \
                contains_room_name & contains_date & contains_time_id

# TODO store hash
fake_db = {'evgeny': {'password': '1234'},
           'marina': {'password': '1234'},
           'egor': {'password': '1234'},
           'andrey': {'password': '1234'}}


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
    return {'access_token': access_token, 'token_type': 'Bearer'}


# @app.get('/protected')
# def protected_route(user=Depends(manager)):
#     return {"user": user}


@app.post("/knopka")
async def knopka_post(request: Request):
    time_stamp = dt.now() + timedelta(hours=3)
    rounded = time_stamp - (time_stamp - dt.min) % timedelta(minutes=30)

    body = await request.json()
    body["data"] = json.loads(base64.b64decode(body["data"]).decode('utf8'))
    # print(body, request.headers)

    room_name = "0"
    date = time_stamp.strftime("%Y-%m-%d")
    time_id = rounded.strftime("%H:%M")

    # print(db)
    possible, index = check_index(room_name, date, time_id)

    if not possible:
        return

    # Process buttons
    if body["data"]["telemetry"]["firstButton"]["status"] == "click":
        db.loc[index, "user"] = None
        db.loc[index, "service_col"] = None
        db.loc[index, "service_time"] = None

    elif body["data"]["telemetry"]["firstButton"]["status"] == "long_press":
        notifications[db.loc[index, "user"][0]] = "WARNING! Your room is contested. You are to loose access in 5 minutes"

        db.loc[index, "service_col"] = db.loc[index, "user"]
        db.loc[index, "user"] = "Anon"
        db.loc[index, "service_time"] = pd.to_datetime(time_stamp)

    elif body["data"]["telemetry"]["firstButton"]["status"] == "double_click":
        if (time_stamp - db.loc[index, "service_time"].dt.to_pydatetime()) > timedelta(minutes=5):
            # print(db)
            return

        db.loc[index, "user"] = db.loc[index, "service_col"]
        db.loc[index, "service_col"] = None
        db.loc[index, "service_time"] = None
    # print(db)


@app.post("/book")
async def book_post(request: Request, user=Depends(manager)):
    body = await request.json()
    print(type(body), body)

    possible, index = check_index(body["room_name"], body["date"], body["time_id"])

    if not possible:
        return { "success": False, "error_msg": "Incorrect data entry" }

    # print(db)
    db.loc[index, "user"] = body["user"]
    # print((contains_room_name & contains_date & contains_time_id).any())
    # print(db)
    return { "success": True, "error_msg": "Successfully booked the room" }


@app.post("/unbook")
async def unbook_post(request: Request, user=Depends(manager)):
    body = await request.json()
    # print(type(body), body)

    possible, index = check_index(body["room_name"], body["date"], body["time_id"])

    if not possible:
        return { "success": False, "error_msg": "Incorrect data entry" }

    db.loc[index, "user"] = None
    # print((contains_room_name & contains_date & contains_time_id).any())
    return { "success": True, "error_msg": "Successfully unbooked the room" }


@app.post("/notify")
async def notify_post(request: Request, user=Depends(manager)):
    name = (await request.json())["user"]

    if not name in notifications:
        return {"notification": None}

    ret = {"notification": notifications[name]}
    del notifications[name]

    return ret


@app.post("/json")
async def json_post(request: Request, user=Depends(manager)):
    slc = db[["room_name", "time_id", "user"]]

    # https://stackoverflow.com/questions/55004985/convert-pandas-dataframe-to-json-with-columns-as-key
    cols = slc.columns.difference(['room_name'])
    return (slc.groupby('room_name')[cols]
            .apply(lambda x: x.to_dict('records'))
            .reset_index(name='data')
            .to_json(orient='records'))


@app.on_event("shutdown")
async def shutdown_event():
    db.to_pickle("db.pkl")
