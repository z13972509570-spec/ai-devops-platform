import statistics

class AnomalyDetector:
    """Detect anomalies in time series"""
    
    def __init__(self, threshold: float = 2.5):
        self.threshold = threshold
    
    def detect(self, values: List[float]) -> List[tuple[int, float]]:
        """Detect anomalies using z-score"""
        if len(values) < 10:
            return []
    
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        
        anomalies = []
        for i, v in enumerate(values):
            if std > 0:
                ze_score = abs((v - mean) / std)
                if ze_score > self.threshold:
                    anomalies.append((i, v))
    
        return anomalies
