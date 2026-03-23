"""Log Analyzer - 日志模式分析"""
import re
from typing import Dict, List
from collections import Counter


class LogAnalyzer:
    """分析日志中的模式"""
    
    def __init__(self):
        """初始化分析器"""
        self.patterns = {
            "error": r"(?i)(ERROR|错误|失败)",
            "warning": r"(?i)(WARN|WARNING|警告)",
            "exception": r"(?i)(Exception|异常)",
            "timeout": r"(?i)(timeout|TIMEOUT|超时)",
            "fatal": r"(?i)(FATAL|CRITICAL|严重)",
        }
        self.analyzer_logger = None
    
    def analyze(self, logs: List[str]) -> Dict:
        """分析日志
        
        Args:
            logs: 日志行列表
            
        Returns:
            分析结果字典
        """
        results = {
            "total": len(logs),
            "patterns": {},
            "top_errors": []
        }
        
        # 统计每种模式匹配数
        for name, pattern in self.patterns.items():
            matches = [log for log in logs if re.search(pattern, log)]
            results["patterns"][name] = len(matches)
        
        # 统计错误行
        error_lines = [
            log for log in logs
            if re.search(self.patterns["error"], log)
        ]
        error_counts = Counter(error_lines)
        results["top_errors"] = [
            {"line": line, "count": count}
            for line, count in error_counts.most_common(5)
        ]
        
        return results
    
    def add_pattern(self, name: str, pattern: str) -> None:
        """添加自定义日志模式
        
        Args:
            name: 模式名称
            pattern: 正则表达式
        """
        self.patterns[name] = pattern
    
    def detect_anomalies(self, logs: List[str]) -> List[Dict]:
        """检测日志中的异常模式
        
        Args:
            logs: 日志列表
            
        Returns:
            异常事件列表
        """
        anomalies = []
        
        for i, log in enumerate(logs):
            # 检测错误
            if re.search(self.patterns["error"], log):
                anomalies.append({
                    "index": i,
                    "type": "error",
                    "message": log.strip()
                })
            # 检测严重错误
            elif re.search(self.patterns["fatal"], log):
                anomalies.append({
                    "index": i,
                    "type": "fatal",
                    "message": log.strip()
                })
        
        return anomalies
