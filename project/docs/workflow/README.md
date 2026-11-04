# 工作流程

这套流程让产品设计、研发实现和上线交付有明确的衔接，任务换人或换聊天后也能继续。

## 关键入口

- [完整流程](workflow.md)：阶段、输入输出和完成条件。
- [UI对齐检查](../../.agents/skills/verify-ui/SKILL.md)：第5步内对照设计与实现，修复后再请用户验收。
- [装配示例](example.md)：一个需求怎样拆解。
- [模板目录](templates/README.md)：任务、PRD、测试与交付记录。
- [澄清与通知](notifications.md)、[项目配置示例](project-settings.example.json)、[文件维护](file-lifecycle.md)。
- [采用说明](adoption.md)：怎样融入已有项目。

## 怎么用

新需求从目标、案例和设计开始；已有任务从当前阶段继续。测试环境开发修复并验证通过后，飞书私聊用户验收；用户确认该版本才发布staging。发布验证、底稿同步与记录完成后，最后分别通知用户和默认群。

执行入口是 [project-workflow Skill](../../.agents/skills/project-workflow/SKILL.md)。

Bug清单修复先看[使用流程](../../../README.md#bug清单修复)，执行细节见 [buglist-fix](../../.agents/skills/buglist-fix/SKILL.md)；[漏斗约定](../../.agents/skills/buglist-fix/references/funnel.md)说明归因和统计口径，[绑定示例](bug-funnel.example.json)采用时填写，不含真实飞书目标。
