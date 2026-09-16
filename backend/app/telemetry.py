"""App-Insights-compatible telemetry: JSONL exporter.

Schema mirrors Azure Application Insights requests/traces closely enough that
(a) the same KQL dashboard works against production App Insights / ADX, and
(b) swapping to the OpenTelemetry Azure Monitor exporter is a config change.
"""
import json
import os
import time
import uuid


def _span_id() -> str:
    return uuid.uuid4().hex[:16]


def record(name: str, *, operation_id: str = None, success: bool = True,
           duration_ms: int = 0, result_code: int = 200,
           custom: dict = None, path: str = None) -> dict:
    entry = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z",
        "name": name,
        "operation_Id": operation_id or str(uuid.uuid4()),
        "traceId": uuid.uuid4().hex[:32],
        "spanId": _span_id(),
        "success": bool(success),
        "duration_ms": int(duration_ms),
        "resultCode": int(result_code),
        "customDimensions": custom or {},
    }
    os.makedirs(os.path.dirname(path or _default_path()), exist_ok=True)
    with open(path or _default_path(), "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def _default_path():
    from . import config
    return os.path.join(config.TELEMETRY_DIR, "app_insights_compat.jsonl")


def summary(path: str = None) -> dict:
    """Aggregate the local JSONL — same numbers the KQL dashboard produces."""
    path = path or _default_path()
    rows = []
    if os.path.exists(path):
        with open(path) as f:
            rows = [json.loads(line) for line in f if line.strip()]

    def pct(vals, p):
        if not vals:
            return 0
        vals = sorted(vals)
        return vals[min(len(vals) - 1, int(p * len(vals)))]

    by_op = {}
    for r in rows:
        d = by_op.setdefault(r["name"], {"count": 0, "ok": 0, "lat": []})
        d["count"] += 1
        if r["success"]:
            d["ok"] += 1
        d["lat"].append(r["duration_ms"])
    out = {}
    for op, d in by_op.items():
        out[op] = {"count": d["count"], "success_rate": round(d["ok"] / d["count"], 3),
                   "p50_ms": pct(d["lat"], 0.50), "p95_ms": pct(d["lat"], 0.95)}
    return {"total": len(rows), "operations": out}
