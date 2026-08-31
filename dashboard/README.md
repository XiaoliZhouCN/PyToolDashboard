# Dashboard

`dashboard` 是 `PyToolDashboard` 的平台宿主，负责为本地 tool 提供统一入口。

## Product Positioning

- 本地优先的桌面宿主程序
- 面向主体项目目录 `project_root` 的工具总览入口
- 通过 manifest 与运行协议调度 tool，而不是直接耦合 tool 内部实现

## Core Modules

当前目标结构如下：

```text
dashboard/
├── architecture_design/
│   └── ARCHITECTURE_DESIGN.md
├── pyproject.toml
├── src/ptd_dashboard/
│   ├── app/
│   ├── launcher/
│   ├── preview/
│   ├── registry/
│   ├── services/
│   └── views/
└── tests/
```

当前第一版已落地的模块：

- `app/`：CLI 入口与宿主启动入口
- `launcher/`：tool entrypoint 调用与子进程编排
- `preview/`：tool preview 响应到 dashboard 模型的最小适配
- `registry/`：扫描 `tools/*/tool.json`
- `services/`：运行时上下文与目录语义

## Tool Discovery

`dashboard` 通过仓库根目录下的 `tools/<tool_id>/tool.json` 发现工具。

第一版已支持：

- 扫描 tool manifest
- 校验 manifest 必需字段
- 输出标准化的工具摘要

## Dispatch Flow

目标调度流程如下：

1. `dashboard` 读取 `tool.json`
2. 根据能力声明决定展示入口或预览入口
3. 后续通过标准 CLI / JSON 协议调用 `launch`、`preview`、`action`
4. 聚合状态、日志与结果后交给宿主 UI 展示

当前第一版实现到第 1 步，已建立可扩展的 registry 骨架。
当前第二版已经补齐开发期调度入口，可从 CLI 直接发起 `preview` 和 `action` 调用。

## Preview Strategy

后续 `preview/` 层会负责：

- 请求 tool preview 响应
- 将不同 tool 的原始 payload 适配为统一展示模型
- 提供空状态、失败态和降级展示

当前该层仅保留包结构，尚未落具体实现。

## Config And Cache Directories

仓库级硬约束：

- `dashboard` 的运行时工作目录默认必须是主体项目目录 `project_root`
- 配置、缓存、日志和历史记录应相对 `project_root` 组织
- 不应默认写入 `PyToolDashboard/` 仓库根目录

## Current Entrypoints

当前可用入口：

```powershell
..\launchers\dashboard.bat .
..\launchers\dashboard.bat . list-tools
..\launchers\dashboard.bat . show-tool mermaid_editor
..\launchers\dashboard.bat . preview-tool mermaid_editor --markdown-file tools/mermaid_editor/samples/sample_workflow.md
python "dashboard/src/ptd_dashboard/app/main.py" --project-root .
python -m ptd_dashboard list-tools --project-root .
python -m ptd_dashboard show-tool mermaid_editor --project-root .
python -m ptd_dashboard preview-tool mermaid_editor --project-root . --markdown-file tools/mermaid_editor/samples/sample_workflow.md
python -m ptd_dashboard run-tool-action mermaid_editor --project-root . --action-name export_svg --markdown-file tools/mermaid_editor/samples/sample_workflow.md
```

说明：

- 若未显式传子命令，默认进入 `host`
- 当前 `host` 先输出 JSON 宿主摘要，作为后续桌面 UI 的占位入口
- `--repo-root` 主要用于测试与开发，不是正常 launcher 的必要参数
- 正式 launcher 已位于 `launchers/dashboard.bat` 与 `launchers/dashboard.sh`
- `preview-tool` 默认输出 dashboard 适配后的 preview 模型；加 `--raw` 可查看原始 tool 响应
- `run-tool-action` 当前直接输出 tool action 的原始 JSON 响应
