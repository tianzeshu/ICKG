# ICKG 知识图谱数据格式说明
**版本**: 5.0  
**创建**: 2026-01-29

---

## 概述

ICKG 系统采用标准的知识图谱数据格式，包括四个核心输出文件：

1. **entity2id.txt** - 实体ID映射 (TSV格式)
2. **id2entity.json** - 完整实体信息 (JSON格式)
3. **relations.jsonl** - 五元组关系 (JSONL格式)
4. **training_data.jsonl** - 训练数据格式 (JSONL格式)

辅助文件：
5. **collection_stats.json** - 采集统计
6. **collection.log** - 详细日志

---

## 1. entity2id.txt

### 格式: TSV (制表符分隔)

```
实体名称     实体ID
中芯国际      1
中芯北方      2
华虹公司      3
12英寸晶圆   4
赵海军       5
...
```

### 说明

- **第一列**: 规范化的实体名称 (中文)
- **第二列**: 唯一的数字ID (从1开始递增)
- **分隔符**: 制表符 (\t)
- **编码**: UTF-8

---

## 2. id2entity.json

### 格式: JSON 对象

```json
{
  "1": {
    "id": 1,
    "mention": "中芯国际",
    "type": "Company",
    "description": "中国大陆领先的集成电路晶圆代工企业...",
    "aliases": ["中芯国际", "SMIC", "中芯"]
  },
  "2": {
    "id": 2,
    "mention": "中芯北方",
    "type": "Company",
    "description": "中芯国际的北方生产基地，位于...",
    "aliases": ["中芯北方"]
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 实体唯一ID |
| mention | str | 实体主要表述 (中文) |
| type | str | 实体类型 (7种之一) |
| description | str | 实体描述或背景信息 |
| aliases | array | 别名列表 (包括主mention) |

### 实体类型定义

| 类型 | 说明 | 示例 |
|------|------|------|
| **Company** | 企业/机构 | 中芯国际, 华虹公司, 台积电 |
| **Person** | 人物/管理者 | 赵海军, 梁孟松, 胡正明 |
| **Product** | 产品/工艺/芯片 | N+2工艺, 麒麟9030, EUV光刻机 |
| **Patent** | 专利/技术 | DUV多重曝光, FinFET技术 |
| **Policy** | 政策/基金 | 国家集成电路基金, 美国出口管制 |
| **Industry** | 产业/领域/生态 | 芯片制造, 半导体, EDA工具 |
| **Report** | 报告/研究 | 2024年芯片产业报告, 市场分析 |

---

## 3. relations.jsonl

### 格式: JSONL (JSON Lines) - 每行一个JSON对象

```jsonl
{"head": "中芯国际", "relation": "acquires", "tail": "中芯北方", "time": "2025年12月29日", "evidence_url": "https://..."}
{"head": "中芯国际", "relation": "produces", "tail": "12英寸晶圆", "time": "2024年第四季度", "evidence_url": "https://..."}
{"head": "赵海军", "relation": "leadsCompany", "tail": "中芯国际", "time": "2025年", "evidence_url": "https://..."}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| head | str | 关系主体实体名称 |
| relation | str | 关系类型 (15种) |
| tail | str | 关系客体实体名称 |
| time | str | 关系发生的时间 (必填) |
| evidence_url | str | 原文链接 (可追溯) |

### 关系类型定义

**企业-企业关系**

| 关系类型 | 说明 | 例子 |
|---------|------|------|
| collaboratesWith | 合作关系 | A公司 -collaboratesWith-> B基金 |
| investsIn | 投资关系 | 国家基金 -investsIn-> 中芯国际 |
| competesWith | 竞争关系 | TSMC -competesWith-> 中芯国际 |
| suppliesTo | 供应关系 | 光刻机厂 -suppliesTo-> 中芯国际 |
| manufactures | 制造关系 | 中芯国际 -manufactures-> 晶圆 |
| acquires | 收购关系 | 中芯国际 -acquires-> 中芯北方 |

**企业-人物关系**

| 关系类型 | 说明 |
|---------|------|
| leadsCompany | 领导企业 |
| foundedCompany | 创办企业 |
| employedBy | 受雇于 |

**企业-产品关系**

| 关系类型 | 说明 |
|---------|------|
| manufactures | 制造产品 |
| produces | 生产产品 |
| develops | 开发产品 |
| usesProduct | 使用产品 |

**其他关系**

| 关系类型 | 说明 |
|---------|------|
| inIndustry | 属于行业 |
| affectedByPolicy | 受政策影响 |
| ownsPatent | 拥有专利 |
| basedOn | 基于 (产品基于技术) |
| usedIn | 用于 (技术用于产品) |

---

## 4. training_data.jsonl

### 格式: JSONL - 用于模型训练

```jsonl
{"id": "news_0001", "text": "2023年，A公司与B公司签署合作协议...", "entities": [...], "time": "2023-07-15", "source": "https://..."}
{"id": "news_0002", "text": "中芯国际与华为签署合作协议...", "entities": [...], "time": "2023-11-20", "source": "https://..."}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | str | 唯一标识符 |
| text | str | 原始新闻文本 |
| entities | array | 实体列表 (含位置信息) |
| time | str | 时间 (可选) |
| source | str | 原文链接 (可选) |

### 实体格式

```json
{
  "start": 0,
  "end": 4,
  "mention": "中芯国际",
  "type": "Company"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| start | int | 实体在 text 中的起始位置 (字符索引) |
| end | int | 实体在 text 中的结束位置 (不包含) |
| mention | str | 实体名称 |
| type | str | 实体类型 (Company/Person/Product/Patent/Policy/Industry/Report) |

---

## 5. collection_stats.json

```json
{
  "timestamp": "2026-01-29T19:30:45.123456",
  "duration_seconds": 1800,
  "entities": {
    "total": 100,
    "by_type": {
      "Company": 25,
      "Product": 50,
      "Industry": 15,
      "Person": 6,
      "Patent": 3,
      "Policy": 1
    }
  },
  "relations": {
    "total": 80,
    "by_type": {
      "produces": 30,
      "inIndustry": 20,
      "investsIn": 15,
      "collaboratesWith": 10,
      "develops": 5
    }
  },
  "training_data": {
    "total": 12
  },
  "summary": {
    "avg_relations_per_entity": 0.8,
    "coverage": "100 个实体，80 条关系"
  }
}
```

---

## 数据质量保证

### 时间字段完整性

✓ **100% 时间覆盖**: 所有关系都从原文中提取了时间  
✓ **多格式支持**: 支持日期、季度、年份等格式  
✓ **格式统一**: 遵循中文日期表述习惯  

### 实体去重

✓ **名称规范化**: 移除空格和括号内容  
✓ **别名链接**: 同一实体的多个表述被链接  
✓ **类型识别**: 自动检测实体的正确类型  

### 关系验证

✓ **源链接追踪**: 每条关系都有原文URL  
✓ **完整性检查**: head和tail都是有效实体  
✓ **关系类型验证**: 关系类型在预定义列表中  

---

**数据格式说明完成！**

