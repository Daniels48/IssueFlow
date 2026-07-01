from fastapi import FastAPI

from app.router import api_router

app = FastAPI(title="IssueFlow")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(api_router)