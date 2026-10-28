# ICKG 知识图谱采集系统 v5.0
**版本**: 5.0  
**状态**: 🚧 开发中

---

## 目录结构

```
ICKG_Semiconductor_v5/
├── src/                      # 核心代码
│   ├── __init__.py
│   ├── collector.py          # 主采集器 (KGCollector)
│   ├── processor.py          # 数据处理器 (DataProcessor)
│   ├── llm_client.py         # LLM 客户端 (LLMClient)
│   └── utils.py              # 工具函数
├── data/                     # 数据目录
│   └── batch_companies.json  # 企业清单
├── output/                   # 输出目录 (自动创建)
├── docs/                     # 文档
│   ├── DATA_SCHEMA.md        # 数据格式说明
│   └── STARTUP_GUIDE.md      # 启动指南
├── config.json               # 配置文件
├── requirements.txt          # Python 依赖
├── start.py                  # 启动脚本
└── README.md                 # 本文件
```

## 快速开始

```bash
# 1. 进入项目目录
cd data/experimental

# 2. 激活虚拟环境
ICKGData_Venv\Scripts\Activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行采集
python start.py --test    # 测试模式 (1家企业)
python start.py           # 完整采集
```

## 输出文件

| 文件 | 格式 | 说明 |
|------|------|------|
| `entity2id.txt` | TSV | 实体ID映射 |
| `id2entity.json` | JSON | 完整实体信息 |
| `relations.jsonl` | JSONL | 五元组关系 |
| `training_data.jsonl` | JSONL | 训练数据格式 |
| `collection_stats.json` | JSON | 采集统计 |

## 文档

- [启动指南](STARTUP_GUIDE.md)
- [数据格式说明](DATA_SCHEMA.md)

