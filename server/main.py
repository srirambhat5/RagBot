from fastapi import FastAPI

app = FastAPI(title="RagBot2.0")


@app.get("/test")
async def test():
    return {"message": "Testing successful..."}