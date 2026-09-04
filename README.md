# 待办事项 API（Todo API）

演示 TRAE 自动化研发流水线的最小示例工程。FastAPI + pytest。

## 技术栈

- Python 3.9+ / FastAPI / uvicorn / pydantic
- pytest + fastapi TestClient

## 启动

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /todos | 列出待办；`?sort=created_at:desc` 按创建时间降序 |
| POST | /todos | 创建待办 `{"title": "...", "done": false}` |
| PATCH | /todos/{id} | 更新待办 |
| DELETE | /todos/{id} | 删除待办 |

## 测试

```bash
pytest -q
```

## 项目规范

见 `AGENTS.md`（AI 编码时需遵循）。
