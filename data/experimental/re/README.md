# ICKG-RE

芯片产业链关系抽取样本。每行保存主体、客体、原始关系标签及对应证据句。

| 划分 | 关系样本数 | 文件 |
| --- | ---: | --- |
| Train | 5,669 | [train.jsonl.gz](train.jsonl.gz) |
| Dev | 1,620 | [dev.jsonl.gz](dev.jsonl.gz) |
| Test | 810 | [test.jsonl.gz](test.jsonl.gz) |
| 合计 | 8,099 | |

## 字段与划分

UTF-8 JSONL使用gzip压缩。字段为`head, head_type, relation, tail, tail_type, sentence`，主体与客体均保留名称字符串，类型保留原始中文标签。

```json
{"head":"中芯国际","head_type":"企业","relation":"属于行业","tail":"晶圆代工行业","tail_type":"行业","sentence":"中芯国际是中国大陆技术最先进、规模最大的晶圆代工龙头企业"}
```

本目录保留固定种子42的现有分组划分，比例约为7∶2∶1。同一证据句的关系不跨集合，不同集合间相同证据句的交集为零；索引见[split_indices.json](split_indices.json)。

数据共有196种原始关系字符串，完整列于[relation_types.json](relation_types.json)。其中整数ID仅用于枚举本版标签，未将标签自动合并为其他本体类别。需要采用归类关系评价时，应固定明确的映射后再运行模型。

## 使用

训练使用Train，Dev用于配置选择，Test用于最终评价。现有原始归档目录继续保留。本次只整理和校验数据，不生成或替代模型实验成绩；实际成绩应与所用划分及标签空间一致。

各集合原始标签计数、名称字符串计数和文件摘要见[statistics.json](statistics.json)、[checksums.sha256](checksums.sha256)，字段约束见[schema.json](schema.json)。来源与文本使用按仓库[数据使用说明](../../../DATA_USE.md)处理。
