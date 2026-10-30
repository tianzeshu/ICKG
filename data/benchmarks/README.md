# 公开基准来源

本目录提供数据来源与评价协议入口，原始基准文件未在此重复打包。获取时遵循各发布方条件，固定确切的数据版本、文件摘要与预处理参数后再运行模型。

| 基准 | 任务 | 来源入口 |
| --- | --- | --- |
| CoNLL03 | 命名实体识别 | [数据发布镜像](https://huggingface.co/datasets/eriktks/conll2003) |
| DocRED | 文档级关系抽取 | [原项目](https://github.com/thunlp/DocRED) |
| ECB+ | 跨文档指称归并 | [原数据项目](https://github.com/cltl/ecbPlus) |
| ICEWS14、ICEWS05-15、ICEWS18 | 时序知识图谱推理 | [RE-GCN基线的数据准备入口](https://github.com/Lee-zix/RE-GCN) |

公开基准采用其任务对应的划分和协议，不统一重划为7∶2∶1。ECB+需固定实体指称范围及评价文档；ICEWS需明确数据变体、时间粒度、过滤方式与单步/多步预测设置。具体版本应与实际实验运行配置共同归档。机器可读入口见[sources.json](sources.json)。
