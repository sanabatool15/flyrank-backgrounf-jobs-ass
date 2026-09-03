from fastapi import FastAPI
import inngest.fast_api

from inngest_functions import inngest_client, say_hello

app = FastAPI(title="background report job")

inngest.fast_api.serve(app, inngest_client, [say_hello])

Reports={}




@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/reports/{report_id}")
def get_report(report_id:int):
    if report_id in Reports:
      inngest_client.send("report/requested", Reports[report_id])
      if Reports[report_id]["status"] == "pending":
        return { "status": 202, "message": "Report is still being generated" }
      elif Reports[report_id]["status"] == "completed":
        return { "status": 200, "message": "Report generation completed!" }
    else:
        return { "status": 404, "message": "Report not found" }


@app.post("/reports")
def reports(topic:str):
   event={ "id":  1, "topic": topic, "status": "pending" }
   inngest_client.send("report/requested", event)
   if event["id"] not in Reports:
        Reports[event["id"]] = event
   return { "status": 202, "message": "Accepted I have the order, work starts soon" }


