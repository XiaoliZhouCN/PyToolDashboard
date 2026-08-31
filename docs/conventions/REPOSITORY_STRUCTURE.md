# Repository Structure Convention

## 1. 一级目录规范

| 目录 | 职责 |
| --- | --- |
| `dashboard/` | 工具总览、工具发现、预览、启动与状态展示 |
| `tools/` | 独立工具集合，每个目录对应一个 tool |
| `packages/` | 共享契约、共享运行时、共享基础模块 |
| `docs/` | 架构文档、协议文档、规范文档、设计记录 |
| `launchers/` | 面向工作区项目的 `sh` / `bat` 启动包装脚本 |
| `scripts/` | 仓库级开发脚本、初始化脚本、校验脚本 |
| `tests/` | 集成测试、契约测试、端到端测试 |
| `examples/` | 示例输入、示例输出、协议样例 |

## 2. dashboard 目录建议

```text
dashboard/
├── README.md
├── pyproject.toml
├── src/ptd_dashboard/
│   ├── app/         # 桌面程序入口
│   ├── registry/    # 工具清单读取与注册
│   ├── launcher/    # tool 启动与 action 调用
│   ├── preview/     # 预览数据适配与展示
│   ├── views/       # UI 视图层
│   └── services/    # 配置、缓存、日志、历史记录
└── tests/
```

## 3. tool 目录建议

每个 tool 必须是一个自包含单元，建议结构如下：

```text
tools/<tool_id>/
├── README.md
├── architecture_design/
│   └── ARCHITECTURE_DESIGN.md
├── pyproject.toml
├── tool.json
├── src/ptd_tool_<tool_id>/
│   ├── app/         # tool 主入口与 CLI
│   ├── actions/     # dashboard 可调用的标准动作
│   ├── preview/     # 预览数据生成
│   ├── domain/      # 核心业务逻辑
│   ├── infra/       # 文件系统、外部进程、第三方适配器
│   └── schemas/     # tool 自有 schema
├── tests/
└── samples/
```

说明：

- `app/` 是入口层，不堆放核心业务。
- `domain/` 不直接依赖 UI。
- `actions/` 暴露给 dashboard 的能力必须细粒度、可文档化、可测试。
- `samples/` 只放可公开示例，不放真实业务数据。
- `architecture_design/ARCHITECTURE_DESIGN.md` 用于记录复杂 tool 的架构决策；简单 tool 可暂不提供，但推荐预留该位置。

## 4. packages 目录建议

```text
packages/
├── README.md
├── ptd_contracts/   # schema、枚举、协议模型
├── ptd_runtime/     # 进程调度、路径、日志、错误定义
└── ptd_storage/     # JSON/CSV 读写、schema 校验、迁移
```

## 5. 目录命名规范

- 根目录和 tool id 使用 `snake_case`
- Python 包名使用 `ptd_*`
- 不使用空格、不使用中文目录名
- 避免 `misc`、`common`、`temp` 这类含义不清的目录名

## 6. Agent 沟通目录建议

推荐在架构目录下固定保留：

```text
docs/architecture/
├── AGENTMANAGER_TO_AGENT.md
└── agent_to_agent/
    └── README.md
```

说明：

- `AGENTMANAGER_TO_AGENT.md` 是 Agent 开工前的入口文档
- `agent_to_agent/` 用于存放 Agent 间沟通、目录归属和交接说明
- 仓库级稳定规则不应长期停留在 `agent_to_agent/`，应上收至正式规范

## 7. launchers 目录建议

```text
launchers/
├── README.md
└── templates/
    ├── dashboard.bat.example
    └── dashboard.sh.example
```

说明：

- `launchers/` 仅放面向最终运行的包装脚本，不放仓库维护脚本。
- `scripts/` 与 `launchers/` 职责必须分离，前者偏开发维护，后者偏运行入口。
- 所有 launcher 都必须显式处理“主体项目目录”作为运行时工作目录。

## 8. 目录演进规则

- 新建 tool 时，优先复制“标准骨架”，不要自由发挥目录结构。
- 同类职责目录应在所有 tool 中保持一致。
- 若某 tool 需要特殊目录，应在其 `README.md` 中显式说明原因。
