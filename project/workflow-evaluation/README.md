# Skill测试与评分

这里用隔离任务检查Skills是否按约定工作，再用实际证据比较版本。目前提供33个场景和评分工具，尚无独立Agent行为实测结果。

## 关键入口

- [评估步骤](evaluation-guide.md)：准备任务、执行、比较和改进。
- [场景输入](scenarios/cases.json)与[评分标准](rubrics/scoring.md)。
- [评分表示例](scorecard.example.json)与[比较记录模板](run-report.template.md)。

## 怎么用

先固定Skill版本和运行条件，在隔离工作区执行场景；评审者查看产物后填写评分表，再运行：

```bash
python3 score.py /path/to/actual-scorecard.json
```

命令在本目录执行。算分工具只汇总人工评分，不判断业务是否正确；测试群通知时使用模拟收据，不给真实群发消息。

新增B01—B10检查清单修复、五轮累计预算、原表回写、回归晋升、漏斗分母、身份缺口及重开归因；尚未执行独立Agent行为实测。
