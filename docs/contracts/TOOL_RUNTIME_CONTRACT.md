# Tool Runtime Contract

## 1. 目标

本协议定义 dashboard 与 tool 之间的最小运行时接口，确保 Python 工具、C++ 可执行程序或其他语言实现都能统一接入。

## 2. 静态发现

每个 tool 根目录必须存在 `tool.json`。

最小建议字段：

```json
{
  "schema_version": "1.0",
  "tool_id": "mermaid_editor",
  "name": "Mermaid Editor",
  "version": "0.1.0",
  "entrypoints": {
    "launch": "python -m ptd_tool_mermaid_editor",
    "preview": "python -m ptd_tool_mermaid_editor preview",
    "action": "python -m ptd_tool_mermaid_editor action"
  },
  "capabilities": [
    "launch_panel",
    "preview",
    "run_action"
  ],
  "launcher_policy": "dashboard_only"
}
```

`launcher_policy` 建议值：

- `dashboard_only`：只能经由 dashboard 唤起
- `standalone_allowed`：允许提供独立 launcher
- `standalone_preferred`：可独立运行，dashboard 也可调度

## 3. 请求结构

```json
{
  "schema_version": "1.0",
  "request_id": "uuid",
  "tool_id": "mermaid_editor",
  "action": "preview",
  "args": {},
  "context": {
    "invoker": "dashboard",
    "workspace": "."
  }
}
```

## 4. 响应结构

```json
{
  "schema_version": "1.0",
  "request_id": "uuid",
  "status": "ok",
  "message": "preview generated",
  "payload": {},
  "artifacts": [],
  "errors": []
}
```

## 5. 退出码建议

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功 |
| `2` | 参数错误 |
| `3` | 输入不存在或不可读 |
| `10` | 业务执行失败 |
| `20` | 内部异常 |

## 6. 最低接入要求

一个 tool 想被 dashboard 正式接入，至少需要满足：

1. 有 `README.md`
2. 有 `tool.json`
3. 有稳定入口命令
4. 能返回标准化错误信息
5. 输入输出格式可文档化

若 tool 允许独立 launcher，还应补充满足：

6. 能显式接收 `project_root`
7. 能在非仓库根目录下稳定运行
