# 工作流Skills

这些文件指导 Agent 按当前阶段工作。通常从调度入口开始，只读取当前需要的能力。

| Skill | 用途 |
|---|---|
| [project-workflow](project-workflow/SKILL.md) | 启动、恢复任务并选择阶段 |
| [prepare-design](prepare-design/SKILL.md) | 理解需求、演示设计、接收交接 |
| [define-api](define-api/SKILL.md) | 明确接口和后端边界 |
| [plan-and-implement](plan-and-implement/SKILL.md) | 拆片、设计测试、实现 |
| [verify-delivery](verify-delivery/SKILL.md) | 测试环境验证修复，私聊用户验收并等待确认 |
| [release-staging](release-staging/SKILL.md) | 发布已确认版本到staging并验证 |
| [refresh-design](refresh-design/SKILL.md) | 上线后更新设计底稿 |
| [notify-project](notify-project/SKILL.md) | 测试后私聊请验收；最后通知用户和默认群；及时报告阻塞 |
| [clarify-task](clarify-task/SKILL.md) | 遇到关键不确定性时调用grill-me |
| [evaluate-workflow](evaluate-workflow/SKILL.md) | 测试、评分并改进这套Skills |

宿主支持项目Skills时使用 `$project-workflow`；否则显式读取对应文件。采用方式见[接入说明](../../docs/workflow/adoption.md)，效果验证见[评估入口](../../workflow-evaluation/README.md)。
