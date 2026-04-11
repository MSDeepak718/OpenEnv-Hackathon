"""
Medium incident tasks — require correlation of 2-3 signals.
May need 2 steps to gather additional evidence.
"""
import random

MEDIUM_TASK_ID = "medium_incident"
MEDIUM_GRADER = "tasks.grader.grade_medium"

MEDIUM_TASKS = [
    {
        "id": "medium_incident",
        "difficulty": "medium",
        "incident_id": "INC-2001",
        "timestamp": "2025-03-15T10:30:00Z",
        "severity_indicator": "P2",
        "title": "API Latency Spike — Slow Database Queries",
        "description": "API response times have increased 10x over the past hour. Users reporting timeouts. No recent deployments.",
        "affected_services": ["api-gateway", "order-service", "postgres-primary"],
        "metrics_by_step": {
            1: {"api_latency_p99_ms": [120, 200, 800, 3500], "db_query_duration_ms": [15, 50, 400, 2800], "active_db_connections": [20, 30, 80, 150]},
            2: {"slow_queries_per_min": [0, 2, 15, 45], "table_row_counts": [100000, 500000, 2000000, 5000000], "index_usage_pct": [95, 80, 40, 5]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-15T09:45:00Z", "level": "WARN", "service": "order-service", "message": "Query execution time 2800ms for SELECT * FROM orders WHERE status='pending' — no index found"},
                {"timestamp": "2025-03-15T10:00:00Z", "level": "WARN", "service": "postgres-primary", "message": "Long-running query detected: sequential scan on orders table (5M rows)"},
                {"timestamp": "2025-03-15T10:15:00Z", "level": "ERROR", "service": "api-gateway", "message": "Upstream timeout: order-service response time > 5s"},
            ],
            2: [
                {"timestamp": "2025-03-15T10:30:00Z", "level": "WARN", "service": "postgres-primary", "message": "pg_stat_user_tables: orders table — seq_scan=4521, idx_scan=12, last vacuum: never"},
                {"timestamp": "2025-03-15T10:31:00Z", "level": "INFO", "service": "postgres-primary", "message": "Table bloat detected: orders 5M rows, dead tuples 2.1M (42%)"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "APILatencyHigh", "severity": "warning", "source": "prometheus", "message": "api-gateway p99 latency > 3000ms", "fired_at": "2025-03-15T10:20:00Z"},
            ],
            2: [
                {"name": "DBConnectionPoolExhausted", "severity": "critical", "source": "prometheus", "message": "Active DB connections > 140 (limit: 150)", "fired_at": "2025-03-15T10:35:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-15T09:30:00Z", "event": "Gradual latency increase began", "source": "prometheus"},
                {"timestamp": "2025-03-15T10:15:00Z", "event": "First user-reported timeouts", "source": "support"},
            ],
            2: [
                {"timestamp": "2025-03-15T10:30:00Z", "event": "Database analysis reveals missing index and table bloat", "source": "DBA-tooling"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "application",
            "remediation": "update_config",
            "key_diagnosis_terms": ["query", "slow", "index", "database", "scan", "bloat", "missing index"],
            "harmful_remediations": ["restart_service"],
        },
        "grader": MEDIUM_GRADER,
    },
    {
        "id": "medium_incident",
        "difficulty": "medium",
        "incident_id": "INC-2002",
        "timestamp": "2025-03-16T15:00:00Z",
        "severity_indicator": "P2",
        "title": "Memory Leak in User Service — Gradual Degradation",
        "description": "User service pods are slowly consuming more memory over the past 6 hours. Response times degrading. No crashes yet but memory usage approaching limits.",
        "affected_services": ["user-service"],
        "metrics_by_step": {
            1: {"memory_usage_mb": [256, 512, 1024, 1800], "gc_pause_ms": [5, 15, 80, 250], "response_time_p50_ms": [20, 30, 80, 200]},
            2: {"heap_objects_count": [50000, 120000, 500000, 1200000], "memory_growth_mb_per_hour": [0, 50, 120, 200], "open_file_descriptors": [100, 200, 800, 1500]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-16T09:00:00Z", "level": "INFO", "service": "user-service", "message": "Service started — memory baseline: 256MB"},
                {"timestamp": "2025-03-16T12:00:00Z", "level": "WARN", "service": "user-service", "message": "GC pressure increasing — pause times > 80ms"},
                {"timestamp": "2025-03-16T14:50:00Z", "level": "WARN", "service": "user-service", "message": "Memory usage 1800MB approaching 2048MB limit — GC pause > 250ms"},
            ],
            2: [
                {"timestamp": "2025-03-16T15:00:00Z", "level": "WARN", "service": "user-service", "message": "Heap analysis: 1.2M objects retained — UserSessionCache growing unbounded"},
                {"timestamp": "2025-03-16T15:01:00Z", "level": "INFO", "service": "profiler", "message": "Top memory consumer: UserSessionCache (68% of heap) — sessions never evicted"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "MemoryUsageHigh", "severity": "warning", "source": "prometheus", "message": "user-service memory > 85% of limit", "fired_at": "2025-03-16T14:30:00Z"},
            ],
            2: [
                {"name": "GCPressureCritical", "severity": "warning", "source": "jvm-exporter", "message": "GC pause time > 200ms", "fired_at": "2025-03-16T15:00:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-16T09:00:00Z", "event": "Service started after last deploy", "source": "kubernetes"},
                {"timestamp": "2025-03-16T14:30:00Z", "event": "Memory usage alert fired", "source": "prometheus"},
            ],
            2: [
                {"timestamp": "2025-03-16T15:00:00Z", "event": "Heap dump analysis identifies leaking cache", "source": "profiler"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "application",
            "remediation": "restart_service",
            "key_diagnosis_terms": ["memory", "leak", "heap", "cache", "GC", "growing", "unbounded"],
            "harmful_remediations": ["rollback_deploy"],
        },
        "grader": MEDIUM_GRADER,
    },
    {
        "id": "medium_incident",
        "difficulty": "medium",
        "incident_id": "INC-2003",
        "timestamp": "2025-03-17T18:30:00Z",
        "severity_indicator": "P3",
        "title": "Rate Limiter Misconfigured — Blocking Legitimate Traffic",
        "description": "After a config change to tighten rate limits, legitimate API users are being rate-limited. 30% of requests returning 429 Too Many Requests.",
        "affected_services": ["api-gateway", "rate-limiter"],
        "metrics_by_step": {
            1: {"http_429_rate_pct": [0.5, 5, 15, 30], "legitimate_requests_blocked": [10, 200, 800, 2000], "total_requests_per_sec": [500, 500, 500, 500]},
            2: {"rate_limit_config_requests_per_min": [1000, 1000, 50, 50], "unique_ips_affected": [5, 50, 300, 500], "config_change_audit": [1, 1, 1, 1]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-17T17:30:00Z", "level": "INFO", "service": "config-manager", "message": "Rate limit config updated: max_requests_per_minute changed from 1000 to 50"},
                {"timestamp": "2025-03-17T18:00:00Z", "level": "WARN", "service": "api-gateway", "message": "Rate limit exceeded for user agent_id=12345 — 429 returned"},
                {"timestamp": "2025-03-17T18:20:00Z", "level": "ERROR", "service": "api-gateway", "message": "2000 requests blocked by rate limiter in last 30 minutes — appears to be legitimate traffic"},
            ],
            2: [
                {"timestamp": "2025-03-17T18:30:00Z", "level": "INFO", "service": "config-manager", "message": "Config audit: rate_limit changed by user=admin at 17:30 — previous value: 1000 req/min, new value: 50 req/min"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "High429Rate", "severity": "warning", "source": "prometheus", "message": "HTTP 429 rate > 25%", "fired_at": "2025-03-17T18:15:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-17T17:30:00Z", "event": "Rate limit configuration changed", "source": "config-manager"},
                {"timestamp": "2025-03-17T18:00:00Z", "event": "429 responses increasing", "source": "api-gateway"},
            ],
        },
        "expected": {
            "triage_priority": "P3",
            "root_cause_category": "configuration",
            "remediation": "update_config",
            "key_diagnosis_terms": ["rate limit", "config", "429", "misconfigured", "throttle", "blocked"],
            "harmful_remediations": ["restart_service", "block_ip"],
        },
        "grader": MEDIUM_GRADER,
    },
    {
        "id": "medium_incident",
        "difficulty": "medium",
        "incident_id": "INC-2004",
        "timestamp": "2025-03-18T07:00:00Z",
        "severity_indicator": "P2",
        "title": "Kafka Consumer Lag — Message Processing Delayed",
        "description": "Order processing is delayed by several minutes. Kafka consumer group for order-processor has growing lag across all partitions.",
        "affected_services": ["order-processor", "kafka-cluster", "order-service"],
        "metrics_by_step": {
            1: {"consumer_lag_messages": [100, 5000, 50000, 200000], "messages_processed_per_sec": [500, 200, 50, 10], "order_processing_delay_sec": [1, 30, 180, 600]},
            2: {"consumer_instances": [5, 5, 2, 2], "cpu_usage_per_consumer_pct": [40, 60, 95, 99], "partition_count": [10, 10, 10, 10]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-18T05:00:00Z", "level": "INFO", "service": "kubernetes", "message": "Scaling event: order-processor scaled from 5 to 2 replicas (HPA — low CPU during night)"},
                {"timestamp": "2025-03-18T06:30:00Z", "level": "WARN", "service": "order-processor", "message": "Consumer lag growing on partitions 0-9 — current lag: 50,000 messages"},
                {"timestamp": "2025-03-18T06:55:00Z", "level": "ERROR", "service": "order-service", "message": "Order #ORD-7823 processing delay: 8 minutes — SLA breach"},
            ],
            2: [
                {"timestamp": "2025-03-18T07:00:00Z", "level": "WARN", "service": "kubernetes", "message": "HPA not scaling up order-processor: CPU threshold 80% but target metric is 95%+ (scaling cooldown: 10min)"},
                {"timestamp": "2025-03-18T07:01:00Z", "level": "INFO", "service": "order-processor", "message": "Only 2 consumers for 10 partitions — each consumer handling 5 partitions at near-max CPU"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "KafkaConsumerLag", "severity": "warning", "source": "kafka-exporter", "message": "Consumer lag > 100,000 messages for order-processor group", "fired_at": "2025-03-18T06:45:00Z"},
            ],
            2: [
                {"name": "OrderProcessingDelay", "severity": "critical", "source": "prometheus", "message": "Order processing delay > 5 min — SLA breach", "fired_at": "2025-03-18T07:00:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-18T05:00:00Z", "event": "HPA scaled order-processor from 5 to 2", "source": "kubernetes"},
                {"timestamp": "2025-03-18T06:30:00Z", "event": "Consumer lag growing significantly", "source": "kafka-exporter"},
            ],
            2: [
                {"timestamp": "2025-03-18T07:00:00Z", "event": "HPA cooldown preventing scale-up", "source": "kubernetes"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "infrastructure",
            "remediation": "scale_up",
            "key_diagnosis_terms": ["Kafka", "consumer", "lag", "scale", "HPA", "partition", "under-provisioned"],
            "harmful_remediations": ["restart_service"],
        },
        "grader": MEDIUM_GRADER,
    },
    {
        "id": "medium_incident",
        "difficulty": "medium",
        "incident_id": "INC-2005",
        "timestamp": "2025-03-19T13:45:00Z",
        "severity_indicator": "P3",
        "title": "Cron Job Failure — Stale Data in Reports",
        "description": "Daily data aggregation cron job has been silently failing for 3 days. Reports showing stale data. No alerts were configured for this job.",
        "affected_services": ["analytics-service", "reporting-dashboard"],
        "metrics_by_step": {
            1: {"report_data_freshness_hours": [1, 24, 48, 72], "cron_job_last_success_hours_ago": [1, 24, 48, 72], "dashboard_queries_per_hour": [200, 200, 200, 200]},
            2: {"cron_exit_codes_last_5_runs": [0, 1, 1, 1], "disk_usage_analytics_pct": [60, 75, 90, 98], "etl_rows_processed": [1000000, 0, 0, 0]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-17T02:00:00Z", "level": "INFO", "service": "cron-scheduler", "message": "Starting daily-aggregation job"},
                {"timestamp": "2025-03-17T02:01:00Z", "level": "ERROR", "service": "analytics-etl", "message": "ETL failed: disk write error on /data/analytics — insufficient space"},
                {"timestamp": "2025-03-18T02:01:00Z", "level": "ERROR", "service": "analytics-etl", "message": "ETL failed: disk write error on /data/analytics — insufficient space"},
                {"timestamp": "2025-03-19T02:01:00Z", "level": "ERROR", "service": "analytics-etl", "message": "ETL failed: disk write error on /data/analytics — insufficient space"},
            ],
            2: [
                {"timestamp": "2025-03-19T13:45:00Z", "level": "INFO", "service": "analytics-etl", "message": "Disk usage on /data/analytics: 98% — temp files from failed ETL runs accumulating"},
                {"timestamp": "2025-03-19T13:46:00Z", "level": "WARN", "service": "cron-scheduler", "message": "No alerting rule configured for daily-aggregation job failure"},
            ],
        },
        "alerts_by_step": {
            1: [],
            2: [
                {"name": "StaleReportData", "severity": "warning", "source": "manual-check", "message": "Report data is 72 hours old", "fired_at": "2025-03-19T13:45:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-16T02:00:00Z", "event": "Last successful ETL run", "source": "cron-scheduler"},
                {"timestamp": "2025-03-17T02:01:00Z", "event": "ETL began failing — disk full", "source": "analytics-etl"},
                {"timestamp": "2025-03-19T13:00:00Z", "event": "User reported stale dashboard data", "source": "support"},
            ],
        },
        "expected": {
            "triage_priority": "P3",
            "root_cause_category": "infrastructure",
            "remediation": "scale_up",
            "key_diagnosis_terms": ["cron", "ETL", "disk", "stale", "failed", "aggregation", "space"],
            "harmful_remediations": ["restart_service"],
        },
        "grader": MEDIUM_GRADER,
    },
    {
        "id": "medium_incident",
        "difficulty": "medium",
        "incident_id": "INC-2006",
        "timestamp": "2025-03-20T20:00:00Z",
        "severity_indicator": "P2",
        "title": "Circuit Breaker Tripped — Downstream Service Cascading Failures",
        "description": "Payment service circuit breaker tripped, causing all checkout flows to fail. The breaker opened due to high error rates from a downstream fraud-check service.",
        "affected_services": ["payment-service", "fraud-check-service", "checkout-flow"],
        "metrics_by_step": {
            1: {"circuit_breaker_state": [0, 0, 1, 1], "checkout_success_rate_pct": [99, 95, 20, 0], "fraud_check_error_rate_pct": [1, 15, 60, 85]},
            2: {"fraud_check_latency_ms": [50, 200, 3000, 9999], "fraud_check_connection_pool": [10, 10, 10, 0], "fraud_check_thread_dump": [0, 0, 5, 10]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-20T19:30:00Z", "level": "WARN", "service": "fraud-check-service", "message": "External fraud API latency > 3000ms — responses timing out"},
                {"timestamp": "2025-03-20T19:45:00Z", "level": "ERROR", "service": "payment-service", "message": "Circuit breaker OPEN for fraud-check — 85% error rate exceeded threshold (50%)"},
                {"timestamp": "2025-03-20T19:46:00Z", "level": "ERROR", "service": "checkout-flow", "message": "Checkout failed: payment-service returning 503 — circuit breaker open"},
            ],
            2: [
                {"timestamp": "2025-03-20T20:00:00Z", "level": "WARN", "service": "fraud-check-service", "message": "Thread pool exhausted — 10 threads blocked waiting on external fraud API"},
                {"timestamp": "2025-03-20T20:01:00Z", "level": "INFO", "service": "fraud-check-service", "message": "External fraud API (FraudGuard Inc.) status: degraded — investigating high latency"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "CircuitBreakerOpen", "severity": "critical", "source": "payment-service", "message": "Circuit breaker tripped for fraud-check dependency", "fired_at": "2025-03-20T19:45:00Z"},
            ],
            2: [
                {"name": "CheckoutCompletelyDown", "severity": "critical", "source": "prometheus", "message": "Checkout success rate 0%", "fired_at": "2025-03-20T20:00:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-20T19:30:00Z", "event": "Fraud check latency spiked", "source": "fraud-check-service"},
                {"timestamp": "2025-03-20T19:45:00Z", "event": "Circuit breaker opened", "source": "payment-service"},
            ],
            2: [
                {"timestamp": "2025-03-20T20:00:00Z", "event": "Root cause: external FraudGuard API degraded", "source": "fraud-check-service"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "external",
            "remediation": "failover",
            "key_diagnosis_terms": ["circuit breaker", "fraud", "external", "downstream", "timeout", "cascade"],
            "harmful_remediations": ["restart_service", "rollback_deploy"],
        },
        "grader": MEDIUM_GRADER,
    },
    {
        "id": "medium_incident",
        "difficulty": "medium",
        "incident_id": "INC-2007",
        "timestamp": "2025-03-21T11:30:00Z",
        "severity_indicator": "P3",
        "title": "Feature Flag Rollout Issue — 500 Errors for Flag-On Users",
        "description": "A new feature flag (new-checkout-v2) was enabled for 10% of users. Those users are experiencing 500 errors. The remaining 90% are unaffected.",
        "affected_services": ["checkout-service", "feature-flag-service"],
        "metrics_by_step": {
            1: {"error_rate_flagged_users_pct": [0, 20, 60, 100], "error_rate_unflagged_users_pct": [0.5, 0.5, 0.5, 0.5], "flagged_user_percentage": [0, 5, 10, 10]},
            2: {"checkout_v2_null_pointer_count": [0, 5, 50, 200], "checkout_v1_errors": [0, 0, 0, 0], "flag_rollout_history": [0, 5, 10, 10]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-21T10:00:00Z", "level": "INFO", "service": "feature-flag-service", "message": "Feature flag 'new-checkout-v2' enabled for 10% of users"},
                {"timestamp": "2025-03-21T10:30:00Z", "level": "ERROR", "service": "checkout-service", "message": "NullReferenceError in CheckoutV2Handler.processPayment() — paymentMethod is null"},
                {"timestamp": "2025-03-21T11:00:00Z", "level": "ERROR", "service": "checkout-service", "message": "500 Internal Server Error for user_id=789 (flag: new-checkout-v2=true)"},
            ],
            2: [
                {"timestamp": "2025-03-21T11:30:00Z", "level": "INFO", "service": "checkout-service", "message": "Error analysis: all 500 errors correlate with new-checkout-v2=true users only"},
                {"timestamp": "2025-03-21T11:31:00Z", "level": "WARN", "service": "checkout-service", "message": "CheckoutV2Handler lacks null-check for paymentMethod field (regression from v1)"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "ErrorRateSpike", "severity": "warning", "source": "prometheus", "message": "checkout-service error rate increase for subset of users", "fired_at": "2025-03-21T11:00:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-21T10:00:00Z", "event": "Feature flag new-checkout-v2 enabled (10%)", "source": "feature-flag-service"},
                {"timestamp": "2025-03-21T10:30:00Z", "event": "First 500 errors from flagged users", "source": "checkout-service"},
            ],
        },
        "expected": {
            "triage_priority": "P3",
            "root_cause_category": "application",
            "remediation": "update_config",
            "key_diagnosis_terms": ["feature flag", "rollout", "bug", "null", "v2", "regression"],
            "harmful_remediations": ["restart_service", "block_ip"],
        },
        "grader": MEDIUM_GRADER,
    },
    {
        "id": "medium_incident",
        "difficulty": "medium",
        "incident_id": "INC-2008",
        "timestamp": "2025-03-22T04:15:00Z",
        "severity_indicator": "P2",
        "title": "Container Image Pull Failures — New Nodes Can't Start Pods",
        "description": "Kubernetes cluster auto-scaled and added new nodes, but pods on new nodes fail to start because container images can't be pulled from the private registry.",
        "affected_services": ["kubernetes", "container-registry", "api-gateway", "order-service"],
        "metrics_by_step": {
            1: {"pod_pending_count": [0, 5, 15, 25], "image_pull_failures": [0, 5, 15, 25], "node_count": [5, 7, 10, 10]},
            2: {"registry_auth_failures": [0, 5, 15, 25], "image_pull_secret_expiry_hours": [72, 48, 24, 0], "new_nodes_with_valid_secrets": [0, 0, 0, 0]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-22T03:00:00Z", "level": "INFO", "service": "cluster-autoscaler", "message": "Scaling up: adding 5 nodes to handle increased load"},
                {"timestamp": "2025-03-22T03:10:00Z", "level": "ERROR", "service": "kubelet", "message": "Failed to pull image registry.example.com/api-gateway:v2.13 — 401 Unauthorized"},
                {"timestamp": "2025-03-22T03:15:00Z", "level": "ERROR", "service": "kubelet", "message": "ErrImagePull: 25 pods stuck in ImagePullBackOff on new nodes"},
            ],
            2: [
                {"timestamp": "2025-03-22T04:15:00Z", "level": "WARN", "service": "kubernetes", "message": "Image pull secret 'registry-creds' in namespace 'production' expired 6 hours ago"},
                {"timestamp": "2025-03-22T04:16:00Z", "level": "INFO", "service": "kubernetes", "message": "Existing nodes still have cached images — only new nodes affected by expired secret"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "PodsPending", "severity": "warning", "source": "kubernetes", "message": "25 pods in Pending/ImagePullBackOff state", "fired_at": "2025-03-22T03:20:00Z"},
            ],
            2: [
                {"name": "ImagePullSecretExpired", "severity": "critical", "source": "kubernetes", "message": "Registry credentials expired", "fired_at": "2025-03-22T04:15:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-22T03:00:00Z", "event": "Cluster scaled up with 5 new nodes", "source": "cluster-autoscaler"},
                {"timestamp": "2025-03-22T03:10:00Z", "event": "Image pull failures on new nodes", "source": "kubelet"},
            ],
            2: [
                {"timestamp": "2025-03-22T04:15:00Z", "event": "Root cause: registry secret expired", "source": "kubernetes"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "configuration",
            "remediation": "update_config",
            "key_diagnosis_terms": ["image pull", "registry", "secret", "expired", "credentials", "auth", "401"],
            "harmful_remediations": ["restart_service", "rollback_deploy"],
        },
        "grader": MEDIUM_GRADER,
    },
]


MEDIUM_TASK_METADATA = {
    "id": MEDIUM_TASK_ID,
    "name": "Medium Incident Triage",
    "difficulty": "medium",
    "description": "Correlate multiple signals to diagnose incidents — slow queries, memory leaks, misconfigurations, cascading failures.",
    "grader": MEDIUM_GRADER,
    "num_variants": len(MEDIUM_TASKS),
}


def get_medium_task():
    return random.choice(MEDIUM_TASKS)
