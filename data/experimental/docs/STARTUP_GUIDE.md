# ICKG 知识图谱采集系统 v5.0 - 启动指南
**版本**: 5.0  
**创建日期**: 2026-01-29  
**状态**: ✅ 就绪

---

## 目录

1. [系统概述](#系统概述)
2. [快速开始](#快速开始)
3. [环境准备](#环境准备)
4. [使用方式](#使用方式)
5. [输出文件](#输出文件)
6. [故障排除](#故障排除)

---

## 系统概述

### 功能

✅ **7 种实体类型** - Company, Person, Product, Patent, Policy, Industry, Report  
✅ **15+ 种关系类型** - collaboratesWith, investsIn, acquires, develops 等  
✅ **标准五元组格式** - (head, relation, tail, time, evidence_url)  
✅ **训练数据输出** - 支持本地模型训练  

### 架构

```
ICKG_Semiconductor_v5/
├── src/
│   ├── __init__.py
│   ├── collector.py      # 主采集器
│   ├── processor.py      # 数据处理器
│   ├── llm_client.py     # LLM 客户端
│   └── utils.py          # 工具函数
├── data/
│   └── batch_companies.json
├── output/               # 输出目录
├── docs/
│   ├── DATA_SCHEMA.md
│   └── STARTUP_GUIDE.md
├── config.json           # 配置文件
├── requirements.txt      # 依赖
└── start.py              # 启动脚本
```

---

## 快速开始

```bash
# 1. 进入项目目录
cd ICKG_Semiconductor_v5

# 2. 安装依赖
pip install -r requirements.txt

# 3. 一键启动
python start.py
```

---

## 环境准备

### 前置条件

- **Python**: 3.8+
- **依赖**: httpx

### 安装依赖

```bash
pip install httpx
```

---

## 使用方式

### 方式 1: 交互式启动 (推荐)

```bash
python start.py
```

会显示配置确认界面，按 `y` 开始采集。

### 方式 2: 命令行参数

```bash
# 测试模式 (1家企业)
python src/collector.py --test

# 采集指定企业
python src/collector.py --companies "中芯国际,华虹公司"

# 批量采集
python src/collector.py --batch data/batch_companies.json --output output

# 自定义参数
python src/collector.py --companies "中芯国际" --news 6 --output my_output
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--companies` | 企业列表（逗号分隔） | - |
| `--batch` | 企业清单文件 (JSON) | - |
| `--test` | 测试模式 | False |
| `--news` | 每企业新闻数 | 6 |
| `--output` | 输出目录 | output |
| `--api-key` | API密钥 | config.json 中 |

---

## 输出文件

采集完成后，结果保存在 `output/` 目录：

```
output/
├── entity2id.txt          # 实体ID映射 (TSV)
├── id2entity.json         # 实体详细信息 (JSON)
├── relations.jsonl        # 五元组关系 (JSONL)
├── training_data.jsonl    # 训练数据 (JSONL)
├── collection_stats.json  # 采集统计 (JSON)
└── collection.log         # 详细日志
```

### 查看结果

```bash
# 查看实体统计
python -c "import json; e=json.load(open('output/id2entity.json')); print(f'实体数: {len(e)}')"

# 查看关系统计
python -c "import json; r=[json.loads(l) for l in open('output/relations.jsonl')]; print(f'关系数: {len(r)}')"

# 查看训练数据
python -c "import json; t=[json.loads(l) for l in open('output/training_data.jsonl')]; print(f'训练样本数: {len(t)}')"
```

---

## 故障排除

### 问题 1: ModuleNotFoundError

**解决**:
```bash
cd ICKG_Semiconductor_v5
pip install -r requirements.txt
```

### 问题 2: API 401 错误

**解决**: 检查 API Key 是否正确配置在 `config.json` 中。

### 问题 3: JSON 解析错误

**解决**: 这是正常现象，系统会自动跳过失败的请求并继续。

### 问题 4: 采集超时

**解决**: 检查网络连接，或减少 `--news` 参数值。

---

## 配置文件

`config.json` 示例：

```json
{
  "api_key": "YOUR_API_KEY",
  "endpoint_id": "YOUR_ENDPOINT_ID",
  "model_name": "YOUR_MODEL_NAME",
  "api_endpoint": "https://ark.cn-beijing.volces.com/api/v3",
  "companies": ["中芯国际", "华虹公司", ...],
  "news_per_company": 6,
  "output_dir": "output"
}
```

---

## 常见问题

### Q: 采集需要多长时间?
**A**: 10 家企业约 10-30 分钟，取决于网络速度和 API 响应。

### Q: 可以中途中断吗?
**A**: 可以按 `Ctrl+C` 中断，已采集的数据会保存到 `output/`。

### Q: 如何增加企业数量?
**A**: 修改 `config.json` 中的 `companies` 数组。

---

## 下一步

1. **运行采集**: `python start.py`
2. **查看结果**: 检查 `output/` 目录
3. **数据验证**: 手动审核关键关系

---

**准备好了吗？运行 `python start.py` 开始采集！** 🚀

