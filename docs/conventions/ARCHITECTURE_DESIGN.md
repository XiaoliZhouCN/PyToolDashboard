# Architecture Design Convention

## 1. 目标

本规范定义单个 tool 的架构设计文档约定，用于记录：

- 工具定位与目标边界
- 关键架构决策与取舍
- 模块划分与依赖关系
- 数据持久化与运行时约束
- 当前实现状态与后续演进方向

该文档的目标不是重复 `README.md`，而是沉淀“为什么这样设计”。

## 2. 文件位置与命名

推荐固定位置：

```text
tools/<tool_id>/
└── architecture_design/
    └── ARCHITECTURE_DESIGN.md
```

规则：

- 目录固定为 `architecture_design/`
- 文件名固定为 `ARCHITECTURE_DESIGN.md`
- 不使用 `architecture.md`、`design_notes.md`、`draft.md` 等多种变体

统一命名的目的，是让人类和 Agent 都能低成本发现该文件。

## 3. 哪些 tool 必须提供

### 3.1 必须提供

以下类型的 tool 必须提供 [ARCHITECTURE_DESIGN.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/ARCHITECTURE_DESIGN.md)：

- 包含明显分层结构的 tool
- 使用 `PySide6 + Web UI`、多进程、插件式扩展、外部可执行程序接入等复杂架构的 tool
- 需要与 dashboard 深度交互的 tool
- 涉及复杂持久化策略、sidecar 文件、schema 兼容或运行目录约束的 tool
- 预期会长期维护和持续扩展的中大型 tool

### 3.2 推荐提供

以下类型推荐提供：

- 当前还不复杂，但未来已明确会持续扩展的 tool
- 有明显技术选型权衡的 tool
- 需要给其他 Agent 或未来维护者快速建立心智模型的 tool

### 3.3 可暂不提供

以下类型可以暂不单独提供，但仍应在 `README.md` 中说明基本结构：

- 单一脚本型小工具
- 无明显架构分层的极简转换工具
- 一次性实验性质工具

## 4. 与 README 的职责分工

### README.md 负责

- 工具是什么
- 怎么安装和运行
- 输入输出是什么
- 用户怎么使用

### ARCHITECTURE_DESIGN.md 负责

- 为什么这样设计
- 为什么选这个技术方向而不是别的方向
- 模块怎么分层
- 数据怎么流转
- 哪些决定是当前刻意保留的约束

简单说：

- `README.md` 偏使用说明
- `ARCHITECTURE_DESIGN.md` 偏架构决策记录

## 5. 必备章节

推荐最少包含以下章节，顺序也建议尽量保持一致：

### 5.1 Tool Goal

- 当前目标
- 核心问题定义
- 非目标范围

### 5.2 Product Positioning

- 本地工具 / 工程工具 / 可视化工具 / 数据处理工具等定位
- 单人使用还是协作场景
- local-first 还是 service-first

### 5.3 Architecture Options

- 至少记录主要备选方案
- 写出选择理由与放弃理由

这个章节非常重要，因为它决定了文档是否真的记录了“设计”，而不只是描述现状。

### 5.4 Final Decision

- 最终架构方案
- 核心技术栈
- 决策理由

### 5.5 Module Layout

需要显式对齐真实目录结构，例如：

```text
src/ptd_tool_<tool_id>/
├── app/
├── domain/
├── infra/
├── preview/
└── schemas/
```

并说明每层职责、允许依赖什么、不应依赖什么。

### 5.6 Data And Persistence

- 输入来源
- 输出产物
- JSON / CSV / sidecar / cache / logs 的位置和职责
- 是否依赖 `project_root`
- 是否有版本迁移问题

### 5.7 Runtime And Integration

- 如何被 dashboard 调用
- 是否支持独立 launcher
- 运行目录规则
- 是否依赖外部可执行程序或 C++ 模块

### 5.8 Constraints And Risks

- 当前明确不做什么
- 已知限制
- 兼容性、性能、可维护性风险

### 5.9 Milestones Or Evolution Plan

- 当前阶段
- 后续演进方向
- 哪些能力已完成、哪些未完成

### 5.10 Status Update

- 当前实现状态
- 与原始设计相比有哪些调整
- 哪些决策已落地、哪些还只是计划

## 6. 推荐增强章节

对于更复杂的 tool，建议增加：

- `Dependency Boundaries`
- `Error Handling Strategy`
- `Preview Strategy`
- `Schema Compatibility`
- `Testing Strategy`
- `Open Questions`

## 7. 写作规范

- 文档应使用稳定标题，不频繁改章节名
- 重点写“为什么”，不是把代码结构逐行翻译一遍
- 架构图、流程图可以有，但文字解释必须足够完整
- 路径描述要与当前仓库真实结构一致
- 避免长期保留过时的硬编码外部路径
- 若引用外部项目目录，要明确它是示例还是运行时约束

## 8. 可维护性要求

为了让该文档对未来维护真正有用，必须满足：

- 目录结构变化时同步更新
- 关键技术选型变化时同步更新
- 运行目录规则变化时同步更新
- `README.md` 与 `ARCHITECTURE_DESIGN.md` 不相互冲突
- 计划中的内容要明确标注，不要写得像已实现事实

## 9. 与 mermaid_editor 的关系

[mermaid_editor 的架构文档](file:///d:/Repositories/PyToolDashboard/tools/mermaid_editor/architecture_design/ARCHITECTURE_DESIGN.md)
提供了一个有价值的起点，尤其适合参考以下内容：

- 目标定义
- 方案对比
- 最终架构决策
- 技术方向
- 里程碑规划
- 实现状态更新

但仓库统一规范应比它更进一步：

- 与当前仓库标准目录对齐
- 明确区分“现状”“计划”“约束”
- 明确记录 `project_root`、launcher、dashboard 集成等仓库级规则
- 避免把过时示例路径长期保留在正文中

## 10. 推荐模板

```md
# <Tool Name> Architecture Design

## 1. Tool Goal
## 2. Product Positioning
## 3. Architecture Options
## 4. Final Decision
## 5. Module Layout
## 6. Data And Persistence
## 7. Runtime And Integration
## 8. Constraints And Risks
## 9. Milestones Or Evolution Plan
## 10. Status Update
```
