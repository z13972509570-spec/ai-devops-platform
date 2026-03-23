"""Monitor Service - AI-powered monitoring"""
import logging
import statistics
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    id: str
    metric: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False


@dataclass
class AlertRule:
    name: str
    metric_name: str
    threshold: float
    operator: str  # "gt", "lt", "eq"
    severity: str
    enabled: bool = True


class MonitorService:
    """监控服务 - 指标收集、异常检测、告警通知"""
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        self.notification_handlers: List[Callable[[Alert], None]] = []
        self.logger = logger
    
    def record_metric(self, name: str, value: float, tags: Dict = None) -> Metric:
        """记录指标
        
        Args:
            name: 指标名称
            value: 指标值
            tags: 标签
            
        Returns:
            创建的 Metric 对象
        """
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.metrics.append(metric)
        return metric
    
    def get_metrics(self, name: str = None, limit: int = 100) -> List[Metric]:
        """获取指标历史
        
        Args:
            name: 指标名称过滤
            limit: 返回数量限制
            
        Returns:
            指标列表
        """
        metrics = self.metrics
        if name:
            metrics = [m for m in metrics if m.name == name]
        return metrics[-limit:]
    
    def add_alert_rule(self, rule: AlertRule) -> None:
        """添加告警规则"""
        self.alert_rules.append(rule)
        self.logger.info(f"Added alert rule: {rule.name}")
    
    def register_notification_handler(self, handler: Callable[[Alert], None]) -> None:
        """注册告警通知处理器
        
        Args:
            handler: 回调函数，接收 Alert 对象
        """
        self.notification_handlers.append(handler)
    
    def _notify(self, alert: Alert) -> None:
        """发送告警通知"""
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Notification handler failed: {e}")
    
    def detect_anomaly(self, metric_name: str, threshold: float = 2.0) -> List[Alert]:
        """基于 Z-score 检测异常
        
        Args:
            metric_name: 指标名称
            threshold: Z-score 阈值
            
        Returns:
            告警列表
        """
        alerts = []
        metric_values = [m.value for m in self.metrics if m.name == metric_name]
        
        if len(metric_values) < 10:
            return alerts
        
        mean = statistics.mean(metric_values)
        std = statistics.stdev(metric_values)
        
        for metric in self.metrics:
            if metric.name == metric_name and std > 0:
                z_score = abs((metric.value - mean) / std)
                if z_score > threshold:
                    severity = "critical" if z_score > 3 else "high" if z_score > 2.5 else "medium"
                    alert = Alert(
                        id=f"alert_{len(self.alerts)}_{metric_name}",
                        metric=metric_name,
                        severity=severity,
                        message=f"Anomaly detected: {metric.value:.2f} (z={z_score:.2f}, mean={mean:.2f})",
                        timestamp=metric.timestamp
                    )
                    alerts.append(alert)
                    self.alerts.append(alert)
                    self._notify(alert)
        
        return alerts
    
    def check_alert_rules(self, metric_name: str, value: float) -> List[Alert]:
        """根据规则检查是否触发告警
        
        Args:
            metric_name: 指标名称
            value: 当前值
            
        Returns:
            触发的告警列表
        """
        alerts = []
        
        for rule in self.alert_rules:
            if not rule.enabled or rule.metric_name != metric_name:
                continue
            
            triggered = False
            if rule.operator == "gt" and value > rule.threshold:
                triggered = True
            elif rule.operator == "lt" and value < rule.threshold:
                triggered = True
            elif rule.operator == "eq" and abs(value - rule.threshold) < 0.001:
                triggered = True
            
            if triggered:
                alert = Alert(
                    id=f"alert_{len(self.alerts)}_{rule.name}",
                    metric=metric_name,
                    severity=rule.severity,
                    message=f"Rule '{rule.name}' triggered: {value} {rule.operator} {rule.threshold}",
                    timestamp=datetime.now()
                )
                alerts.append(alert)
                self.alerts.append(alert)
                self._notify(alert)
        
        return alerts
    
    def get_alerts(self, resolved: bool = None, severity: str = None) -> List[Alert]:
        """获取告警列表
        
        Args:
            resolved: 按已解决状态过滤
            severity: 按严重级别过滤
            
        Returns:
            告警列表
        """
        alerts = self.alerts
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return alerts
    
    def resolve_alert(self, alert_id: str) -> bool:
        """标记告警为已解决
        
        Args:
            alert_id: 告警 ID
            
        Returns:
            是否成功
        """
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                self.logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    def get_statistics(self, metric_name: str, limit: int = 100) -> Dict:
        """获取指标统计信息
        
        Args:
            metric_name: 指标名称
            limit: 采样数量
            
        Returns:
            统计信息字典
        """
        values = [m.value for m in self.get_metrics(metric_name, limit)]
        if not values:
            return {}
        
        return {
            "name": metric_name,
            "count": len(values),
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values),
            "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 1 else values[0]
        }
