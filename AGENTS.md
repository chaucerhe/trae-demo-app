# AGENTS.md — 待办事项 API 项目规范

本文件是 AI 编码时的项目级规范（演示"项目知识注入 / wiki 跟随分支"机制）。AI 修改本仓库代码时必须遵守。

## 技术栈

- Python 3.9+，FastAPI，pydantic v2，pytest
- 数据仅存内存（模块级列表 `app.main._todos`），不引入数据库

## 代码规范

- 接口统一使用 FastAPI 装饰器，返回 Pydantic 模型（`response_model`）
- 所有接口补全类型注解（type hints）
- 公共函数写一句话 docstring（中文）
- 时间字段统一 ISO 8601 UTC 字符串

## 接口约定

- `GET /healthz`：健康检查，返回 `{"status": "ok"}`，HTTP 200
- 资源路径统一小写复数（如 `/todos`）
- 创建类接口返回 201；删除类接口返回 204；资源不存在返回 404

## 测试规范

- 测试文件位于 `tests/`，使用 `fastapi.testclient.TestClient`
- 每个接口（含新接口）都必须在 `tests/test_api.py` 中补充对应测试
- 提交前必须 `pytest -q` 全绿
