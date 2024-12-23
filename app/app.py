from fastapi import FastAPI

app = FastAPI()


@app.post("/test")
async def test():
    return 'Slt'
