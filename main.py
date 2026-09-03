import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import inngest.fast_api
from inngest_functions import inngest_client, make_report, say_hello
from store import reports

app = FastAPI(title="background report job")

inngest.fast_api.serve(app, inngest_client, [say_hello, make_report])


@app.get("/health")
def health():
    return {"status": "ok"}


class ReportRequest(BaseModel):
    topic: str | None = None


@app.post("/reports", status_code=202)
async def create_report(body: ReportRequest):
    if not body.topic:
        raise HTTPException(status_code=400, detail="topic is required")

    report_id = str(uuid.uuid4())
    reports[report_id] = {"id": report_id, "topic": body.topic, "status": "pending"}

    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={"id": report_id, "topic": body.topic},
        )
    )

    return {"id": report_id, "status": "pending"}


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    report = reports.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="report not found")
    return report
