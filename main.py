from fastapi import FastAPI
import inngest.fast_api

from inngest_functions import inngest_client, say_hello

app = FastAPI(title="background report job")

inngest.fast_api.serve(app, inngest_client, [say_hello])


@app.get("/health")
def health():
    return {"status": "ok"}
