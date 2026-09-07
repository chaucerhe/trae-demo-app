"""待办事项 API：演示工程（初始状态，/healthz 将由流水线生成）"""
import json
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Todo API", version="0.1.0")

_todos: List[dict] = []


@app.get("/healthz")
def healthz() -> dict:
    """健康检查接口，返回服务状态。"""
    return {"status": "ok"}


class TodoIn(BaseModel):
    title: str
    done: bool = False


class Todo(TodoIn):
    id: str
    created_at: str


class StatsOut(BaseModel):
    total: int
    done: int
    pending: int
    done_ratio: float


@app.get("/todos", response_model=List[Todo])
def list_todos(sort: Optional[str] = None):
    """列出所有待办。sort=created_at:desc 时按创建时间降序。"""
    items = _todos
    if sort == "created_at:desc":
        items = sorted(_todos, key=lambda t: t["created_at"], reverse=True)
    return items


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(payload: TodoIn):
    todo = {
        "id": str(uuid4()),
        "title": payload.title,
        "done": payload.done,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _todos.append(todo)
    return todo


def _compute_stats() -> StatsOut:
    """统计待办总数、完成数、待办数与完成率。"""
    total = len(_todos)
    done = sum(1 for t in _todos if t["done"])
    pending = total - done
    done_ratio = round(done / total, 2) if total else 0.0
    return StatsOut(total=total, done=done, pending=pending, done_ratio=done_ratio)


@app.get("/todos/stats", response_model=StatsOut)
def todos_stats() -> StatsOut:
    """按完成状态统计待办数量与完成率。"""
    return _compute_stats()


_STATS_PAGE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Todo 完成状态分布</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, "PingFang SC", "Helvetica Neue", sans-serif;
    background: #f5f6fa; color: #1f2430; padding: 48px 16px;
  }
  .card {
    max-width: 640px; margin: 0 auto; background: #fff;
    border-radius: 16px; padding: 32px; box-shadow: 0 4px 24px rgba(0,0,0,.06);
  }
  h1 { font-size: 22px; font-weight: 600; }
  .subtitle { margin-top: 6px; font-size: 13px; color: #8a90a0; }
  .chart-wrap { display: flex; justify-content: center; margin: 28px 0 20px; }
  .legend { display: flex; justify-content: center; gap: 32px; margin-bottom: 24px; }
  .legend-item { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #4a5064; }
  .swatch { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
  .stats {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
    border-top: 1px solid #eef0f5; padding-top: 24px;
  }
  .stat { text-align: center; }
  .stat .num { font-size: 24px; font-weight: 600; }
  .stat .label { margin-top: 4px; font-size: 12px; color: #8a90a0; }
  .empty-text { fill: #9aa0b0; font-size: 14px; }
</style>
</head>
<body>
<div class="card">
  <h1>Todo 完成状态分布</h1>
  <p class="subtitle">GET /todos/stats · 按完成状态统计数量与占比</p>
  <div class="chart-wrap">
    <svg id="pie" width="220" height="220" viewBox="0 0 220 220" role="img"></svg>
  </div>
  <div class="legend" id="legend"></div>
  <div class="stats">
    <div class="stat"><div class="num" id="num-total">-</div><div class="label">total</div></div>
    <div class="stat"><div class="num" id="num-done">-</div><div class="label">done</div></div>
    <div class="stat"><div class="num" id="num-pending">-</div><div class="label">pending</div></div>
    <div class="stat"><div class="num" id="num-ratio">-</div><div class="label">done_ratio</div></div>
  </div>
</div>
<script>
window.__STATS__ = %STATS_JSON%;
(function () {
  var stats = window.__STATS__;
  var COLOR_PENDING = "#2f4bd7";
  var COLOR_DONE = "#1a9e66";
  var COLOR_EMPTY = "#e4e7ee";
  var svgNS = "http://www.w3.org/2000/svg";
  var svg = document.getElementById("pie");
  var cx = 110, cy = 110, r = 80;

  function polarToXY(angle) {
    var rad = (angle - 90) * Math.PI / 180;
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
  }

  function makeSlice(startAngle, endAngle, color) {
    var p1 = polarToXY(startAngle);
    var p2 = polarToXY(endAngle);
    var largeArc = (endAngle - startAngle) > 180 ? 1 : 0;
    var path = document.createElementNS(svgNS, "path");
    path.setAttribute("d",
      "M " + cx + " " + cy +
      " L " + p1[0] + " " + p1[1] +
      " A " + r + " " + r + " 0 " + largeArc + " 1 " + p2[0] + " " + p2[1] + " Z");
    path.setAttribute("fill", color);
    svg.appendChild(path);
  }

  function makeLabel(angle, pct, color) {
    var p = polarToXY(angle);
    var lx = cx + (p[0] - cx) * 0.6;
    var ly = cy + (p[1] - cy) * 0.6;
    var text = document.createElementNS(svgNS, "text");
    text.setAttribute("x", lx);
    text.setAttribute("y", ly);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("dominant-baseline", "middle");
    text.setAttribute("fill", "#fff");
    text.setAttribute("font-size", "13");
    text.textContent = pct + "%";
    svg.appendChild(text);
  }

  var legend = document.getElementById("legend");
  function legendItem(name, color, pct) {
    var item = document.createElement("div");
    item.className = "legend-item";
    var sw = document.createElement("span");
    sw.className = "swatch";
    sw.style.background = color;
    item.appendChild(sw);
    item.appendChild(document.createTextNode(name + " " + pct + "%"));
    legend.appendChild(item);
  }

  var total = stats.total;
  if (total === 0) {
    var ring = document.createElementNS(svgNS, "circle");
    ring.setAttribute("cx", cx);
    ring.setAttribute("cy", cy);
    ring.setAttribute("r", r / 2);
    ring.setAttribute("fill", "none");
    ring.setAttribute("stroke", COLOR_EMPTY);
    ring.setAttribute("stroke-width", r);
    svg.appendChild(ring);
    var emptyText = document.createElementNS(svgNS, "text");
    emptyText.setAttribute("x", cx);
    emptyText.setAttribute("y", cy);
    emptyText.setAttribute("text-anchor", "middle");
    emptyText.setAttribute("dominant-baseline", "middle");
    emptyText.setAttribute("class", "empty-text");
    emptyText.textContent = "暂无数据";
    svg.appendChild(emptyText);
    legendItem("待办 pending", COLOR_PENDING, "0");
    legendItem("已完成 done", COLOR_DONE, "0");
  } else {
    var pendingPct = Math.round(stats.pending / total * 1000) / 10;
    var donePct = Math.round(stats.done / total * 1000) / 10;
    var pendingAngle = stats.pending / total * 360;
    if (stats.pending > 0) {
      makeSlice(0, pendingAngle, COLOR_PENDING);
      if (pendingPct >= 8) { makeLabel(pendingAngle / 2, pendingPct, COLOR_PENDING); }
    }
    if (stats.done > 0) {
      makeSlice(pendingAngle, 360, COLOR_DONE);
      if (donePct >= 8) { makeLabel(pendingAngle + (360 - pendingAngle) / 2, donePct, COLOR_DONE); }
    }
    legendItem("待办 pending", COLOR_PENDING, pendingPct);
    legendItem("已完成 done", COLOR_DONE, donePct);
  }

  document.getElementById("num-total").textContent = stats.total;
  document.getElementById("num-done").textContent = stats.done;
  document.getElementById("num-pending").textContent = stats.pending;
  document.getElementById("num-ratio").textContent = stats.done_ratio.toFixed(2);
})();
</script>
</body>
</html>
"""


@app.get("/todos/stats/view", response_class=HTMLResponse)
def todos_stats_view() -> HTMLResponse:
    """以 HTML 饼图页面展示待办完成状态分布。"""
    stats_json = json.dumps(_compute_stats().model_dump())
    return HTMLResponse(_STATS_PAGE_HTML.replace("%STATS_JSON%", stats_json))


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, payload: TodoIn):
    for t in _todos:
        if t["id"] == todo_id:
            t.update(payload.model_dump())
            return t
    raise HTTPException(status_code=404, detail="todo not found")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str):
    global _todos
    _todos = [t for t in _todos if t["id"] != todo_id]
