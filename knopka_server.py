from datetime import datetime as dt
from datetime import timedelta
import json
import pandas as pd
import base64
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

db = pd.read_pickle("db.pkl")
notifications = dict()

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
async def book_post(request: Request):
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
async def unbook_post(request: Request):
    body = await request.json()
    # print(type(body), body)

    possible, index = check_index(body["room_name"], body["date"], body["time_id"])

    if not possible:
        return { "success": False, "error_msg": "Incorrect data entry" }

    db.loc[index, "user"] = None
    # print((contains_room_name & contains_date & contains_time_id).any())
    return { "success": True, "error_msg": "Successfully unbooked the room" }

@app.post("/notify")
async def notify_post(request: Request):
    name = (await request.json())["user"]

    if not name in notifications:
        return {"notification": None}
    
    ret = {"notification": notifications[name]}
    del notifications[name]

    return ret

@app.post("/json")
async def json_post(request: Request):
    slc = db[["room_name", "time_id", "user"]]

    # https://stackoverflow.com/questions/55004985/convert-pandas-dataframe-to-json-with-columns-as-key
    cols = slc.columns.difference(['time_id'])
    return (slc.groupby('time_id')[cols]
            .apply(lambda x: x.to_dict('records'))
            .reset_index(name='data')
            .to_json(orient='records'))

@app.on_event("shutdown")
async def shutdown_event():
    db.to_pickle("db.pkl")

