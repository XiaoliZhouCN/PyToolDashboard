---
alwaysApply: true
scene: git_message
---

本仓库的 git commit message 必须遵循以下格式：

`[XX][XX] change summary[EN]: details[EN]`

字段含义：

1. 第一个 `[XX]`：具体模块名，取值为 `dashboard` 或具体工具名，例如 `mermaid_editor`
2. 第二个 `[XX]`：具体改动部位，优先使用模块内一级子目录名，例如 `app`、`actions`、`preview`、`domain`、`infra`、`docs`
3. `change summary[EN]`：英文短摘要，尽量使用 1 个短语，不超过 5 个英文单词
4. `details[EN]`：英文详细说明，1 句话为宜，不超过 20 个英文单词

生成要求：

- 全部使用英文书写 `change summary` 和 `details`
- 冒号使用英文冒号 `:`
- 摘要应聚焦“改了什么”，避免空泛表述
- 详细说明应补充范围或目的，不要重复摘要
- 若改动只涉及文档或规范，也必须按相同格式生成
- 若同时涉及多个模块，优先选择本次提交影响最大的模块；不要在一次提交标题中列多个模块
- 若第二段无法准确归属到代码子目录，可使用 `root`、`docs`、`config`、`tests`

推荐示例：

- `[dashboard][registry] add tool discovery: register manifest files for local tools`
- `[mermaid_editor][app] refine startup flow: initialize the editor window from manifest settings`
- `[dashboard][docs] update architecture notes: clarify the tool runtime contract`

避免：

- 过长摘要，例如超过 5 个英文单词
- details 写成多句长段落
- 使用中文摘要或中文 details
- 使用含义模糊的 summary，如 `update code`、`fix issues`
