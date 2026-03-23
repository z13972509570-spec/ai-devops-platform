"""Knowledge Service - 运维知识图谱服务"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Incident:
    """故障记录"""
    id: str
    title: str
    description: str
    symptoms: List[str] = field(default_factory=list)
    solutions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class KnowledgeNode:
    """知识图谱节点"""
    id: str
    type: str  # "symptom", "incident", "solution"
    data: Dict
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgeEdge:
    """知识图谱边"""
    from_id: str
    to_id: str
    relation: str  # "leads_to", "resolves", "causes"
    weight: float = 1.0


class KnowledgeGraph:
    """知识图谱"""
    
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
    
    def add_node(self, node: KnowledgeNode) -> None:
        """添加节点"""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: KnowledgeEdge) -> None:
        """添加边"""
        self.edges.append(edge)
        self.adjacency[edge.from_id].append(edge.to_id)
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """获取相邻节点"""
        return self.adjacency.get(node_id, [])
    
    def get_outgoing_edges(self, node_id: str) -> List[KnowledgeEdge]:
        """获取从指定节点出发的边"""
        return [e for e in self.edges if e.from_id == node_id]
    
    def search_nodes(self, query: str) -> List[KnowledgeNode]:
        """搜索节点"""
        results = []
        query_lower = query.lower()
        for node in self.nodes.values():
            if query_lower in str(node.data).lower():
                results.append(node)
        return results[:10]


class KnowledgeService:
    """运维知识服务"""
    
    def __init__(self):
        self.kg = KnowledgeGraph()
        self.incidents: List[Incident] = []
        self._init_sample_data()
        self.logger = logger
    
    def _init_sample_data(self) -> None:
        """初始化示例数据"""
        # 添加示例节点
        self.kg.add_node(KnowledgeNode(
            id="cpu_spike",
            type="symptom",
            data={"description": "CPU 使用率飙升", "threshold": "80%"}
        ))
        self.kg.add_node(KnowledgeNode(
            id="memory_leak",
            type="symptom",
            data={"description": "内存泄漏", "threshold": "90%"}
        ))
        self.kg.add_node(KnowledgeNode(
            id="oom_killer",
            type="incident",
            data={"description": "OOM 被内核终止"}
        ))
        self.kg.add_node(KnowledgeNode(
            id="pod_restart",
            type="incident",
            data={"description": "Pod 频繁重启"}
        ))
        self.kg.add_node(KnowledgeNode(
            id="restart_service",
            type="solution",
            data={"description": "重启服务"}
        ))
        self.kg.add_node(KnowledgeNode(
            id="increase_memory",
            type="solution",
            data={"description": "增加内存限制"}
        ))
        
        # 添加边：症状 -> 事件 -> 解决方案
        self.kg.add_edge(KnowledgeEdge("cpu_spike", "pod_restart", "leads_to"))
        self.kg.add_edge(KnowledgeEdge("memory_leak", "oom_killer", "leads_to"))
        self.kg.add_edge(KnowledgeEdge("pod_restart", "restart_service", "resolves"))
        self.kg.add_edge(KnowledgeEdge("oom_killer", "restart_service", "resolves"))
        self.kg.add_edge(KnowledgeEdge("memory_leak", "increase_memory", "resolves"))
        self.kg.add_edge(KnowledgeEdge("cpu_spike", "oom_killer", "leads_to"))
    
    def search(self, query: str) -> List[Dict]:
        """搜索知识
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的知识节点列表
        """
        results = []
        for node in self.kg.search_nodes(query):
            results.append({
                "id": node.id,
                "type": node.type,
                "data": node.data,
                "created_at": node.created_at.isoformat()
            })
        return results
    
    def get_recommendations(self, symptoms: List[str]) -> List[Dict]:
        """根据症状获取解决方案推荐
        
        Args:
            symptoms: 症状列表
            
        Returns:
            解决方案推荐列表
        """
        recommendations = []
        
        for symptom in symptoms:
            # 找到该症状相关的所有边（模糊匹配）
            symptom_node = None
            symptom_lower = symptom.lower()
            for node in self.kg.nodes.values():
                if node.type != "symptom":
                    continue
                # 检查症状词是否出现在节点描述中
                node_desc = str(node.data.get("description", "")).lower()
                # 匹配：输入的症状词是否在描述中，或者描述词是否在症状中
                if (symptom_lower in node_desc or
                    any(word in symptom_lower for word in node_desc.split())):
                    symptom_node = node
                    break
            
            if not symptom_node:
                continue
            
            # 查找症状导致的事件
            events = []
            for edge in self.kg.get_outgoing_edges(symptom_node.id):
                if edge.relation == "leads_to":
                    target = self.kg.nodes.get(edge.to_id)
                    if target:
                        events.append(target)
            
            # 查找解决事件的方法
            seen_solutions = set()
            for event in events:
                for edge in self.kg.get_outgoing_edges(event.id):
                    if edge.relation == "resolves":
                        solution = self.kg.nodes.get(edge.to_id)
                        if solution and solution.id not in seen_solutions:
                            seen_solutions.add(solution.id)
                            recommendations.append({
                                "symptom": symptom_node.data,
                                "incident": event.data,
                                "solution": solution.data,
                                "confidence": edge.weight
                            })
        
        return recommendations
    
    def add_incident(self, incident: Incident) -> None:
        """记录故障"""
        self.incidents.append(incident)
        self.logger.info(f"Incident recorded: {incident.title}")
    
    def get_incidents(self, limit: int = 10) -> List[Dict]:
        """获取故障历史"""
        return [
            {
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "symptoms": i.symptoms,
                "solutions": i.solutions,
                "created_at": i.created_at.isoformat(),
                "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None
            }
            for i in self.incidents[-limit:]
        ]
    
    def add_knowledge(self, node_type: str, data: Dict) -> str:
        """添加知识
        
        Args:
            node_type: 节点类型
            data: 节点数据
            
        Returns:
            节点 ID
        """
        node_id = f"{node_type}_{len(self.kg.nodes)}"
        self.kg.add_node(KnowledgeNode(id=node_id, type=node_type, data=data))
        return node_id
