"""AI DevOps Platform - 集成测试"""
import asyncio
from src.core.pipeline.engine import PipelineEngine, TaskStatus
from src.core.monitor.service import MonitorService, AlertRule
from src.core.chatops.service import ChatOpsService
from src.core.knowledge.service import KnowledgeService, Incident
from src.ml.detector import AnomalyDetector
from src.ml.analyzer import LogAnalyzer
from src.ml.optimizer import PipelineOptimizer


def test_pipeline_engine():
    """测试 Pipeline 引擎"""
    print("\n=== Testing Pipeline Engine ===")
    
    engine = PipelineEngine()
    
    # 创建 Pipeline
    tasks = [
        {"id": "build", "name": "Build", "command": "make build", "deps": []},
        {"id": "test", "name": "Test", "command": "make test", "deps": ["build"]},
        {"id": "deploy", "name": "Deploy", "command": "make deploy", "deps": ["test"]},
    ]
    
    pipeline = engine.create_pipeline("CI/CD Pipeline", tasks)
    print(f"✓ Created pipeline: {pipeline.id}")
    
    # 运行 Pipeline
    result = asyncio.run(engine.run(pipeline.id))
    print(f"✓ Pipeline execution result: {result}")
    
    # 获取状态
    status = engine.get_status(pipeline.id)
    print(f"✓ Pipeline status: {status['status']}")
    assert status['status'] == 'success'


def test_monitor_service():
    """测试监控服务"""
    print("\n=== Testing Monitor Service ===")
    
    monitor = MonitorService()
    
    # 记录指标
    for i in range(20):
        monitor.record_metric("cpu_usage", 50 + i * 2)
    print("✓ Recorded 20 metrics")
    
    # 检测异常
    alerts = monitor.detect_anomaly("cpu_usage", threshold=2.0)
    print(f"✓ Detected {len(alerts)} anomalies")
    
    # 添加告警规则
    rule = AlertRule(
        name="High CPU",
        metric_name="cpu_usage",
        threshold=80,
        operator="gt",
        severity="high"
    )
    monitor.add_alert_rule(rule)
    print("✓ Added alert rule")
    
    # 检查规则
    alerts = monitor.check_alert_rules("cpu_usage", 85)
    print(f"✓ Rule check triggered {len(alerts)} alerts")
    
    # 获取统计
    stats = monitor.get_statistics("cpu_usage")
    print(f"✓ Statistics: mean={stats['mean']:.2f}, std={stats['std']:.2f}")


def test_chatops_service():
    """测试 ChatOps 服务"""
    print("\n=== Testing ChatOps Service ===")
    
    chatops = ChatOpsService()
    
    # 测试各种意图
    test_messages = [
        "部署 myapp 服务",
        "查看状态",
        "扩容到 5 个实例",
        "重启服务",
        "查看日志",
    ]
    
    for msg in test_messages:
        result = chatops.process(msg)
        print(f"✓ '{msg}' -> intent: {result['intent']}, status: {result['result']['status']}")
    
    # 获取支持的意图
    intents = chatops.get_supported_intents()
    print(f"✓ Supported intents: {len(intents)}")


def test_knowledge_service():
    """测试知识服务"""
    print("\n=== Testing Knowledge Service ===")
    
    knowledge = KnowledgeService()
    
    # 搜索知识
    results = knowledge.search("CPU")
    print(f"✓ Search results: {len(results)} nodes found")
    
    # 获取推荐
    recommendations = knowledge.get_recommendations(["CPU 飙升"])
    print(f"✓ Got {len(recommendations)} recommendations")
    for rec in recommendations:
        print(f"  - {rec['solution']['description']}")
    
    # 记录故障
    incident = Incident(
        id="inc_001",
        title="Pod 频繁重启",
        description="生产环境 Pod 频繁重启",
        symptoms=["CPU 飙升", "内存泄漏"],
        solutions=["重启服务", "增加内存"]
    )
    knowledge.add_incident(incident)
    print("✓ Recorded incident")
    
    # 获取故障历史
    incidents = knowledge.get_incidents()
    print(f"✓ Got {len(incidents)} incidents")


def test_anomaly_detector():
    """测试异常检测器"""
    print("\n=== Testing Anomaly Detector ===")
    
    detector = AnomalyDetector(threshold=2.5)
    
    # 生成测试数据（大部分正常，少数异常）
    values = [50 + i for i in range(20)]  # 正常数据
    values.extend([150, 160])  # 异常数据
    
    anomalies = detector.detect(values)
    print(f"✓ Detected {len(anomalies)} anomalies")
    
    # 获取统计
    stats = detector.get_statistics(values)
    print(f"✓ Statistics: mean={stats['mean']:.2f}, std={stats['std']:.2f}")


def test_log_analyzer():
    """测试日志分析器"""
    print("\n=== Testing Log Analyzer ===")
    
    analyzer = LogAnalyzer()
    
    # 生成测试日志
    logs = [
        "[INFO] Application started",
        "[ERROR] Connection failed",
        "[WARNING] High memory usage",
        "[ERROR] Timeout occurred",
        "[FATAL] Critical error",
    ]
    
    result = analyzer.analyze(logs)
    print(f"✓ Analyzed {result['total']} logs")
    print(f"  - Errors: {result['patterns']['error']}")
    print(f"  - Warnings: {result['patterns']['warning']}")
    
    # 检测异常
    anomalies = analyzer.detect_anomalies(logs)
    print(f"✓ Detected {len(anomalies)} anomalies")


def test_pipeline_optimizer():
    """测试 Pipeline 优化器"""
    print("\n=== Testing Pipeline Optimizer ===")
    
    optimizer = PipelineOptimizer()
    
    # 创建任务
    tasks = [
        {"id": "build", "name": "Build", "deps": []},
        {"id": "test", "name": "Test", "deps": ["build"]},
        {"id": "deploy", "name": "Deploy", "deps": ["test"]},
        {"id": "smoke_test", "name": "Smoke Test", "deps": ["deploy"]},
    ]
    
    # 优化
    optimized = optimizer.optimize(tasks)
    print(f"✓ Optimized {len(optimized)} tasks")
    for task in optimized:
        print(f"  - {task['id']}: deps={task['deps']}")
    
    # 验证依赖
    validation = optimizer.validate_dependencies(tasks)
    print(f"✓ Validation: valid={validation['valid']}")
    
    # 估算并行度
    parallelism = optimizer.estimate_parallelism(tasks)
    print(f"✓ Estimated parallelism: {parallelism}")


if __name__ == "__main__":
    print("🚀 AI DevOps Platform - Integration Tests")
    
    try:
        test_pipeline_engine()
        test_monitor_service()
        test_chatops_service()
        test_knowledge_service()
        test_anomaly_detector()
        test_log_analyzer()
        test_pipeline_optimizer()
        
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
