<div align="center">

# ICKG

### 多层次时序产业链知识图谱

Multilevel Temporal Industrial-Chain Knowledge Graph

面向半导体产业链，连接行业、企业、产品、政策、专利、报告与人物，组织实体关系、时间信息及来源证据。

**[在线探索](https://tianzeshu.github.io/ICKG/) · [下载数据](https://github.com/tianzeshu/ICKG/archive/refs/heads/main.zip) · [数据说明](data/README.md) · [引用](CITATION.cff)**

</div>

---

本仓库配套论文《**多层次时序产业链知识图谱构建方法研究**》，提供半导体产业链数据、七层图谱及交互展示。研究方法围绕本体构建、信息抽取、实体消歧和时序知识图谱推理展开，支持产业要素关联分析与关系演化研究。

<a href="https://tianzeshu.github.io/ICKG/">
  <img src="docs/assets/full-overview.png" alt="ICKG七层产业链知识图谱预览，点击进入交互展示" width="100%">
</a>

*点击预览图进入交互页面，可查看实体关联、切换知识快照并按日期筛选。*

## 从这里开始

| 你希望做什么 | 入口 |
| --- | --- |
| 浏览七层产业链图谱 | [在线交互展示](https://tianzeshu.github.io/ICKG/) |
| 使用实体、关系和时序事实 | [最新全量图谱](data/full/current/) · [字段定义](data/full/public-schema.json) |
| 查看截至2025年底的知识快照 | [历史快照](data/full/asof-2025/) |
| 下载NER、RE与ED任务数据 | [实验数据导航](data/experimental/README.md) |
| 使用半导体型号词表 | [全球半导体实体目录](resources/global_semiconductor_entities/README.md) |
| 查看数据读取与评价步骤 | [复现指南](guides/REPRODUCIBILITY.md) |
| 核查来源、时间口径和文件完整性 | [全量说明](data/full/README.md) · [文件校验清单](data/full/FILES_SHA256SUMS) |

## 数据下载

完整数据可通过页面顶部的“**下载数据**”链接下载，也可以执行：

```bash
git clone https://github.com/tianzeshu/ICKG.git
cd ICKG
```

### 全量图谱

| 知识快照 | 正式实体 | 已断言去重时序事实 | 数据目录 |
| --- | ---: | ---: | --- |
| 最新快照 · 2026-10-28 | 45,230 | 47,406 | [current](data/full/current/) |
| 历史快照 · 截至2025-12-31 | 43,940 | 36,423 | [asof-2025](data/full/asof-2025/) |

统计按正式实体和已断言事实计数；两个快照的事实表各另保留1条计划记录，通过`modality`字段区分。快照表示相应时点可获得的知识，包含不同的来源公开时间和事实时间。

<details>
<summary><strong>展开查看七层实体规模</strong></summary>

| 语义层 | 最新快照 | 历史快照 |
| --- | ---: | ---: |
| 行业 Industry | 670 | 252 |
| 企业 Company | 2,720 | 1,853 |
| 产品 Product | 379 | 379 |
| 政策 Policy | 131 | 126 |
| 专利 Patent | 10,022 | 10,022 |
| 报告 Report | 513 | 513 |
| 人物 Person，含专利发明人 | 30,795 | 30,795 |
| **合计** | **45,230** | **43,940** |

</details>

### 自建任务数据

| 任务 | 发布内容 | Train / Dev / Test | 下载与字段 |
| --- | --- | --- | --- |
| ICKG-NER | 6,030篇，103,972条自动实体跨度 | 4,221 / 1,206 / 603篇 | [NER](data/experimental/ner/README.md) |
| ICKG-RE | 8,099条关系样本，196种原始关系标签 | 5,669 / 1,620 / 810条 | [RE](data/experimental/re/README.md) |
| ICKG-ED | 1,785篇，14,031指称，6,424全局参考身份 | 1,250 / 357 / 178篇 | [ED](data/experimental/ed/README.md) |
| ICKG-TKG | 最终时序划分待归档 | — | [归档状态](data/experimental/tkg/README.md) |

NER提供自动补标后的固定跨度，ED身份为AI辅助参考标签；各目录保留标注状态与校验结果。本次发布固定数据文件和评价入口，模型成绩的复现还需对应实际运行代码与配置。原始语料、关系记录及旧划分仍可通过[原归档说明](data/experimental/README.md#原始归档说明)访问。

### 外部资源与公开基准

- [全球半导体实体库](resources/global_semiconductor_entities/README.md)：215,708个去重制造商与型号组合，附来源清单、核验层级及读取样例，可用于词表扩展和实体检索。
- [公开基准入口](data/benchmarks/README.md)：CoNLL03、DocRED、ECB+及ICEWS系列的数据来源和协议说明。

外部实体目录与实验文本跨度分别统计；它是否参与某次实验应由相应配置明确记录。

## 数据组织与时间信息

全量图谱采用UTF-8 JSONL，每行一条记录，使用gzip压缩。实体、关系断言、时序事实和来源文档分别建表，通过稳定ID关联。

| 文件 | 内容 |
| --- | --- |
| `entities.jsonl.gz` | 七类实体、规范名称、别名及证据引用 |
| `assertions.jsonl.gz` | 关系断言、主体与客体、模态及来源信息 |
| `temporal_facts.jsonl.gz` | 归并后的时序事实及其支持断言 |
| `quadruples_event.jsonl.gz` | 按事实发生或生效时间组织的四元组 |
| `quadruples_observation.jsonl.gz` | 按来源观察时间组织的四元组 |
| `documents.jsonl.gz`、`mentions.jsonl.gz` | 来源元数据、文档关联和证据定位 |

时间记录区分**事实发生或生效时间**与**来源公开或观察时间**，支持时间点、区间及不同精度；未知事实时间保留空值。完整字段、分类结构和辅助表见[数据说明](data/full/README.md)与[JSON Schema](data/full/public-schema.json)。

## 快速读取

以下代码使用Python标准库，从最新快照读取一个实体：

```python
import gzip
import json
from pathlib import Path

path = Path("data/full/current/entities.jsonl.gz")
with gzip.open(path, "rt", encoding="utf-8") as file:
    entity = json.loads(next(file))

print(entity["entity_id"], entity["canonical_name"], entity["type"])
```

切换为`data/full/asof-2025/`即可读取历史快照。批量处理时按行读取，避免一次性载入全部数据。

## 仓库导航

```text
ICKG/
├── README.md                 项目与数据入口
├── CITATION.cff              引用信息
├── DATA_USE.md               来源与使用说明
├── data/
│   ├── experimental/         NER、RE、ED及TKG状态；原归档保留
│   ├── benchmarks/           公开基准来源与协议
│   └── full/                 最新与历史七层图谱快照
├── resources/                独立全球半导体型号目录
├── examples/                 数据样例与加载方式
├── scripts/                  数据完整性检查与B³评价
├── guides/                   数据组织及复现指南
└── docs/                     现有在线交互图谱
```

## 关联论文与引用

**多层次时序产业链知识图谱构建方法研究**  
田泽庶、白佳敏、张宏莉  
哈尔滨工业大学计算学部

论文状态：软件学报稿件。使用数据时，请注明所用目录、快照日期及仓库提交号；引用信息见[CITATION.cff](CITATION.cff)，也可使用仓库侧栏的 **Cite this repository**。

## 数据使用与反馈

数据包含自动抽取和辅助复核记录，标注状态与来源核验层级保留在相应文件中。全量图谱提供来源链接和证据坐标，第三方全文、原图及其使用条件以各来源为准，详见[DATA_USE.md](DATA_USE.md)。

字段疑问、数据问题或使用反馈，可提交[GitHub Issue](https://github.com/tianzeshu/ICKG/issues)。建议同时注明文件路径、实体或事实ID，以及所用快照。
