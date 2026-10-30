# 全球半导体实体目录

本目录提供独立的半导体产品型号与订货编号资源，按“规范化制造商名称＋目录型号”去重，共 **215,708条**，覆盖 **770个制造商或品牌名称**。可用于名称检索、实体链接候选召回和领域词表扩展。

这是外部实体目录，与ICKG实验文本中的NER位置标注分别统计。记录由公开结构化目录和厂商产品索引自动提取；`human_verified=false`保留在数据中。

## 文件

| 文件 | 内容 |
| --- | --- |
| [entity_catalog.jsonl.gz](entity_catalog.jsonl.gz) | 完整实体目录，UTF-8 JSONL，每行一个实体 |
| [sample.jsonl](sample.jsonl) | 可直接查看的真实记录样例 |
| [schema.json](schema.json) | JSON Schema字段定义 |
| [source_manifest.jsonl](source_manifest.jsonl) | 来源下载地址、源文件摘要、大小与核验信息 |
| [statistics.json](statistics.json) | 规模、范围、去重及来源统计 |
| [manufacturer_statistics.json](manufacturer_statistics.json) | 制造商/品牌分布及原始名称写法 |
| [catalog_rules.py](catalog_rules.py) | 名称归一化和排除规则 |
| [validate_catalog.py](validate_catalog.py) | 标准库数据完整性检查程序 |
| [validation.json](validation.json) | 此发布文件的校验结果 |
| [checksums.sha256](checksums.sha256) | 本目录发布文件的SHA-256 |

## 字段与计数

- `entity_id`：根据规范化制造商与型号生成的稳定标识。
- `canonical_name`、`surface_forms`：来源中明确出现的型号及其名称写法。
- `type`：统一为`Product`。
- `manufacturer`：规范化制造商或品牌名称。
- `catalog_granularity`：产品页面型号、订货编号等原目录粒度。
- `catalog_categories`、`catalog_subcategories`、`packages`：可获得的器件分类及封装信息。
- `sources`：原始名称、制造商、来源URL、源行号或产品页面和核验层级。
- `mention_ids`、`document_ids`、`splits`：空数组；本资源按目录实体组织，与原文指称和实验划分分别管理。

不同来源的同一制造商与型号合并为一条实体，来源和已出现的别名保存在该记录中。名称大小写及单纯排版差异统一；型号中的实际连字符、小数点、斜线、`#`及订货后缀保留。真实不同的订货型号独立记录，产品系列与订货型号的粒度由`catalog_granularity`说明。

范围涵盖集成电路、离散半导体器件、光电器件及芯片式传感器等；401条封装功率半导体模块单列为`packaged_power_semiconductor_module`。开发板、完整电源转换模块、无线PCB模块、配件及身份冲突的来源记录按规则隔离。

## 来源与核验层级

来源包括[Texas Instruments](https://www.ti.com/product/sitemap-standard.xml)、[Analog Devices](https://www.analog.com/media/en/en-pdp-sitemap.xml)、[Infineon](https://www.infineon.com/en.sitemap.part-row-sitemap.xml)、[STMicroelectronics](https://www.st.com/content/st_com/sitemap-index.xml)、[Renesas](https://www.renesas.com/sitemap.xml)的官方索引，以及[yaqwsx/jlcparts](https://github.com/yaqwsx/jlcparts)和[nhansendev/LCSCPartSearch](https://github.com/nhansendev/LCSCPartSearch)发布的JLCPCB/LCSC目录快照。

`verification_level`区分两种来源依据：

| 值 | 含义 |
| --- | --- |
| `public_catalog_record_snapshot_verified` | 制造商和型号与保存的公开目录行相符 |
| `official_sitemap_url_only` | 型号来自官方产品索引路径；是否单独核对详情页见`individually_page_verified` |

同一JLCPCB/LCSC来源的两份镜像保留各自快照信息，不作为彼此独立的人工验证。原始全量目录快照未随包发布；来源清单保留可核查的URL与文件摘要，其中`snapshot_file`仅为相对的快照文件名。上游资料的权利与许可分别以发布方说明为准。

## 读取

```python
import gzip
import json

with gzip.open("resources/global_semiconductor_entities/entity_catalog.jsonl.gz", "rt", encoding="utf-8") as file:
    entity = json.loads(next(file))

print(entity["manufacturer"], entity["canonical_name"])
```

从仓库根目录执行完整性检查：

```bash
python resources/global_semiconductor_entities/validate_catalog.py resources/global_semiconductor_entities
```

该检查校验压缩与未压缩文件摘要、记录数量、唯一标识、制造商与型号组合、来源引用及保留字段。逐条来源依据与核验层级见`sources`。
