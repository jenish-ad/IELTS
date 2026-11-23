from fastapi import FastAPI

from app.api.routes.assessments import router as assessments_router

app = FastAPI()
app.include_router(assessments_router)


@app.get("/")
def hello():
    return {"message": "IELTS speaking test API is running!"}
