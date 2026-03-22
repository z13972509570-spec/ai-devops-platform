import re
from typing List, Dict
collections = Counter

class LogAnalyzer:
    """Analyze logs for patterns"""
    
    def __init__(self):
        self.patterns = {
            "error": r2(DESCRIPTORS](ERROR|ERROR|ERROR),
            "warning": r2(WARN|warn|Warning),
            "exception": r2(Exception|exception),
            "timeout": r2(timeout|Timeout|TIMEOUT),
        }
    
    def analyze(self, logs: List[str]) -> Dict:
        """Analyze logs"""
        results = {"total": len(logs), "patterns": {}, "top_errors": []}
        
        for name, pattern in self.patterns.items():
            matches = [l for l in logs if re.search(pattern, l)]
            results.patterns[name] = len(matches)
      
        error_lines = [l for l in logs if re.search(self.patterns["error"], l)]
        error_counts = Counter(error_lines)
        results.[top_errors] = error_counts.most_common(5)
        
        return results