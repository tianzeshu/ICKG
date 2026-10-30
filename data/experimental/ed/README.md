# ICKG-ED

芯片产业链跨文档实体归并数据。给定原文和实体指称，模型将指向同一现实对象的指称归为实体簇。输入、参考身份标签和标签核查目录分别保存。

## 文件与规模

| 划分 | 文档数 | 指称数 | 该集合参考簇数 | 输入 | 目标 |
| --- | ---: | ---: | ---: | --- | --- |
| Train | 1,250 | 9,819 | 4,981 | [inputs/train.jsonl.gz](inputs/train.jsonl.gz) | [labels/train.jsonl.gz](labels/train.jsonl.gz) |
| Dev | 357 | 2,802 | 1,741 | [inputs/dev.jsonl.gz](inputs/dev.jsonl.gz) | [labels/dev.jsonl.gz](labels/dev.jsonl.gz) |
| Test | 178 | 1,410 | 716 | [inputs/test.jsonl.gz](inputs/test.jsonl.gz) | [labels/test.jsonl.gz](labels/test.jsonl.gz) |

全集共1,785篇、14,031个指称、6,424个全局参考身份。各集合的簇数独立去重，不能相加作为全局身份数。

## 字段

UTF-8 JSONL使用gzip压缩，输入每行一篇文档，目标每行一个指称。

| 文件 | 主要字段 |
| --- | --- |
| `inputs/*.jsonl.gz` | `document_id, text, sources, mentions, relations, original_sample_ids` |
| `mentions`元素 | `mention_id, start, end, mention, type` |
| `labels/*.jsonl.gz` | `mention_id, document_id, entity_id, type` |
| `reference/entity_catalog.jsonl.gz` | 参考身份、规范名称、别名、指称ID及标注来源 |

`start/end`采用从0开始、右端不包含的Unicode字符区间，满足`text[start:end] == mention`。输入中的关系使用本篇文档的`mention_id`作端点。时间及证据为已保留的原始辅助信息，来源的文章时间不自动解释为关系发生时间。字段约束见[schema.json](schema.json)。

## 划分与评价

保留现有固定种子42、约7∶2∶1的来源文章和已识别近重复文档分组划分。同一来源URL及已识别来源组不跨集合，现实实体可以在不同集合再次出现；文档成员见[split_membership.json](split_membership.json)，交叉身份数见[statistics.json](statistics.json)。

训练读取Train输入和对应标签，Dev用于阈值选择；Test输入不包含参考`entity_id`。Test身份目标以及全局参考实体目录仅用于评价和标签核查，不作为测试时的模型候选知识库。

归并评价采用B³：逐指称比较预测簇与参考簇的交集，分别除以预测簇大小和参考簇大小后，对评价集合全部指称求平均，最后计算B³-P与B³-R的调和平均。每个评价指称应恰好分配到一个预测簇，单例同样参与评价，不能只评价已找到匹配的指称。

## 标注状态

身份标签为规则与AI上下文辅助形成的参考标注（silver），`human_verified=false`。保留已确认的别名归并，区分母子公司、型号差异、不同报告期及具体文献等身份范围。全局参考目录可查看各身份的名称和标注来源。

本次发布固定数据与评价约定，不生成模型成绩。来源和第三方材料的使用条件见仓库[数据使用说明](../../../DATA_USE.md)，文件摘要见[checksums.sha256](checksums.sha256)。
