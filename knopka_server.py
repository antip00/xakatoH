import json
import base64
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

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
