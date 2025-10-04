import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["POST"],
    allow_headers=["*"],
    expose_headers=["*"],  # expose all headers to the browser in response
)

with open("./q-vercel-latency.json") as f:
    telemetry = json.load(f)

class MetricsRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/api/latency-metrics")
async def latency_metrics(req: MetricsRequest):
    result = {}
    for region in req.regions:
        records = [r for r in telemetry if r.get("region") == region]
        if not records:
            continue
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]
        breaches = 0
        for latency in latencies:
            if latency > req.threshold_ms:
                breaches += 1
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }
    return result
