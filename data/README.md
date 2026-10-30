# 数据入口

按研究任务选择实验数据，按知识快照选择展示图谱。所有JSONL使用UTF-8，一行一个对象；gzip文件可流式读取。

| 资源 | 主要内容 | 入口 |
| --- | --- | --- |
| ICKG-NER | 6030篇、103972条自动跨度，七类实体 | [NER](experimental/ner/README.md) |
| ICKG-RE | 8099条关系样本、196种原始标签 | [RE](experimental/re/README.md) |
| ICKG-ED | 1785篇、14031指称、6424全局参考身份 | [ED](experimental/ed/README.md) |
| ICKG-TKG | 最终时序实验划分归档状态 | [TKG](experimental/tkg/README.md) |
| 七层全量图谱 | 稳定实体ID、关系断言、时序事实与来源 | [全量说明](full/README.md) |
| 原始归档 | 原抽取语料、关系记录、原始划分与采集附录 | [归档说明](experimental/README.md#原始归档说明) |
| 全球半导体实体库 | 215708个制造商与型号组合，独立外部资源 | [实体目录](../resources/global_semiconductor_entities/README.md) |
| 公开基准 | CoNLL03、DocRED、ECB+、ICEWS系列的来源与协议 | [基准入口](benchmarks/README.md) |

## 计数与划分

NER的实体数按文本内标注跨度计数；RE的样本数按关系实例计数；ED参考身份按全局entity_id去重，不将三个集合簇数相加；外部目录按制造商与型号组合去重。全量图谱快照表示知识可用时点，与实验Train/Dev/Test划分分别组织。

## 读取、校验与评价

最小样例见[examples](../examples/README.md)。完整性检查和B³评价的命令见[复现指南](../guides/REPRODUCIBILITY.md)。每任务的checksums.sha256固定文件内容；统计依据实际发布文件生成。
