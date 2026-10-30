# 数据读取、完整性检查与评价

## 当前可用入口

| 内容 | 状态 |
| --- | --- |
| NER、RE、ED任务数据 | 固定划分、字段、统计和摘要已发布 |
| 全球半导体实体库 | 主数据、来源、Schema及独立校验器已发布 |
| 全量图谱 | 保留当前与历史快照及既有在线展示 |
| B³评价 | 提供标准库实现，覆盖所有指称及单例 |
| 完整方法与基线训练 | 实际训练入口、环境和配置尚待归档 |
| ICKG-TKG时序实验划分 | 最终四元组及匹配ID映射尚待归档 |

本页命令用于读取固定文件、检查数据和评价给定预测，不将文件发布或语法检查当作论文模型成绩已经复现。

## 环境与数据检查

以下脚本只需Python 3.11及以上标准库，不需安装训练框架。在仓库根目录执行：

```bash
python scripts/validate_data.py
```

脚本核对NER/RE/ED与独立资源的文件摘要、跨度、身份对应和发布统计。资源目录另有独立校验器，见其README。全量快照原有文件摘要见data/full/FILES_SHA256SUMS。

## 数据读取

```bash
python examples/read_data.py --task ner --split train
python examples/read_data.py --task re --split dev
python examples/read_data.py --task ed --split test
```

## ED评价

预测文件使用UTF-8 JSONL，每行包含mention_id与cluster_id。每个参考指称恰好出现一次；多余、缺失或重复指称会报错。cluster_id只表示该次预测内的簇编号，不需与参考entity_id同名。

```bash
python scripts/evaluate_ed.py --gold data/experimental/ed/labels/test.jsonl.gz --pred predictions.jsonl --output metrics.json
```

输出B³-P、B³-R和B³-F1，统一为0到100的百分数。对全部指称逐项求平均，包含单例；不丢弃无匹配指称，不把不同集合混在一次聚类评分中。

## 论文运行对应

固定当前发布文件后，仍需将原实验实际数据、关系类别映射、模型检查点及运行配置对应归档。原关系划分具有时间交叉，不能直接当作TKG的按时间划分；NER新补标数据亦不自动对应既有性能表。当前目录不提供占位训练脚本或虚构检查点。

## 原有内容

本次增加任务数据和导航，未删除原始数据、图谱页面或发布流程。更新前首页可查看[固定提交原页](https://github.com/tianzeshu/ICKG/blob/9251319a9b835331f31eaede8d0aa3048b87da25/README.md)，本仓库也保留[归档副本](archive/README.before-reorganization.md)。数据来源与使用条件见[DATA_USE.md](../DATA_USE.md)。
