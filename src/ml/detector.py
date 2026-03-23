"""Anomaly Detector - 基于统计的异常检测"""
import statistics
from typing import List, Tuple


class AnomalyDetector:
    """检测时间序列中的异常值（基于 Z-score）"""
    
    def __init__(self, threshold: float = 2.5):
        """初始化检测器
        
        Args:
            threshold: Z-score 阈值，超过此值视为异常
        """
        self.threshold = threshold
        self.history: List[List[float]] = []
    
    def detect(self, values: List[float]) -> List[Tuple[int, float]]:
        """检测异常值
        
        Args:
            values: 数值列表
            
        Returns:
            异常值列表，每项为 (索引, 值)
        """
        if len(values) < 10:
            return []
        
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        
        anomalies = []
        for i, v in enumerate(values):
            if std > 0:
                z_score = abs((v - mean) / std)
                if z_score > self.threshold:
                    anomalies.append((i, v))
        
        # 记录历史
        self.history.append(values)
        
        return anomalies
    
    def detect_incremental(self, values: List[float], baseline: List[float]) -> List[Tuple[int, float]]:
        """增量检测：使用 baseline 作为基准检测新数据中的异常
        
        Args:
            values: 待检测的新数据
            baseline: 历史基准数据
            
        Returns:
            异常值列表
        """
        if len(baseline) < 10:
            return self.detect(values)
        
        mean = statistics.mean(baseline)
        std = statistics.stdev(baseline)
        
        anomalies = []
        for i, v in enumerate(values):
            if std > 0:
                z_score = abs((v - mean) / std)
                if z_score > self.threshold:
                    anomalies.append((i, v))
        
        return anomalies
    
    def get_statistics(self, values: List[float]) -> dict:
        """获取统计信息
        
        Returns:
            包含 mean, std, min, max, median 的字典
        """
        if not values:
            return {}
        
        return {
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values),
            "count": len(values)
        }
