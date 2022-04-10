from datetime import datetime as dt
from datetime import timedelta
import json
import pandas as pd
import base64
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

db = pd.read_pickle("db.pkl")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/knopka")
async def knopka_post(request: Request):
    time_stamp = dt.now()
    rounded = time_stamp - (time_stamp - dt.min) % timedelta(minutes=30) + timedelta(hours=3)

    body = await request.json()
    body["data"] = json.loads(base64.b64decode(body["data"]).decode('utf8'))
    # print(body, request.headers)

    if body["data"]["telemetry"]["firstButton"]["status"] == "click":
        room_name = "0"
        date = time_stamp.strftime("%Y-%m-%d")
        time_id = rounded.strftime("%H:%M")

        print(room_name, date, time_id)
        contains_room_name = db["room_name"].str.contains(room_name)
        contains_date = db["date"].str.contains(date)
        contains_time_id = db["time_id"].str.contains(time_id)

        if not (contains_room_name.any() and \
                contains_date.any() and \
                contains_time_id.any()):
            return

        print(db)
        db.loc[contains_room_name & contains_date & contains_time_id, "user"] = None
        print(db)

@app.post("/book")
async def book_post(request: Request):
    body = await request.json()
    print(type(body), body)

    contains_room_name = db["room_name"].str.contains(body["room_name"])
    contains_date = db["date"].str.contains(body["date"])
    contains_time_id = db["time_id"].str.contains(body["time_id"])

    if not (contains_room_name.any() and \
            contains_date.any() and \
            contains_time_id.any()):

        return { "success": False, "error_msg": "Incorrect data entry" }

    # print(db)
    db.loc[contains_room_name & contains_date & contains_time_id, "user"] = body["user"]
    # print((contains_room_name & contains_date & contains_time_id).any())
    # print(db)
    return { "success": True, "error_msg": "Successfully booked the room" }

@app.post("/unbook")
async def unbook_post(request: Request):
    body = await request.json()
    print(type(body), body)

    contains_room_name = db["room_name"].str.contains(body["room_name"])
    contains_date = db["date"].str.contains(body["date"])
    contains_time_id = db["time_id"].str.contains(body["time_id"])

    if not (contains_room_name.any() and \
            contains_date.any() and \
            contains_time_id.any()):

        return { "success": False, "error_msg": "Incorrect data entry" }

    db.loc[contains_room_name & contains_date & contains_time_id, "user"] = None
    # print((contains_room_name & contains_date & contains_time_id).any())
    return { "success": True, "error_msg": "Successfully unbooked the room" }

@app.on_event("shutdown")
async def shutdown_event():
    db.to_pickle("db.pkl")
