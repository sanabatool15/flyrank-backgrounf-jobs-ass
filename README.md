# Your first background job

FlyRank Internship · Backend Track · Week 4 · Assignment A7

A small FastAPI app whose slow work (an 8-second report) runs in an Inngest
background job instead of inside the request. The API answers instantly, a
status endpoint reports progress, and a cron job runs on the clock alone.

## How to run it

Two terminals, two commands:

**Terminal 1 — the API**
```
uv sync
uvicorn main:app --reload --port 8000
```

**Terminal 2 — the Inngest Dev Server**
```
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```

Open the dashboard at http://localhost:8288 to watch functions run.

## Endpoints & functions

| Route / Function | Type | What it does |
|---|---|---|
| `GET /health` | endpoint | `{"status": "ok"}` health check |
| `POST /reports` | endpoint | Accepts `{"topic": "..."}`, returns `202` + `id` instantly, sends `report/requested` event |
| `GET /reports/{id}` | endpoint | Returns the report: `pending` → `done` + result. Unknown id → `404` |
| `say-hello` | Inngest function | Triggered by `test/hello`; sleeps 5s, returns a greeting (Stage 1 warm-up) |
| `make-report` | Inngest function | Triggered by `report/requested`; sleeps 8s (`do-the-slow-work`), then runs `build-report`; retries up to 2 times on failure |
| `heartbeat` | Inngest function | Cron-triggered (`* * * * *`, every minute); no endpoint, no event — logs a summary of how many reports are `pending`, `done`, `failed` |

## 202 proof

```
$ curl -i -X POST http://localhost:8000/reports -H "Content-Type: application/json" -d '{"topic":"cats"}'
HTTP/1.1 202 Accepted
{"id":"05f4026f-0658-463a-8d50-363d7749fc33","status":"pending"}

$ curl http://localhost:8000/reports/05f4026f-0658-463a-8d50-363d7749fc33
{"id":"05f4026f-0658-463a-8d50-363d7749fc33","topic":"cats","status":"pending"}

# ~8 seconds later
$ curl http://localhost:8000/reports/05f4026f-0658-463a-8d50-363d7749fc33
{"id":"05f4026f-0658-463a-8d50-363d7749fc33","topic":"cats","status":"done","result":{"topic":"cats","summary":"Report about cats"}}
```

## Stage 3 note — retries vs. validation

A missing `topic` is a client mistake that will never succeed no matter how
many times you retry it, so `POST /reports` rejects it once with `400` and
sends no event. A failed `make-report` run (e.g. `topic: "fail"`) is a
different kind of problem — a temporary failure that might succeed on a
later attempt — so Inngest retries it automatically (`retries=2`, 3 attempts
total) before marking the run Failed.

## Stage 4 note — cron expressions

The `heartbeat` function uses `* * * * *` (every minute) so it's easy to
watch during testing. A real daily version would use `0 8 * * *` — every day
at 08:00. To run it every Sunday at 22:00 instead, the expression would be
`0 22 * * 0` (both built and confirmed on crontab.guru).

## Dashboard screenshot

_Screenshot to be added here: open http://localhost:8288, run through the
checkpoints for Stages 1–4, then save a screenshot showing a completed
`make-report` run with its steps, a failed `make-report` run with its 3
retry attempts, and at least two `heartbeat` cron runs a minute apart —
save it as `docs/dashboard.png` and embed it with
`![dashboard](docs/dashboard.png)`._

## AI vs me

_To be filled in for the bonus stage._
