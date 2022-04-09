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
    body = await request.json()
    body["data"] = json.loads(base64.b64decode(body["data"]).decode('utf8'))
    print(body)

@app.get("/app")
async def app_get(request: Request):
    body = await request.json()
    print(body)
    return {"test": "mew"}

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
