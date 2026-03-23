"""ChatOps Service - 智能对话运维"""
import logging
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class IntentClassifier:
    """意图分类器"""
    
    INTENTS = {
        "deploy": {
            "keywords": ["部署", "deploy", "上线", "release"],
            "description": "部署应用"
        },
        "rollback": {
            "keywords": ["回滚", "rollback", "撤销"],
            "description": "回滚版本"
        },
        "status": {
            "keywords": ["状态", "status", "查看", "健康"],
            "description": "查看状态"
        },
        "scale": {
            "keywords": ["扩容", "scale", "扩展", "实例"],
            "description": "扩缩容"
        },
        "logs": {
            "keywords": ["日志", "logs", "查看日志"],
            "description": "查看日志"
        },
        "restart": {
            "keywords": ["重启", "restart", "重新启动"],
            "description": "重启服务"
        },
        "scale_up": {
            "keywords": ["扩容", "增加实例", "scale up"],
            "description": "增加实例"
        },
        "scale_down": {
            "keywords": ["缩容", "减少实例", "scale down"],
            "description": "减少实例"
        },
    }
    
    def classify(self, text: str) -> str:
        """分类用户意图
        
        Args:
            text: 用户输入
            
        Returns:
            意图名称
        """
        text_lower = text.lower()
        
        # 优先匹配更具体的意图
        intent_scores = {}
        for intent, config in self.INTENTS.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword.lower() in text_lower:
                    score += 1
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return "unknown"
        
        # 返回得分最高的意图
        return max(intent_scores, key=intent_scores.get)
    
    def extract_params(self, text: str, intent: str) -> Dict:
        """提取意图参数
        
        Args:
            text: 用户输入
            intent: 已识别的意图
            
        Returns:
            参数字典
        """
        params: Dict = {}
        text_lower = text.lower()
        
        # 提取服务名（常见模式）
        import re
        service_match = re.search(r'(?:服务|应用|app|service)[\s:]*(\w+)', text_lower)
        if service_match:
            params["service"] = service_match.group(1)
        
        # 提取数量（用于扩缩容）
        if intent in ["scale_up", "scale_down", "scale"]:
            count_match = re.search(r'(\d+)', text)
            if count_match:
                params["count"] = int(count_match.group(1))
        
        # 提取版本号（用于部署/回滚）
        version_match = re.search(r'v?(\d+\.\d+)', text)
        if version_match and intent in ["deploy", "rollback"]:
            params["version"] = version_match.group(1)
        
        return params


class CommandExecutor:
    """命令执行器"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
    
    def register(self, intent: str, handler: Callable[[Dict], Dict]) -> None:
        """注册命令处理器
        
        Args:
            intent: 意图名称
            handler: 处理函数
        """
        self.handlers[intent] = handler
    
    def execute(self, intent: str, params: Dict) -> Dict:
        """执行命令
        
        Args:
            intent: 意图名称
            params: 参数
            
        Returns:
            执行结果
        """
        handler = self.handlers.get(intent)
        if handler:
            try:
                result = handler(params)
                logger.info(f"Executed {intent}: {result}")
                return result
            except Exception as e:
                logger.error(f"Execution failed for {intent}: {e}")
                return {
                    "action": intent,
                    "status": "error",
                    "message": f"执行失败: {str(e)}"
                }
        
        # 默认响应
        return {
            "action": intent,
            "status": "not_implemented",
            "message": f"Intent '{intent}' handler not registered"
        }


class ChatOpsService:
    """ChatOps 服务"""
    
    def __init__(self):
        self.classifier = IntentClassifier()
        self.executor = CommandExecutor()
        self._register_default_handlers()
        self.logger = logger
    
    def _register_default_handlers(self) -> None:
        """注册默认命令处理器"""
        
        def handle_deploy(params: Dict) -> Dict:
            return {
                "action": "deploy",
                "status": "success",
                "message": f"部署成功，服务: {params.get('service', 'unknown')}",
                "version": params.get("version", "latest")
            }
        
        def handle_rollback(params: Dict) -> Dict:
            return {
                "action": "rollback",
                "status": "success",
                "message": f"回滚成功，服务: {params.get('service', 'unknown')}",
                "version": params.get("version", "previous")
            }
        
        def handle_status(params: Dict) -> Dict:
            return {
                "action": "status",
                "status": "success",
                "message": f"服务状态正常: {params.get('service', 'all')}",
                "instances": 3,
                "health": "healthy"
            }
        
        def handle_scale(params: Dict) -> Dict:
            count = params.get("count", 2)
            return {
                "action": "scale",
                "status": "success",
                "message": f"扩缩容完成，目标实例数: {count}",
                "instances": count
            }
        
        def handle_restart(params: Dict) -> Dict:
            return {
                "action": "restart",
                "status": "success",
                "message": f"重启完成，服务: {params.get('service', 'unknown')}"
            }
        
        def handle_logs(params: Dict) -> Dict:
            return {
                "action": "logs",
                "status": "success",
                "message": "日志获取成功（示例）",
                "lines": ["[INFO] Application started", "[INFO] Server listening on port 8080"]
            }
        
        self.executor.register("deploy", handle_deploy)
        self.executor.register("rollback", handle_rollback)
        self.executor.register("status", handle_status)
        self.executor.register("scale", handle_scale)
        self.executor.register("scale_up", lambda p: handle_scale({**p, "count": p.get("count", 3)}))
        self.executor.register("scale_down", lambda p: handle_scale({**p, "count": p.get("count", 1)}))
        self.executor.register("restart", handle_restart)
        self.executor.register("logs", handle_logs)
    
    def process(self, message: str) -> Dict:
        """处理用户消息
        
        Args:
            message: 用户消息
            
        Returns:
            处理结果
        """
        intent = self.classifier.classify(message)
        params = self.classifier.extract_params(message, intent)
        result = self.executor.execute(intent, params)
        
        return {
            "intent": intent,
            "result": result,
            "message": result.get("message", "完成"),
            "params": params
        }
    
    def get_supported_intents(self) -> List[Dict]:
        """获取支持的意图列表"""
        return [
            {"intent": intent, "description": config["description"], "keywords": config["keywords"]}
            for intent, config in IntentClassifier.INTENTS.items()
        ]
