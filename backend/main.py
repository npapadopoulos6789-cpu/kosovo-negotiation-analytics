from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Kosovo Negotiation Analytics API is running"}