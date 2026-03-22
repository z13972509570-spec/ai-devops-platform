"""Knowledge Service"""
import logging
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Incident:
    id: str
    title: str
    description: str
    symptoms: List[str]
    solutions: List[str]

class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
    def add_node(self, id: str, type: str, data: Dict):
        self.nodes[id] = {"type": type, "data": data}
    def add_edge(self, from_id: str, to_id: str, relation: str):
        self.edges.append({"from": from_id, "to": to_id, "relation": relation})

class KnowledgeService:
    def __init__(self):
        self.kg = KnowledgeGraph()
        self.incidents: List[Incident] = []
        self._init_sample_data()
    def _init_sample_data(self):
        self.kg.add_node("cpu_spike", "symptom", {"description": "CPU飙升"})
        self.kg.add_node("oom", "incident", {"description": "OOM错误"})
        self.kg.add_node("restart", "solution", {"description": "重启服务"})
        self.kg.add_edge("cpu_spike", "oom", "leads_to")
        self.kg.add_edge("restart", "oom", "resolves")
    def search(self, query: str) -> List[Dict]:
        results = []
        for node_id, node in self.kg.nodes.items():
            if query.lower() in str(node.get("data", {})).lower():
                results.append({"id": node_id, **node})
        return results[:10]
    def get_recommendations(self, symptoms: List[str]) -> List[Dict]:
        recommendations = []
        for edge in self.kg.edges:
            if edge["relation"] == "resolves":
                symptom_node = self.kg.nodes.get(edge["from"])
                if symptom_node:
                    recommendations.append({"symptom": symptom_node["data"]})
        return recommendations
