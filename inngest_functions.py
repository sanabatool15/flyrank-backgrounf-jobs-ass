import datetime
import logging

import inngest

from store import reports

inngest_client = inngest.Inngest(
    app_id="report-api",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
)


@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    await ctx.step.sleep("wait-a-bit", datetime.timedelta(seconds=5))
    return "Hello from the background!"


@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
)
async def make_report(ctx: inngest.Context) -> str:
    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]

    await ctx.step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    def build_report() -> dict:
        if topic == "fail":
            raise Exception("The report oven is broken!")
        return {"topic": topic, "summary": f"Report about {topic}"}

    try:
        result = await ctx.step.run("build-report", build_report)
    except Exception:
        if report_id in reports:
            reports[report_id]["status"] = "failed"
        raise

    if report_id in reports:
        reports[report_id]["status"] = "done"
        reports[report_id]["result"] = result

    return "done"


@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context) -> str:
    counts = {"pending": 0, "done": 0, "failed": 0}
    for report in reports.values():
        status = report.get("status")
        if status in counts:
            counts[status] += 1

    summary = (
        f"reports: {counts['pending']} pending, "
        f"{counts['done']} done, {counts['failed']} failed"
    )
    ctx.logger.info(summary)
    return summary
