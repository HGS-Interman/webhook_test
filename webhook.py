import os
import json
import uvicorn
from fastapi import FastAPI, Query, Body, Header, Request
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import hmac
import subprocess

# FastAPI app
app = FastAPI()
SECRET = 'secret'


# --------- github webhook -------------
@app.post('/github/event')
async def webhook_handler(request: Request):
    # verify webhook signature
    raw = await request.body()
    signature = request.headers.get("X-Hub-Signature")

    digest = hmac.new(
        key=SECRET.encode("utf-8"), msg=raw, digestmod="sha1"
    ).hexdigest()
    calc_signature = f"sha1={digest}"

    if signature != calc_signature:
        return JSONResponse(status_code=401, content="Unauthorized")

    # handle events
    # payload = await request.json()
    event_type = request.headers.get("X-Github-Event")
    if event_type == 'push':
        shell_file = os.path.abspath(os.path.join(os.path.dirname(__file__),'gitpull.sh'))
        subprocess.run(shell_file)

    return JSONResponse(status_code=200, content="OK")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)