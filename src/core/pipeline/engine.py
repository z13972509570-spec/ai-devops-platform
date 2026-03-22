"""Pipeline Engine - DAG orchestration"""
import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Task:
    id: str
    name: str
    command: str
    deps: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING

@dataclass
class Pipeline:
    id: str
    name: str
    tasks: List[Task] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING

class PipelineEngine:
    """DAG Pipeline Engine"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.logger = logger
    
    def create_pipeline(self, name: str, tasks: List[Dict]) -> Pipeline:
        pipeline_id = f"pipeline_{len(self.pipelines) + 1}"
        task_list = [
            Task(id=f"t{i}", name=t.get("name", ""), command=t.get("command", ""), deps=t.get("deps", []))
            for i, t in enumerate(tasks)
        ]
        pipeline = Pipeline(id=pipeline_id, name=name, tasks=task_list)
        self.pipelines[pipeline_id] = pipeline
        self.logger.info(f"Created pipeline: {name}")
        return pipeline
    
    async def run(self, pipeline_id: str) -> Dict:
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return {"error": "Pipeline not found"}
        
        pipeline.status = TaskStatus.RUNNING
        results = {}
        
        for task in pipeline.tasks:
            if all(results.get(dep) for dep in task.deps):
                task.status = TaskStatus.SUCCESS
                results[task.id] = True
            else:
                task.status = TaskStatus.SKIPPED
                results[task.id] = False
        
        pipeline.status = TaskStatus.SUCCESS
        return {"pipeline_id": pipeline_id, "status": "completed"}
    
    def get_status(self, pipeline_id: str) -> Optional[Dict]:
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
        return {
            "id": pipeline.id,
            "name": pipeline.name,
            "status": pipeline.status.value,
            "tasks": [{"id": t.id, "name": t.name, "status": t.status.value} for t in pipeline.tasks]
        }
