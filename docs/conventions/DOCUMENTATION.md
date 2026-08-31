# Documentation Convention

## 1. 文档分层

| 位置 | 内容 |
| --- | --- |
| `README.md` | 仓库级介绍、快速开始、模块导航 |
| `docs/architecture/` | 架构设计、边界、依赖关系 |
| `docs/architecture/AGENTMANAGER_TO_AGENT.md` | Agent 类型分流、必读文件与按需阅读规则 |
| `docs/architecture/agent_to_agent/` | Agent 间架构沟通、交接和职责归属记录 |
| `docs/contracts/` | tool 与 dashboard 的协议 |
| `docs/conventions/` | 规范与约束 |
| `launchers/README.md` | 启动脚本目录说明与使用约定 |
| `tools/<tool_id>/README.md` | 单个 tool 的说明与使用方式 |
| `tools/<tool_id>/architecture_design/ARCHITECTURE_DESIGN.md` | 单个复杂 tool 的架构决策与设计记录 |
| `dashboard/README.md` | dashboard 的职责与模块说明 |

## 2. 每个 tool 的 README 必须包含

1. 工具简介
2. 适用场景
3. 目录结构说明
4. 入口命令或启动方式
5. 输入格式
6. 输出格式
7. 可被 dashboard 调用的 action
8. 示例
9. 当前限制与待办

推荐模板：

```md
# <Tool Name>

## Overview
## Use Cases
## Structure
## Entrypoints
## Inputs
## Outputs
## Dashboard Actions
## Examples
## Limitations
```

## 3. dashboard README 必须包含

1. 产品定位
2. 核心模块说明
3. 工具发现方式
4. 调度流程
5. 预览机制
6. 配置与缓存目录

## 4. 单个 tool 的 ARCHITECTURE_DESIGN.md 规范

对于中大型或复杂 tool，推荐在
[tools/<tool_id>/architecture_design/ARCHITECTURE_DESIGN.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/ARCHITECTURE_DESIGN.md)
中记录架构设计。

该文档不替代 `README.md`，而是补充：

1. 架构备选方案与取舍
2. 最终架构决策
3. 模块分层与依赖边界
4. 数据与持久化设计
5. dashboard 集成与运行目录约束
6. 当前实现状态与后续演进

简单 tool 可暂不单独提供；复杂 tool 应优先补齐。

## 5. 文档写作规则

- 标题层级稳定，不跳级
- 术语统一，优先使用仓库约定名称
- 协议文档必须带版本
- 示例优先给最小可运行样例
- 限制与假设要显式写出
- Agent 间临时协作记录优先放 `docs/architecture/agent_to_agent/`
- 已稳定的协作规则应尽快上收为正式规范，避免长期停留在 issue 记录里

## 6. 文档维护规则

- 结构变化时同步更新对应 README 与 architecture 文档
- 协议变化时同步更新 `docs/contracts/`
- 重要决策应记录在 `docs/architecture/`，避免只留在对话里
