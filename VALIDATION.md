# 模板包验证

本轮实际执行：

- 10个Skill使用skill-creator的quick_validate.py校验，全部通过。
- 116个Markdown相对链接存在性检查通过；所有JSON文件可解析。
- 评分与场景准备工具10项unittest通过，覆盖23个场景隔离准备、已有内容保护、路径越界、评分/证据缺失、不适用权重、非法输入、低维度和致命问题不被均分掩盖。
- 15份README均为13—21行，保留模块用途、关键入口与使用说明。
- 接口定义位于project/apiend/contracts，原project/contracts不存在。

## 本轮流程调整

测试环境开发修复与本轮验证通过后，飞书私聊用户验收；用户明确确认该版本后，由新增release-staging发布同一制品到staging并验证。随后同步designend底稿、补齐记录，第9步最后分别通知用户和默认项目群。

项目配置示例包含测试/staging环境、用户私聊与默认群的私有绑定引用；实际目标仍未绑定。通知逐路记录回执，不因一路失败重复已成功的另一路。新增C19—C21评估待确认不发布、确认版本与候选不一致、双路通知部分失败；C13/C17/C18及评分依据同步更新。

## 验证边界

以上是模板格式、文档链接和工具测试，不是Skill行为实测。没有执行独立Agent行为评测，没有运行或部署业务应用，也未验证目标项目CI、分支保护、发布或底稿同步脚本。

没有发送飞书消息、绑定真实私聊/群、配置收信或后台提醒；配置示例不代表通知已接通。没有全局安装Skills，也未修改commercial-bidding-tools。原始Skill指纹保留在评估baselines目录，当前版本指纹更新在skill-baseline.json；两者都不是效果分数。

## 复现工具测试

在本包根目录运行：

```bash
python3 -m unittest discover -s project/workflow-evaluation -p 'test_*.py' -v
python3 project/workflow-evaluation/score.py project/workflow-evaluation/scorecard.example.json
```

算分示例为合成数据，不能当作Skill成绩。独立行为评测步骤见project/workflow-evaluation/README.md；Skill格式校验使用宿主skill-creator实际安装位置。
