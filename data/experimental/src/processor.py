# ICKG 知识图谱采集系统 - 数据处理器
# v5.0

"""
数据处理模块

负责实体管理、关系管理、数据保存等核心功能。
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 实体类型
ENTITY_TYPES = [
    "Company",    # 企业
    "Person",     # 人物
    "Product",    # 产品/工艺
    "Patent",     # 专利
    "Policy",     # 政策
    "Industry",   # 行业
    "Report"      # 报告
]

# 关系类型
RELATION_TYPES = [
    # 企业-企业
    "collaboratesWith",  # 合作
    "investsIn",         # 投资
    "acquires",          # 收购
    "competesWith",      # 竞争
    "suppliesTo",        # 供应
    "manufactures",      # 制造
    # 企业-人物
    "leadsCompany",      # 领导企业
    "foundedCompany",    # 创办企业
    "employedBy",        # 受雇于
    # 企业-产品
    "produces",          # 生产
    "develops",          # 开发
    "usesProduct",       # 使用
    # 其他
    "inIndustry",        # 属于行业
    "affectedByPolicy",  # 受政策影响
    "ownsPatent",        # 拥有专利
    "basedOn",           # 基于
    "usedIn"             # 用于
]


@dataclass
class EntityRecord:
    """实体记录"""
    entity_id: int
    mention: str
    entity_type: str
    description: str = ""
    aliases: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        if not self.aliases:
            self.aliases = {self.mention}
        self.aliases.add(self.mention)


@dataclass
class RelationRecord:
    """关系记录 (五元组)"""
    head: str
    relation: str
    tail: str
    time: str = ""
    evidence_url: str = ""
    
    def to_dict(self) -> dict:
        return {
            "head": self.head,
            "relation": self.relation,
            "tail": self.tail,
            "time": self.time,
            "evidence_url": self.evidence_url
        }


class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        self.entities: Dict[str, EntityRecord] = {}  # mention -> EntityRecord
        self.relations: List[RelationRecord] = []
        self.training_data: List[dict] = []
        self.entity_id_counter = 0
    
    # ==================== 实体管理 ====================
    
    def add_entity(
        self,
        name: str,
        entity_type: str,
        description: str = "",
        aliases: Set[str] = None
    ) -> int:
        """添加实体
        
        Args:
            name: 实体名称
            entity_type: 实体类型
            description: 描述
            aliases: 别名集合
            
        Returns:
            实体ID
        """
        # 规范化名称
        name = self.normalize_entity_name(name)
        if not name:
            return -1
        
        # 检查是否已存在
        if name in self.entities:
            return self.entities[name].entity_id
        
        # 创建新实体
        self.entity_id_counter += 1
        entity = EntityRecord(
            entity_id=self.entity_id_counter,
            mention=name,
            entity_type=entity_type,
            description=description,
            aliases=aliases or {name}
        )
        
        self.entities[name] = entity
        return entity.entity_id
    
    def find_entity(self, name: str) -> Optional[EntityRecord]:
        """查找实体"""
        name = self.normalize_entity_name(name)
        return self.entities.get(name)
    
    def get_entity_by_mention(self, mention: str) -> Optional[EntityRecord]:
        """根据 mention 查找实体"""
        mention = self.normalize_entity_name(mention)
        return self.find_entity(mention)
    
    def get_entities_by_type(self, entity_type: str) -> List[EntityRecord]:
        """获取指定类型的所有实体"""
        return [e for e in self.entities.values() if e.entity_type == entity_type]
    
    # ==================== 关系管理 ====================
    
    def add_relation(
        self,
        head: str,
        relation: str,
        tail: str,
        time: str = "",
        evidence_url: str = ""
    ) -> bool:
        """添加关系
        
        Args:
            head: 头实体
            relation: 关系类型
            tail: 尾实体
            time: 时间
            evidence_url: 证据链接
            
        Returns:
            是否添加成功
        """
        # 验证关系类型
        if relation not in RELATION_TYPES:
            logger.warning(f"未知关系类型: {relation}")
            return False
        
        # 规范化实体名称
        head_norm = self.normalize_entity_name(head)
        tail_norm = self.normalize_entity_name(tail)
        
        if not head_norm or not tail_norm:
            return False
        
        # 格式化时间
        time = self.parse_time(time)
        
        # 创建关系
        relation_record = RelationRecord(
            head=head_norm,
            relation=relation,
            tail=tail_norm,
            time=time,
            evidence_url=evidence_url
        )
        
        # 检查重复关系
        for existing in self.relations:
            if (existing.head == head_norm and 
                existing.relation == relation and 
                existing.tail == tail_norm and
                existing.time == time):
                return False
        
        self.relations.append(relation_record)
        return True
    
    def get_relations_by_head(self, head: str) -> List[RelationRecord]:
        """获取指定头实体的所有关系"""
        head_norm = self.normalize_entity_name(head)
        return [r for r in self.relations if r.head == head_norm]
    
    def get_relations_by_tail(self, tail: str) -> List[RelationRecord]:
        """获取指定尾实体的所有关系"""
        tail_norm = self.normalize_entity_name(tail)
        return [r for r in self.relations if r.tail == tail_norm]
    
    # ==================== 训练数据管理 ====================
    
    def add_training_data(
        self,
        news_id: str,
        text: str,
        entities: List[dict],
        time: str = "",
        source: str = ""
    ):
        """添加训练数据
        
        Args:
            news_id: 新闻ID
            text: 原始新闻文本
            entities: 实体列表 [{"start": 0, "end": 4, "mention": "实体名", "type": "Company"}, ...]
            time: 时间 (可选)
            source: 原文链接 (可选)
        """
        self.training_data.append({
            "id": news_id,
            "text": text,
            "entities": entities,
            "time": time,
            "source": source
        })
    
    # ==================== 规范化 ====================
    
    @staticmethod
    def normalize_entity_name(name: str) -> str:
        """规范化实体名称"""
        if not name:
            return ""
        # 移除首尾空格
        name = name.strip()
        # 移除括号内容，如 "中芯国际 (SMIC)"
        name = re.sub(r'\s*\([^)]*\)\s*', '', name)
        # 移除多余空格
        name = re.sub(r'\s+', ' ', name)
        return name.strip()
    
    @staticmethod
    def parse_time(time_str: str) -> str:
        """解析并格式化时间"""
        if not time_str:
            return ""
        
        time_str = time_str.strip()
        
        # 匹配 "2024年3月28日"
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', time_str)
        if match:
            return f"{match.group(1)}年{match.group(2)}月{match.group(3)}日"
        
        # 匹配 "2024年3月"
        match = re.search(r'(\d{4})年(\d{1,2})月', time_str)
        if match:
            return f"{match.group(1)}年{match.group(2)}月"
        
        # 匹配 "2024年"
        match = re.search(r'(\d{4})年', time_str)
        if match:
            return f"{match.group(1)}年"
        
        # 匹配 "2024-Q1" 或 "2024年Q1"
        match = re.search(r'(\d{4})[年\s]*Q([1-4])', time_str, re.IGNORECASE)
        if match:
            return f"{match.group(1)}年Q{match.group(2)}季度"
        
        return time_str
    
    # ==================== 保存文件 ====================
    
    def save_entity2id(self, filepath: Path):
        """保存 entity2id.txt (TSV格式)"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for entity in sorted(self.entities.values(), key=lambda x: x.entity_id):
                f.write(f"{entity.mention}\t{entity.entity_id}\n")
        logger.info(f"✓ 已保存 {len(self.entities)} 个实体到 {filepath}")
    
    def save_id2entity(self, filepath: Path):
        """保存 id2entity.json"""
        data = {}
        for entity in self.entities.values():
            data[str(entity.entity_id)] = {
                "id": entity.entity_id,
                "mention": entity.mention,
                "type": entity.entity_type,
                "description": entity.description,
                "aliases": sorted(list(entity.aliases))
            }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ 已保存实体详情到 {filepath}")
    
    def save_relations(self, filepath: Path):
        """保存 relations.jsonl (五元组)"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for rel in self.relations:
                f.write(json.dumps(rel.to_dict(), ensure_ascii=False) + '\n')
        logger.info(f"✓ 已保存 {len(self.relations)} 条关系到 {filepath}")
    
    def save_training_data(self, filepath: Path):
        """保存 training_data.jsonl (训练数据格式)
        
        输出格式:
        {
            "id": "news_0001",
            "text": "2023年，A公司与B公司签署合作协议...",
            "entities": [
                {"start": 6, "end": 8, "mention": "A公司", "type": "Company"},
                {"start": 9, "end": 11, "mention": "B公司", "type": "Company"}
            ],
            "time": "2023-07-15",
            "source": "https://..."
        }
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in self.training_data:
                record = {
                    'id': item.get('id', ''),
                    'text': item.get('text', ''),
                    'entities': item.get('entities', []),
                    'time': item.get('time', ''),
                    'source': item.get('source', '')
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        logger.info(f"✓ 已保存 {len(self.training_data)} 条训练数据到 {filepath}")
    
    def save_stats(self, filepath: Path, duration: float):
        """保存 collection_stats.json"""
        # 统计实体类型
        entity_types = {}
        for entity in self.entities.values():
            entity_types[entity.entity_type] = entity_types.get(entity.entity_type, 0) + 1
        
        # 统计关系类型
        relation_types = {}
        for rel in self.relations:
            relation_types[rel.relation] = relation_types.get(rel.relation, 0) + 1
        
        stats = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "entities": {
                "total": len(self.entities),
                "by_type": entity_types
            },
            "relations": {
                "total": len(self.relations),
                "by_type": relation_types
            },
            "training_data": {
                "total": len(self.training_data)
            },
            "summary": {
                "avg_relations_per_entity": round(
                    len(self.relations) / len(self.entities) if self.entities else 0, 2
                ),
                "coverage": f"{len(self.entities)} 个实体，{len(self.relations)} 条关系"
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ 已保存采集统计到 {filepath}")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "entities": len(self.entities),
            "relations": len(self.relations),
            "training_data": len(self.training_data)
        }
    
    def clear(self):
        """清空所有数据"""
        self.entities.clear()
        self.relations.clear()
        self.training_data.clear()
        self.entity_id_counter = 0

