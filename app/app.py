import os

from fastapi import FastAPI

app = FastAPI()


@app.post("/test")
async def test():
    return {"message": "Slt"}


if __name__ == "__main__":
    # Get port from environment variable or default to 8080
    port = int(os.getenv("PORT", 8080))
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
