# 数据样例

本目录从已发布Train集合和外部目录各取一条真实记录，便于查看字段。sample文件用于格式展示，不代表小型训练或评价集；ED输入与目标分别存放。

- [NER](ner.sample.jsonl)
- [RE](re.sample.jsonl)
- [ED输入](ed_input.sample.jsonl)与[首个指称目标](ed_label.sample.jsonl)
- [外部实体目录](entity_catalog.sample.jsonl)

```bash
python examples/read_data.py --task ner --split train
```

完整文件、划分和标注状态见[数据总表](../data/README.md)。
