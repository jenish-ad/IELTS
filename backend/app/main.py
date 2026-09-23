# print("Hello main.py")
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return {"message": "IELTS speaking test API is running!"}
