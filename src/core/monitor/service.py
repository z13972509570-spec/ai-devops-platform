"""Monitor Service - AI-powered monitoring"""
import logging
import statistics
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]

@dataclass
class Alert:
    id: str
    metric: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False

class MonitorService:
    def __init__(self):
        self.metrics: List[Metric] = []
        self.alerts: List[Alert] = []
        self.logger = logger
    
    def record_metric(self, name: str, value: float, tags: Dict = None) -> Metric:
        metric = Metric(name=name, value=value, timestamp=datetime.now(), tags=tags or {})
        self.metrics.append(metric)
        return metric
    
    def get_metrics(self, name: str = None, limit: int = 100) -> List[Metric]:
        metrics = self.metrics
        if name:
            metrics = [m for m in metrics if m.name == name]
        return metrics[-limit:]
    
    def detect_anomaly(self, metric_name: str, threshold: float = 2.0) -> List[Alert]:
        alerts = []
        metric_values = [m.value for m in self.metrics if m.name == metric_name]
        if len(metric_values) < 10:
            return alerts
        mean = statistics.mean(metric_values)
        std = statistics.stdev(metric_values)
        for metric in self.metrics:
            if metric.name == metric_name:
                z_score = abs((metric.value - mean) / std) if std > 0 else 0
                if z_score > threshold:
                    alert = Alert(
                        id=f"alert_{len(self.alerts)}",
                        metric=metric_name,
                        severity="high" if z_score > 3 else "medium",
                        message=f"Anomaly: {metric.value} (z={z_score:.2f})",
                        timestamp=metric.timestamp
                    )
                    alerts.append(alert)
                    self.alerts.append(alert)
        return alerts
    
    def get_alerts(self, resolved: bool = None) -> List[Alert]:
        if resolved is not None:
            return [a for a in self.alerts if a.resolved == resolved]
        return self.alerts
