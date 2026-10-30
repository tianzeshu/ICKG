# ICKG-NER

芯片产业链命名实体识别数据。每行保存一篇文本及其已标注实体跨度，包含行业、企业、产品、政策、专利、报告和人物七类实体。

## 下载与划分

| 划分 | 文本数 | 实体跨度数 | 文件 |
| --- | ---: | ---: | --- |
| Train | 4,221 | 72,742 | [train.jsonl.gz](train.jsonl.gz) |
| Dev | 1,206 | 20,642 | [dev.jsonl.gz](dev.jsonl.gz) |
| Test | 603 | 10,588 | [test.jsonl.gz](test.jsonl.gz) |
| 合计 | 6,030 | 103,972 | |

文本及文档ID保持不变，按已冻结的来源组索引导出7∶2∶1划分。同一已识别来源组不跨集合；相同全文在不同集合间没有交叉。固定索引见[split_indices.json](split_indices.json)，分组映射见[source_groups.json](source_groups.json)。

## 字段

UTF-8 JSONL使用gzip压缩，每行一个JSON对象。

| 字段 | 含义 |
| --- | --- |
| `id`、`text` | 文本ID及原文 |
| `entities` | 实体数组；包含`eid, start, end, mention, type, annotation_method, human_verified` |
| `relations` | 原联合抽取记录中保留的辅助关系，以当前文本中的实体`eid`为端点 |
| `annotation_metadata` | 标注方法、来源组及原文保留信息 |

字符位置采用从0开始、右端不包含的区间，满足`text[start:end] == mention`。类别取值见[entity_types.json](entity_types.json)，字段约束见[schema.json](schema.json)。`relations`中的辅助关系不等同于独立ICKG-RE样本总量。

## 标注与使用

本目录提供自动提取与AI辅助复核后的跨度标注，`human_verified=false`；它与现有原始数据目录分别保存。全部103,972条跨度的位置与原文已逐项校验。原文包含不同年份的公开文本，保留其实际内容，不统一改写为某个年份范围。

这些文件固定当前发布的标签与划分；本次整理没有运行模型训练或产生性能结果。模型成绩应对应其实际使用的数据和配置。

```python
import gzip
import json

with gzip.open("data/experimental/ner/train.jsonl.gz", "rt", encoding="utf-8") as file:
    sample = json.loads(next(file))
for entity in sample["entities"]:
    assert sample["text"][entity["start"]:entity["end"]] == entity["mention"]
```

统计和文件摘要分别见[statistics.json](statistics.json)与[checksums.sha256](checksums.sha256)。第三方文本的来源与使用条件按仓库[数据使用说明](../../../DATA_USE.md)处理。
