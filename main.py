from fastapi import FastAPI

app = FastAPI(title="background report job")


@app.get("/health")
def health():
    return {"status": "ok"}
