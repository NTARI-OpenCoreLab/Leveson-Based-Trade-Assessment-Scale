> 社区翻译（草稿）— NTARI 政策 P2-002《全球多语言广播》。来源：README.md（英文原版，快照日期 2026-07-29）。本文件为机器辅助生成的社区翻译草稿，尚待区域维护者按照 P2-002 §3.1 进行审核。根据 §2.2，核心技术规范仍以英文为准。
>
> 如发现译文有误，欢迎 fork 仓库并提交 Pull Request
> 来改进翻译：https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale。翻译修正与代码贡献同样宝贵，我们诚挚欢迎。

# 基于 Leveson 的贸易评估量表（LBTAS）

一套面向数字商务的评级系统，基于 Nancy Leveson 的飞机软件评估方法论，并具备双向评估标准。

## 概述

基于 Leveson 的贸易评估量表（Leveson-Based Trade Assessment Scale，LBTAS）实现了 Nancy Leveson 为航空航天应用开发的飞机软件评估方法论，并将其调整用于数字商务与经济评估场景。LBTAS 提供了一个使用 6 级量表采集交易质量数据的框架。

## 传统评级系统的问题

5 星评级系统无法提供能够激励生产者改进的数据。5 星系统由 Forbes Travel Guide（前身为 Mobil Travel Guide）于 1958 年创立，用于宣传美国州际公路沿线的酒店质量。它被设计为服务于公路旅行的单向沟通系统，而非为数字商务而生。

**局限性：**
- 评级在电子商务场景中提供的价值有限
- 公关经理会为政策变革设置障碍
- 粒度不足，无法捕捉交易的复杂性
- 单向评估忽视了消费者的问责
- 数据不足迫使人们依赖评论区

## 为什么采用 Leveson 方法？

Leveson 系统源自飞机软件开发领域，在该领域中系统失效会导致生命损失或研发投资的浪费。这一方法论：

- 使用带有类别定义的 6 级量表（从 +4 到 -1）
- 将含义压缩进每一个评级等级
- 减少对评论区数据的依赖
- 支持双向评估（生产者与消费者双方）
- 支持数据驱动的改进循环

## 量表定义

### +4 **惊喜（Delight）**
交互预见了用户在交易之后的实践与关注点的演变

### +3 **无负面后果（No Negative Consequences）**
交互的设计旨在防止损失，超越基本质量标准

### +2 **基本满意（Basic Satisfaction）**
交互达到社会普遍接受的标准，超出用户明确表达的需求

### +1 **基本承诺（Basic Promise）**
交互满足用户明确表达的全部需求，仅此而已

### 0 **敷衍式满足（Cynical Satisfaction）**
交互兑现了一个基本承诺，但在用户满意度方面几乎或完全没有投入用心

### -1 **无信任（No Trust）**
用户受到伤害、被剥削，或所获得的产品/服务表现出毫无用心或存在恶意的证据

## 双向评估

LBTAS 通过为双方维护评级，在数字网络中实现双向问责：

- **生产者（Producers）**：识别服务提供方
- **消费者（Consumers）**：识别客户

这一方法促进社区自治，减少对集中式内容审核的需求。

## 解读声誉

评级从不取平均值。声誉是在各个等级（`-1` 到 `+4`）上收到的评级数量，再加上总数。总数本身就有意义：它反映了交易量，并间接反映了服务时长。在 5,000 条评级上呈现的干净分布，比在 5 条评级上呈现的相同形态是更强的信号——而取平均值会把两者压缩成同一个数字，从而抹去这种差异。（该计数指的是评级的数量；精确的交易与服务年限数据来自 API，API 会为每一次评级事件加盖时间戳。）

`-1`（「无信任」）从不会被稀释：`report` 命令会在 `harm_flagged` 列表中列出每一个收到过一条或多条 `-1` 评级的交换（exchange），而 `list` 会为任何带有 `-1` 的交换附加伤害标记。

## 功能特性

- **方法论**：基于航空航天评估框架
- **双向评估**：对交易中的双方进行评级
- **粒度**：带有明确定义的 6 级量表
- **依赖项**：可集成到各类系统中
- **数据库支持**：支持持久化层
- **开源**：社区驱动的开发与定制

## 安装

```bash
# Clone the repository
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale

# Make executable (optional)
chmod +x lbtas.py

# Run directly
python3 lbtas.py --help
```

无需任何外部依赖。仅使用 Python 3 标准库。

## 快速上手

```python
from lbtas import LevesonRatingSystem

# Initialize the rating system
rating_system = LevesonRatingSystem()

# Add an exchange (transaction)
rating_system.add_exchange("transaction_001")

# Add ratings (categories: reliability, usability, performance, support)
rating_system.add_rating(
    exchange_name="transaction_001",
    criterion="reliability",
    rating=3  # No Negative Consequences
)

# Read the distribution (ratings are never averaged)
ratings = rating_system.view_ratings("transaction_001")
print(ratings["reliability"])
# {'distribution': {'-1': 0, '0': 0, '1': 0, '2': 0, '3': 1, '4': 0}, 'total': 1}
```

### 命令行界面

```bash
# Interactive rating
python3 lbtas.py rate --exchange "MyService"

# Programmatic rating
python3 lbtas.py add --exchange "MyService" --criterion reliability --rating 3

# View ratings
python3 lbtas.py view --exchange "MyService"

# Generate report
python3 lbtas.py report

# Export data
python3 lbtas.py export --format json --output ratings.json
```

## 存储

LBTAS 使用 JSON 文件存储实现持久化：

```python
# Initialize with storage file
rating_system = LevesonRatingSystem(storage_file='ratings.json')

# Ratings are saved automatically to the file
rating_system.add_exchange("service_001")
rating_system.add_rating("service_001", "reliability", 3)
```

存储文件格式：
```json
{
  "service_001": {
    "reliability": [3, 4, 3],
    "usability": [2, 3],
    "performance": [4],
    "support": [3, 3, 2],
    "_metadata": {
      "created": "2024-09-04T10:30:00",
      "total_ratings": 10
    }
  }
}
```

### 评级类别

默认类别：
- **可靠性（Reliability）**：可信赖程度与一致性
- **易用性（Usability）**：使用便捷性与用户体验
- **性能（Performance）**：速度与效率
- **支持（Support）**：客户服务质量

可在初始化时定义自定义类别。

## 应用场景

### 学术研究
- 研究评级量表设计如何影响用户行为与市场结果
- 衡量双向评估对信任与合作的影响
- 分析基于质量的评估方案作为现有框架的替代

### 电子商务平台
- 为市场交易实现质量指标
- 支持社区驱动的声誉系统
- 通过自治减少内容审核开销

### 数字合作社
- 促进点对点问责
- 支持治理结构
- 支持数据驱动的政策改进

## 架构

LBTAS 以单个 Python 模块实现，包含：

1. **核心类**：`LevesonRatingSystem` 管理评级与存储
2. **JSON 持久化**：基于文件的存储，自动保存
3. **CLI 界面**：用于交互式和程序化使用的命令行工具
4. **无外部依赖**：仅使用 Python 标准库

系统支持：
- 交互式评级采集
- 程序化评级提交
- 自定义评级类别
- 报告生成与数据导出

## 文档

- [完整文档](docs/README.md)
- [API 参考](docs/api.md)
- [集成指南](docs/integration.md)
- [研究应用](docs/research.md)

## 参与贡献

贡献通过 NTARI Slack 工作区进行：

**加入讨论**：https://ntari.slack.com/archives/C09N88JN2SH

请参阅我们的[贡献指南](CONTRIBUTING.md)，了解：

- 代码风格与标准
- 测试要求
- Pull Request 流程
- 社区行为准则

## 研究与开发

本程序由 **Network Theory Applied Research Institute 的 Forge Laboratory**（现为 NTARI Research & Development）出品，由 Jodson B. Graves 于 2024 年 9 月 4 日使用 ChatGPT-3 创建。

### 关于 NTARI Research & Development

NTARI Research & Development 是 NTARI 的软件开发计划，致力于打造运用网络理论增强互联网协作能力的数字系统与协议。我们开发开源工具、平台与框架，助力社区构建线上生态系统。

**了解更多并支持 NTARI**：[https://ntari.org](https://ntari.org)

## 引用

如果您在研究中使用了 LBTAS，请引用：

```bibtex
@software{lbtas2024,
  title={Leveson-Based Trade Assessment Scale},
  author={Graves, Jodson B.},
  organization={Network Theory Applied Research Institute},
  year={2024},
  url={https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale}
}
```

## 参考文献

- Leveson, N. G. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press.
- Leveson, N. G. (2020). *CAST Handbook: How to Learn More from Incidents and Accidents*. MIT.

## 许可证

本项目基于 GNU Affero 通用公共许可证 v3.0（AGPL-3.0）授权——详见 [LICENSE](LICENSE) 文件。

AGPL-3.0 许可证要求：
- 当软件通过网络提供使用时，必须公开源代码
- 修改内容必须以相同许可证发布
- 变更必须记录在案
- 网络使用视同分发

## 致谢

- **Nancy Leveson** - 原始方法论的开发
- **NTARI Research & Development** - 研究与实现
- **开源社区** - 贡献与反馈

---

**维护方**：[NTARI Research & Development](https://ntari.org)  
**有疑问？** 请提交 issue，或通过 info@ntari.org 联系我们
