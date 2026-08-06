> 社区翻译（草稿）——NTARI 政策 P2-002《全球多语言广播》。来源：contributing.md（英文原版，2026-07-29 快照）。本文为机器辅助的社区翻译草稿，尚待区域维护者按 P2-002 §3.1 审核。根据 §2.2，核心技术规范仍以英文为准。
>
> 如发现译文有误，欢迎 fork 仓库并提交 Pull Request
> 来改进翻译：https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale。翻译修正与代码贡献同样宝贵，我们诚挚欢迎。

# 为 LBTAS 做贡献

## 如何贡献

贡献活动通过 NTARI Slack 工作区进行。

**加入讨论**：https://ntari.slack.com/archives/C09N88JN2SH

## 贡献类型

### 代码贡献
- Bug 修复
- 功能实现
- 性能改进
- 文档更新

### 研究贡献
- 用例研究
- 使用 LBTAS 的学术论文
- 集成示例
- 评级有效性分析

### 社区贡献
- 问题（issue）报告
- 功能建议
- 文档改进
- 翻译支持

## 开发流程

### 1. 讨论
在开始工作之前，请先在 Slack 频道中讨论你提议的更改。

### 2. Fork 与创建分支
```bash
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale
git checkout -b feature/your-feature-name
```

### 3. 代码规范

**Python 风格**
- 遵循 PEP 8
- 使用类型注解（type hints）
- 为所有函数和类编写 docstring
- 保持函数职责单一，且不超过 50 行

**文档风格**
- 使用客观、技术性的语言撰写
- 避免使用形容词和副词
- 附上代码示例
- 测试所有示例

### 4. 测试

测试你的更改：
```bash
# Test basic functionality
python3 lbtas.py rate --exchange "TestService"
python3 lbtas.py view --exchange "TestService"
python3 lbtas.py report

# Test as library
python3 -c "from lbtas import LevesonRatingSystem; rs = LevesonRatingSystem(); rs.add_exchange('test'); print('OK')"
```

### 5. 提交信息（Commit Messages）

格式：`type: brief description`

类型：
- `feat`：新功能
- `fix`：Bug 修复
- `docs`：文档更改
- `refactor`：代码重构
- `test`：测试的新增或修改
- `chore`：维护性任务

示例：
```
feat: add CSV export format
fix: handle empty rating lists in report
docs: update installation instructions
```

### 6. Pull Request

1. 将你的分支推送到你的 fork
2. 向 main 分支发起 pull request
3. 引用所有相关的 issue
4. 说明所做的更改及其理由
5. 等待审核，并在 Slack 中参与讨论

## 行为准则

### 行为标准

- 尊重所有贡献者
- 以技术价值为核心
- 提供建设性的反馈
- 接受对你的贡献的批评意见
- 将项目目标置于个人偏好之上

### 禁止行为

- 人身攻击或骚扰
- 歧视性言论或行为
- 恶意挑衅（trolling）或煽动性言论
- 泄露他人的私人信息
- 不道德或不专业的行为

### 执行措施

违规可能导致：
1. 警告
2. 暂时停止参与项目
3. 永久禁止参与项目

违规行为请举报至：forge@ntari.org

## 许可证

一旦提交贡献，即表示你同意你的贡献将以 AGPL-3.0 许可证发布。

所有贡献必须：
- 是你的原创作品，或已注明适当的出处
- 不侵犯任何第三方权利
- 符合 AGPL-3.0 的各项要求

## 有疑问？

关于贡献的问题：
1. 在 Slack 中提问：https://ntari.slack.com/archives/C09N88JN2SH
2. 在 GitHub 上提交 issue
3. 发送邮件至：forge@ntari.org

## 贡献者致谢

贡献者将在以下位置获得署名：
- Git 提交历史
- 发布说明（release notes）
- 项目文档

获得认可的贡献类型：
- 代码贡献（提交记录）
- 研究贡献（引用）
- 文档贡献（文档署名）
- 社区支持（鸣谢）
