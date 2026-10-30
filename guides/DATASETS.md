# 数据组织指南

从[数据总表](../data/README.md)选择任务。NER、RE和ED的Train用于训练，Dev用于配置选择，Test用于最终评价。NER和ED跨度均为Unicode字符的0起始半开区间；RE保留原始中文实体类型与关系字符串。

ED的inputs不含参考entity_id，labels提供对应身份目标。reference实体目录包含所有集合的参考名称与身份，只供标签核查，不作为盲测输入。主协议按来源文章分组，允许现实实体在不同集合出现。

全量图谱分current与asof-2025两个知识快照，事实时间和来源观察时间分别记录。原采集归档及旧关系划分保留于data/experimental/data/，任务化数据通过实验目录导航访问。

独立全球实体库放resources/，产品型号、包装后缀与品牌范围见其说明。它不计入NER文本跨度，也不自动成为ED测试候选库。

各任务README、schema、statistics和checksums分别负责语义说明、字段约束、实际统计和文件完整性。变更标签后应记录数据与模型运行的对应关系，再比较实验结果。
