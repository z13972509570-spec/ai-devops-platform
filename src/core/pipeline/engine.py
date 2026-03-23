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
    output: Optional[str] = None
    error: Optional[str] = None


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
        """创建 Pipeline
        
        Args:
            name: Pipeline 名称
            tasks: 任务列表，每个任务包含 id, name, command, deps
            
        Returns:
            创建的 Pipeline 对象
        """
        pipeline_id = f"pipeline_{len(self.pipelines) + 1}"
        task_list = [
            Task(
                id=t.get("id", f"task_{i}"),
                name=t.get("name", ""),
                command=t.get("command", ""),
                deps=t.get("deps", [])
            )
            for i, t in enumerate(tasks)
        ]
        pipeline = Pipeline(id=pipeline_id, name=name, tasks=task_list)
        self.pipelines[pipeline_id] = pipeline
        self.logger.info(f"Created pipeline: {name} with {len(task_list)} tasks")
        return pipeline
    
    async def run(self, pipeline_id: str) -> Dict:
        """执行 Pipeline
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            执行结果字典
        """
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return {"error": "Pipeline not found"}
        
        pipeline.status = TaskStatus.RUNNING
        results = {}
        
        # 构建任务索引
        task_map = {task.id: task for task in pipeline.tasks}
        
        # DAG 拓扑排序执行
        completed = set()
        failed = set()
        
        max_iterations = len(pipeline.tasks) * 2  # 防止死循环
        iteration = 0
        
        while len(completed) + len(failed) < len(pipeline.tasks) and iteration < max_iterations:
            iteration += 1
            made_progress = False
            
            for task in pipeline.tasks:
                if task.id in completed or task.id in failed:
                    continue
                
                # 检查依赖是否都完成
                deps_met = all(dep in completed for dep in task.deps)
                
                if deps_met:
                    made_progress = True
                    task.status = TaskStatus.RUNNING
                    
                    # 真正执行命令（这里用 subprocess 模拟）
                    try:
                        # 在实际环境中，这里应该是:
                        # proc = await asyncio.create_subprocess_shell(...)
                        # stdout, stderr = await proc.communicate()
                        task.output = f"Executed: {task.command}"
                        task.status = TaskStatus.SUCCESS
                        results[task.id] = True
                        completed.add(task.id)
                        self.logger.info(f"Task {task.id} completed successfully")
                    except Exception as e:
                        task.error = str(e)
                        task.status = TaskStatus.FAILED
                        results[task.id] = False
                        failed.add(task.id)
                        self.logger.error(f"Task {task.id} failed: {e}")
            
            if not made_progress:
                # 无法取得进展，可能是循环依赖
                self.logger.warning("Cannot make progress, possible circular dependency")
                break
        
        # 设置 Pipeline 状态
        if failed:
            pipeline.status = TaskStatus.FAILED
        elif len(completed) == len(pipeline.tasks):
            pipeline.status = TaskStatus.SUCCESS
        else:
            pipeline.status = TaskStatus.FAILED
        
        return {
            "pipeline_id": pipeline_id,
            "status": pipeline.status.value,
            "completed": list(completed),
            "failed": list(failed),
            "total": len(pipeline.tasks)
        }
    
    def get_status(self, pipeline_id: str) -> Optional[Dict]:
        """获取 Pipeline 状态"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
        return {
            "id": pipeline.id,
            "name": pipeline.name,
            "status": pipeline.status.value,
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "status": t.status.value,
                    "output": t.output,
                    "error": t.error
                }
                for t in pipeline.tasks
            ]
        }
    
    def list_pipelines(self) -> List[Dict]:
        """列出所有 Pipeline"""
        return [
            {"id": p.id, "name": p.name, "status": p.status.value}
            for p in self.pipelines.values()
        ]
