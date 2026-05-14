from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_input = ""
latest_output = ""


@app.get("/status")
def status():
    return {"input": latest_input, "output": latest_output}


@app.post("/input")
def update_input(data: dict):
    global latest_input
    latest_input = data.get("text", "")
    return {"ok": True}


@app.post("/output")
def update_output(data: dict):
    global latest_output
    latest_output = data.get("text", "")
    return {"ok": True}