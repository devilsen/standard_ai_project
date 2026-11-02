# 项目协作入口

这里按“产品独立设计 → 测试环境实现与验证 → 用户确认 → staging发布验证 → 更新底稿 → 私聊与默认群通知”协作。当前提供目录规则和流程模板，尚未包含可启动的业务应用。

## 各模块做什么

| 模块 | 用途 |
|---|---|
| [frontend](frontend/README.md) | 正式用户界面，连接真实后端 |
| [designend](designend/README.md) | 产品增量设计，独立页面，使用模拟数据 |
| [mockend](mockend/README.md) | 查看、修改设计场景和模拟数据 |
| [apiend](apiend/README.md) | 统一维护接口定义、示例与浏览页面 |
| [backend](backend/README.md) | 实现业务规则、数据保存和外部服务对接 |
| [e2e](e2e/README.md) | 验证浏览器操作与完整业务流程 |
| [cases](cases/README.md) | 保存用户案例、预期结果及验证说明 |

## 怎么开始

先读 [工作流程](docs/workflow/README.md)，再打开本次涉及模块的 README。执行任务时，从 [Skill入口](.agents/skills/README.md) 选择当前阶段；启动和测试命令在采用模板后从实际项目配置中登记。

开发提交项目名、PRD、固定设计版本和输入/预期案例；产品提交目标、设计范围、案例和待决定问题，在独立 designend 中用 mock 完成设计。可直接复制[分角色使用示例](../README.md#日常怎么使用)。资料不全时，Agent 会先查已有来源，再逐项澄清关键缺口。

[协作规则](AGENTS.md) · [采用模板](docs/workflow/adoption.md) · [评估Skills](workflow-evaluation/README.md)
