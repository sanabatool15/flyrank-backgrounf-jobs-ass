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

    result = await ctx.step.run("build-report", build_report)

    if report_id in reports:
        reports[report_id]["status"] = "done"
        reports[report_id]["result"] = result

    return "done"
