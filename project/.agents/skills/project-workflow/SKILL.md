---
name: project-workflow
description: 在采用独立设计交接流程的项目中启动或继续需求，定位当前阶段并按需调用设计、契约、实现、验收及底稿更新能力。
---

# 项目工作流调度

## 首次动作

读仓库根与本任务相关目录的AGENTS.md、已有任务记录、用户最新指令。读 [workflow.md](../../../docs/workflow/workflow.md) 的阶段表，定位实际进度；继续任务时核对已记录产物，不能只凭聊天或状态字段跳阶段。

用简短更新说明：本轮目标、当前阶段、固定依据、下一动作。用户只要求讨论/模板时交付相应材料，不自行建设应用或发布。

## 按缺口选能力

| 当前需要 | 读取并执行 |
|---|---|
| 用户给出Markdown/飞书Bug清单，要求逐项修复 | [buglist-fix](../buglist-fix/SKILL.md) |
| 目标/case/交互不明确，或接收产品设计 | [prepare-design](../prepare-design/SKILL.md) |
| 界面行为明确，需要接口和内部边界 | [define-api](../define-api/SKILL.md) |
| 契约足够，准备拆解/实现 | [plan-and-implement](../plan-and-implement/SKILL.md) |
| 需要在测试环境验证修复并请用户验收 | [verify-delivery](../verify-delivery/SKILL.md) |
| 用户已确认本轮测试版本，准备发布staging | [release-staging](../release-staging/SKILL.md) |
| 已实际上线，需要更新设计底稿 | [refresh-design](../refresh-design/SKILL.md) |
| staging验证、底稿同步与交付记录已完成，准备最后交付 | [notify-project](../notify-project/SKILL.md)，分别通知用户和默认项目群 |
| 用户要测试/改进这套Skills | [evaluate-workflow](../evaluate-workflow/SKILL.md) |
| 调查后仍有影响方向的用户决定 | [clarify-task](../clarify-task/SKILL.md)，再加载宿主grill-me |
| 需要向已绑定项目群发阶段消息 | [notify-project](../notify-project/SKILL.md)，再加载宿主feishu-messenger |

按需读取当前阶段，不一次加载全部Skill和参考。仅修改局部文案等已有合同充分的小任务，复用前置成果；说明跳过阶段的依据。研发实现时仍逐片验证。

## 连续性

复用一份任务记录，无等价物时采用 [task模板](../../../docs/workflow/templates/task.md)。记录固定的设计提交/PRD、接口、case，当前切片、证据、阻塞和下一步。不得将未交接的最新designend自动替换本轮来源。

已授权后续工作继续执行，不因切换Skill重复索取许可。缺用户决定时执行clarify-task，不自行定方向；缺case时先索取，合成样例只用于标明的开发验证。

需求累计后的查找/关闭按 [文件生命周期](../../../docs/workflow/file-lifecycle.md) 处理：默认只读当前模块来源、本次task与直接依赖；旧需求按ID/模块搜索。已交付需求关闭前确认当前文档和长期测试已更新，不把历史提案自动当当前规则。

## 冲突和范围

界面/PRD/接口/case冲突时定位具体差异；产品语义不可擅自裁定。新增业务限制、重大交互或职责变化先提出；不以“继续”推定超出授权的部署或外部消息权限。

## 完成

上线交付按顺序执行verify-delivery（测试环境修复验证→飞书请用户验收→等待明确确认）→release-staging（发布已验收版本并验证）→refresh-design（同步底稿并验证）→补齐交付记录→notify-project（最后分别通知用户和默认群）。不能将测试通过、群通知或旧的测试机部署授权当成本轮用户确认。

交付用户实际请求的范围；逐项区分完成、未通过、未执行。只在实际发布并完成对应工作后记录上线与底稿同步，不能用源码测试替代。更新任务记录以供下一会话恢复。通知失败只影响通知状态，不伪装成业务未实现或发送成功；恢复时只续办待完成通知，不重跑发布。需求疑问/阻塞等过程消息仍及时发送；用户只要求PR时不擅自上线或发送上线完成通知。
