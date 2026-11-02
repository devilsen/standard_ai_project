# 产品设计与研发协作模板

这套模板帮助产品和研发按同一流程协作：独立设计、固定交接、测试环境开发验证、用户确认后发布staging，更新设计底稿，最后通知用户和默认项目群。

## 从哪里看

- [项目与模块入口](project/README.md)：了解各模块做什么、怎样使用。
- [工作流程](project/docs/workflow/README.md)：了解每个阶段和交接方式。
- [Skills导航](project/.agents/skills/README.md)：查看Agent怎样执行任务。
- [测试与评分](project/workflow-evaluation/README.md)：用实际任务改进Skills。

## 怎么采用

1. 阅读[采用说明](project/docs/workflow/adoption.md)，将模板与已有规则合并。
2. 选择一个模块，按[装配示例](project/docs/workflow/example.md)跑完整个流程。
3. 根据真实问题调整规则与Skills，再推广到其他模块。

本包提供文档、10个Skills和评估工具；尚未包含可运行的业务应用，也未修改现有项目。实际完成的检查见[验证记录](VALIDATION.md)。
