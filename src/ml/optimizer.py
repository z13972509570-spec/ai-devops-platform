"""Pipeline Optimizer - Pipeline 执行优化"""
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class PipelineOptimizer:
    """优化 Pipeline 任务执行顺序"""
    
    def __init__(self):
        self.logger = logger
    
    def optimize(self, tasks: List[Dict]) -> List[Dict]:
        """优化任务顺序，基于依赖关系进行拓扑排序
        
        Args:
            tasks: 任务列表，每项包含 id, name, deps 等
            
        Returns:
            优化后的任务列表（拓扑排序）
        """
        optimized = []
        remaining = tasks.copy()
        completed: Set[str] = set()
        
        max_iterations = len(tasks) * len(tasks)  # 防止死循环
        iteration = 0
        
        while remaining and iteration < max_iterations:
            iteration += 1
            made_progress = False
            
            for task in remaining[:]:  # 复制列表避免遍历中修改问题
                task_id = task.get("id", "")
                deps = set(task.get("deps", []))
                
                # 检查依赖是否都已完成
                if deps <= completed:
                    optimized.append(task)
                    completed.add(task_id)
                    remaining.remove(task)
                    made_progress = True
                    self.logger.debug(f"Task {task_id} added to optimized list")
            
            if not made_progress:
                # 无法取得进展，记录并退出
                self.logger.warning(
                    f"Cannot optimize further. "
                    f"Remaining tasks: {[t.get('id') for t in remaining]}"
                )
                # 将剩余任务追加到结果（即使有循环依赖）
                optimized.extend(remaining)
                break
        
        return optimized
    
    def validate_dependencies(self, tasks: List[Dict]) -> Dict:
        """验证任务依赖是否有效
        
        Args:
            tasks: 任务列表
            
        Returns:
            验证结果，包含 valid, errors
        """
        task_ids = {task.get("id") for task in tasks}
        errors = []
        
        for task in tasks:
            task_id = task.get("id")
            deps = task.get("deps", [])
            
            for dep in deps:
                if dep not in task_ids:
                    errors.append({
                        "task": task_id,
                        "error": f"Missing dependency: {dep}"
                    })
                
                # 检测自循环
                if dep == task_id:
                    errors.append({
                        "task": task_id,
                        "error": f"Self-dependency: {task_id}"
                    })
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def estimate_parallelism(self, tasks: List[Dict]) -> int:
        """估算可并行执行的任务数
        
        Args:
            tasks: 任务列表
            
        Returns:
            最大并行度
        """
        if not tasks:
            return 0
        
        task_map = {task.get("id"): task for task in tasks}
        levels: Dict[str, int] = {}
        
        def get_level(task_id: str) -> int:
            if task_id in levels:
                return levels[task_id]
            
            task = task_map.get(task_id)
            if not task:
                levels[task_id] = 0
                return 0
            
            deps = task.get("deps", [])
            if not deps:
                levels[task_id] = 0
                return 0
            
            max_dep_level = max(get_level(dep) for dep in deps)
            levels[task_id] = max_dep_level + 1
            return levels[task_id]
        
        # 计算每层的任务数
        level_counts: Dict[int, int] = {}
        for task in tasks:
            level = get_level(task.get("id", ""))
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return max(level_counts.values()) if level_counts else 1
