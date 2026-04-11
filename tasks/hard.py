"""
Hard incident tasks — misleading signals, cascading failures, security events.
Require 2-3 steps, careful evidence-gathering, and precise remediation.
"""
import random

HARD_TASK_ID = "hard_incident"
HARD_GRADER = "tasks.grader.grade_hard"

HARD_TASKS = [
    {
        "id": "hard_incident",
        "difficulty": "hard",
        "incident_id": "INC-3001",
        "timestamp": "2025-03-15T02:00:00Z",
        "severity_indicator": "P1",
        "title": "DDoS Attack Masking Unauthorized Database Access",
        "description": "Massive traffic spike detected across all frontend services. Appears to be a volumetric DDoS. However, security team noticed unusual database query patterns during the attack window.",
        "affected_services": ["api-gateway", "web-frontend", "postgres-primary", "waf"],
        "metrics_by_step": {
            1: {"requests_per_sec": [2000, 5000, 50000, 150000], "bandwidth_gbps": [0.5, 1.0, 8.0, 25.0], "error_rate_pct": [1, 5, 30, 60]},
            2: {"unique_source_ips": [5000, 8000, 120000, 300000], "waf_blocked_requests_pct": [2, 10, 60, 80], "api_latency_p99_ms": [100, 500, 5000, 9999]},
            3: {"db_unusual_queries_per_min": [0, 2, 15, 40], "db_data_exfil_mb": [0, 0, 50, 200], "auth_bypass_attempts": [0, 0, 5, 20]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-15T01:30:00Z", "level": "WARN", "service": "waf", "message": "Traffic anomaly detected — 150,000 req/sec (normal: 2,000)"},
                {"timestamp": "2025-03-15T01:35:00Z", "level": "ERROR", "service": "api-gateway", "message": "Connection pool exhausted — dropping 60% of requests"},
                {"timestamp": "2025-03-15T01:40:00Z", "level": "WARN", "service": "waf", "message": "DDoS pattern detected: SYN flood from 300K unique IPs"},
            ],
            2: [
                {"timestamp": "2025-03-15T01:45:00Z", "level": "INFO", "service": "waf", "message": "WAF rate limiting activated — blocking 80% of traffic"},
                {"timestamp": "2025-03-15T01:50:00Z", "level": "WARN", "service": "security-audit", "message": "Anomalous DB query pattern: SELECT * FROM users WHERE role='admin' — source IP: internal service"},
            ],
            3: [
                {"timestamp": "2025-03-15T01:55:00Z", "level": "ERROR", "service": "security-audit", "message": "SQL injection detected via compromised API endpoint: /api/v1/search?q=' UNION SELECT * FROM users--"},
                {"timestamp": "2025-03-15T02:00:00Z", "level": "FATAL", "service": "security-audit", "message": "Data exfiltration detected: 200MB of user data extracted through /api/v1/export endpoint during DDoS cover"},
                {"timestamp": "2025-03-15T02:01:00Z", "level": "ERROR", "service": "postgres-primary", "message": "Unusual bulk SELECT on users, payment_methods, addresses tables — 40 queries/min from compromised service account"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "DDoSDetected", "severity": "critical", "source": "waf", "message": "Volumetric DDoS attack in progress", "fired_at": "2025-03-15T01:35:00Z"},
            ],
            2: [
                {"name": "WAFRateLimiting", "severity": "warning", "source": "waf", "message": "WAF rate limiting active — 80% traffic blocked", "fired_at": "2025-03-15T01:45:00Z"},
            ],
            3: [
                {"name": "SQLInjectionDetected", "severity": "critical", "source": "security-audit", "message": "SQL injection via /api/v1/search", "fired_at": "2025-03-15T01:55:00Z"},
                {"name": "DataExfiltration", "severity": "critical", "source": "security-audit", "message": "200MB unauthorized data access detected", "fired_at": "2025-03-15T02:00:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-15T01:30:00Z", "event": "Traffic spike began", "source": "waf"},
                {"timestamp": "2025-03-15T01:35:00Z", "event": "DDoS confirmed", "source": "waf"},
            ],
            2: [
                {"timestamp": "2025-03-15T01:45:00Z", "event": "WAF mitigation activated", "source": "waf"},
                {"timestamp": "2025-03-15T01:50:00Z", "event": "Anomalous DB queries detected", "source": "security-audit"},
            ],
            3: [
                {"timestamp": "2025-03-15T01:55:00Z", "event": "SQL injection identified", "source": "security-audit"},
                {"timestamp": "2025-03-15T02:00:00Z", "event": "Data exfiltration confirmed", "source": "security-audit"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "security",
            "remediation": "block_ip",
            "key_diagnosis_terms": ["DDoS", "cover", "SQL injection", "exfiltration", "breach", "security", "compromised"],
            "harmful_remediations": ["restart_service", "monitor"],
        },
        "grader": HARD_GRADER,
    },
    {
        "id": "hard_incident",
        "difficulty": "hard",
        "incident_id": "INC-3002",
        "timestamp": "2025-03-16T06:00:00Z",
        "severity_indicator": "P1",
        "title": "Cascading Failures from Shared Redis Dependency",
        "description": "Multiple services failing simultaneously — order-service, inventory-service, and notification-service all reporting errors. No single deployment or config change correlates with the failures.",
        "affected_services": ["order-service", "inventory-service", "notification-service", "redis-cluster"],
        "metrics_by_step": {
            1: {"order_service_error_rate": [2, 15, 45, 80], "inventory_service_error_rate": [1, 10, 40, 75], "notification_service_error_rate": [0, 5, 30, 60]},
            2: {"redis_cluster_memory_pct": [70, 85, 95, 99], "redis_eviction_rate": [0, 100, 5000, 20000], "redis_connections": [1000, 1200, 1500, 1800]},
            3: {"redis_node_3_status": [1, 1, 0, 0], "cluster_slots_ok": [16384, 16384, 11000, 11000], "cache_miss_rate_pct": [5, 20, 60, 95]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-16T05:00:00Z", "level": "ERROR", "service": "order-service", "message": "Cache read failed: CLUSTERDOWN The cluster is down"},
                {"timestamp": "2025-03-16T05:05:00Z", "level": "ERROR", "service": "inventory-service", "message": "Redis CLUSTERDOWN — falling back to database (slow path)"},
                {"timestamp": "2025-03-16T05:10:00Z", "level": "ERROR", "service": "notification-service", "message": "Failed to dequeue notification: Redis cluster unavailable"},
            ],
            2: [
                {"timestamp": "2025-03-16T05:30:00Z", "level": "WARN", "service": "redis-cluster", "message": "Node redis-node-3: memory at 99% — evicting keys aggressively"},
                {"timestamp": "2025-03-16T05:35:00Z", "level": "ERROR", "service": "redis-cluster", "message": "Node redis-node-3: maxmemory reached, all writes rejected"},
            ],
            3: [
                {"timestamp": "2025-03-16T05:45:00Z", "level": "FATAL", "service": "redis-cluster", "message": "Node redis-node-3 unresponsive — cluster marking slots 11000-16383 as FAIL"},
                {"timestamp": "2025-03-16T05:50:00Z", "level": "ERROR", "service": "redis-cluster", "message": "Cluster partition: 5384 slots without master — cluster enters CLUSTERDOWN state"},
                {"timestamp": "2025-03-16T06:00:00Z", "level": "WARN", "service": "redis-cluster", "message": "Root cause: redis-node-3 had no memory limit increase after data growth — hot key 'session:global_counter' consuming 40% of node memory"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "MultiServiceFailure", "severity": "critical", "source": "prometheus", "message": "3 services with error rate > 40%", "fired_at": "2025-03-16T05:15:00Z"},
            ],
            2: [
                {"name": "RedisMemoryCritical", "severity": "critical", "source": "redis-exporter", "message": "redis-node-3 memory at 99%", "fired_at": "2025-03-16T05:30:00Z"},
            ],
            3: [
                {"name": "RedisClusterDown", "severity": "critical", "source": "redis-cluster", "message": "Redis cluster entered CLUSTERDOWN state", "fired_at": "2025-03-16T05:50:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-16T05:00:00Z", "event": "Multiple services began failing", "source": "prometheus"},
            ],
            2: [
                {"timestamp": "2025-03-16T05:30:00Z", "event": "Redis node-3 memory critical", "source": "redis-exporter"},
            ],
            3: [
                {"timestamp": "2025-03-16T05:50:00Z", "event": "Redis cluster entered CLUSTERDOWN", "source": "redis-cluster"},
                {"timestamp": "2025-03-16T06:00:00Z", "event": "Hot key identified as root cause", "source": "redis-cluster"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "infrastructure",
            "remediation": "failover",
            "key_diagnosis_terms": ["Redis", "cluster", "shared", "dependency", "cascade", "node", "memory", "hot key"],
            "harmful_remediations": ["rollback_deploy"],
        },
        "grader": HARD_GRADER,
    },
    {
        "id": "hard_incident",
        "difficulty": "hard",
        "incident_id": "INC-3003",
        "timestamp": "2025-03-17T14:00:00Z",
        "severity_indicator": "P2",
        "title": "Intermittent Network Partition Between AZs",
        "description": "Users in US-West experiencing sporadic failures. Some requests succeed, others timeout. The issue appears random — no clear pattern in which endpoints fail.",
        "affected_services": ["api-gateway-us-west", "database-replica-us-west", "service-mesh"],
        "metrics_by_step": {
            1: {"us_west_success_rate_pct": [95, 85, 70, 55], "us_east_success_rate_pct": [99, 99, 99, 99], "cross_az_latency_ms": [5, 50, 500, 9999]},
            2: {"packet_loss_az_a_to_b_pct": [0, 2, 15, 30], "tcp_retransmissions_per_sec": [10, 100, 1000, 5000], "service_mesh_connection_resets": [5, 50, 500, 2000]},
            3: {"bgp_route_changes": [0, 0, 5, 12], "network_interface_errors": [0, 50, 500, 2000], "az_b_switch_crc_errors": [0, 100, 5000, 20000]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-17T13:00:00Z", "level": "WARN", "service": "api-gateway-us-west", "message": "Intermittent 502 errors — upstream connection reset by peer"},
                {"timestamp": "2025-03-17T13:30:00Z", "level": "ERROR", "service": "database-replica-us-west", "message": "Replication lag: 45 seconds — intermittent connectivity to primary"},
            ],
            2: [
                {"timestamp": "2025-03-17T13:45:00Z", "level": "WARN", "service": "service-mesh", "message": "Envoy proxy health checks failing for 25% of cross-AZ endpoints"},
                {"timestamp": "2025-03-17T13:50:00Z", "level": "ERROR", "service": "network-monitor", "message": "Packet loss between AZ-A and AZ-B: 30% — TCP retransmissions spiking"},
            ],
            3: [
                {"timestamp": "2025-03-17T13:55:00Z", "level": "ERROR", "service": "network-monitor", "message": "BGP route flapping detected: 12 route changes in 10 minutes between AZ-A and AZ-B"},
                {"timestamp": "2025-03-17T14:00:00Z", "level": "FATAL", "service": "network-monitor", "message": "Root cause: faulty network switch in AZ-B (tor-switch-42) — CRC errors 20,000/sec indicating hardware failure"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "USWestDegradation", "severity": "warning", "source": "prometheus", "message": "US-West success rate < 60%", "fired_at": "2025-03-17T13:30:00Z"},
            ],
            2: [
                {"name": "CrossAZPacketLoss", "severity": "critical", "source": "network-monitor", "message": "30% packet loss between AZ-A and AZ-B", "fired_at": "2025-03-17T13:50:00Z"},
            ],
            3: [
                {"name": "NetworkHardwareFailure", "severity": "critical", "source": "network-monitor", "message": "Switch tor-switch-42 hardware failure — CRC errors", "fired_at": "2025-03-17T14:00:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-17T13:00:00Z", "event": "Intermittent failures in US-West", "source": "api-gateway"},
            ],
            2: [
                {"timestamp": "2025-03-17T13:50:00Z", "event": "Cross-AZ packet loss confirmed", "source": "network-monitor"},
            ],
            3: [
                {"timestamp": "2025-03-17T14:00:00Z", "event": "Faulty switch identified in AZ-B", "source": "network-monitor"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "network",
            "remediation": "failover",
            "key_diagnosis_terms": ["network", "partition", "packet loss", "switch", "AZ", "hardware", "intermittent"],
            "harmful_remediations": ["restart_service", "rollback_deploy"],
        },
        "grader": HARD_GRADER,
    },
    {
        "id": "hard_incident",
        "difficulty": "hard",
        "incident_id": "INC-3004",
        "timestamp": "2025-03-18T09:00:00Z",
        "severity_indicator": "P1",
        "title": "Cryptominer Deployed via Compromised CI/CD Pipeline",
        "description": "Unusual CPU usage across production nodes. Performance degraded but no obvious application errors. Recent deployments look normal in CI/CD logs.",
        "affected_services": ["kubernetes-workers", "ci-cd-pipeline", "all-services"],
        "metrics_by_step": {
            1: {"node_cpu_usage_pct": [45, 60, 85, 95], "node_cpu_steal_pct": [0, 5, 15, 30], "application_throughput_pct_of_normal": [100, 85, 60, 40]},
            2: {"unknown_process_cpu_pct": [0, 10, 30, 45], "network_outbound_mb_per_sec": [10, 15, 30, 50], "process_count_anomaly": [0, 2, 5, 8]},
            3: {"crypto_mining_pool_connections": [0, 0, 2, 5], "ci_pipeline_tampered_builds": [0, 0, 1, 3], "compromised_service_accounts": [0, 0, 1, 1]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-18T06:00:00Z", "level": "WARN", "service": "node-exporter", "message": "k8s-node-03 CPU usage 95% — no corresponding workload increase"},
                {"timestamp": "2025-03-18T07:00:00Z", "level": "WARN", "service": "node-exporter", "message": "CPU steal time 30% across 5 nodes — possible noisy neighbor or rogue process"},
                {"timestamp": "2025-03-18T08:00:00Z", "level": "INFO", "service": "prometheus", "message": "Application request throughput down 40% despite no deployment changes"},
            ],
            2: [
                {"timestamp": "2025-03-18T08:30:00Z", "level": "WARN", "service": "security-scanner", "message": "Unknown process 'kworker-helper' consuming 45% CPU on k8s-node-03, running as root"},
                {"timestamp": "2025-03-18T08:35:00Z", "level": "WARN", "service": "network-monitor", "message": "Unusual outbound traffic: 50MB/sec to IP 185.220.101.x (known mining pool)"},
            ],
            3: [
                {"timestamp": "2025-03-18T08:45:00Z", "level": "FATAL", "service": "security-audit", "message": "CI/CD pipeline tampered: base image for worker-service injected with cryptominer binary 'kworker-helper'"},
                {"timestamp": "2025-03-18T08:50:00Z", "level": "FATAL", "service": "security-audit", "message": "Compromised: CI service account 'ci-deployer' — API key leaked in public GitHub repo 3 days ago"},
                {"timestamp": "2025-03-18T09:00:00Z", "level": "ERROR", "service": "security-audit", "message": "3 deployments in past 72h contained tampered base images — miner deployed to 8 production nodes"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "HighCPUUsage", "severity": "warning", "source": "prometheus", "message": "Multiple nodes at > 90% CPU without workload increase", "fired_at": "2025-03-18T07:00:00Z"},
            ],
            2: [
                {"name": "UnknownProcess", "severity": "critical", "source": "security-scanner", "message": "Unrecognized process 'kworker-helper' running as root", "fired_at": "2025-03-18T08:30:00Z"},
            ],
            3: [
                {"name": "CryptominerDetected", "severity": "critical", "source": "security-audit", "message": "Cryptominer in production — CI/CD pipeline compromised", "fired_at": "2025-03-18T08:45:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-18T06:00:00Z", "event": "CPU anomaly detected", "source": "node-exporter"},
            ],
            2: [
                {"timestamp": "2025-03-18T08:30:00Z", "event": "Unknown process identified", "source": "security-scanner"},
                {"timestamp": "2025-03-18T08:35:00Z", "event": "Outbound traffic to mining pool", "source": "network-monitor"},
            ],
            3: [
                {"timestamp": "2025-03-18T08:45:00Z", "event": "CI/CD pipeline compromise confirmed", "source": "security-audit"},
                {"timestamp": "2025-03-18T09:00:00Z", "event": "Full scope: 8 nodes, 3 compromised deployments", "source": "security-audit"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "security",
            "remediation": "rollback_deploy",
            "key_diagnosis_terms": ["cryptominer", "CI/CD", "compromised", "pipeline", "security", "tampered", "mining"],
            "harmful_remediations": ["restart_service", "monitor"],
        },
        "grader": HARD_GRADER,
    },
    {
        "id": "hard_incident",
        "difficulty": "hard",
        "incident_id": "INC-3005",
        "timestamp": "2025-03-19T16:00:00Z",
        "severity_indicator": "P2",
        "title": "Database Replication Drift Causing Stale Reads",
        "description": "Some API responses return stale data — users see old order statuses, inventory counts are wrong. Writes succeed but reads sometimes return data from minutes ago. Issue is intermittent and affects a random subset of requests.",
        "affected_services": ["postgres-primary", "postgres-replica-1", "postgres-replica-2", "api-gateway"],
        "metrics_by_step": {
            1: {"stale_read_rate_pct": [0, 5, 15, 25], "replication_lag_seconds": [0.1, 5, 30, 120], "read_from_replica_pct": [70, 70, 70, 70]},
            2: {"replica_1_lag_sec": [0.1, 0.5, 1, 2], "replica_2_lag_sec": [0.5, 10, 60, 180], "replica_2_wal_receive_rate": [100, 50, 10, 2]},
            3: {"replica_2_disk_iops": [3000, 2000, 500, 100], "replica_2_io_wait_pct": [5, 15, 40, 70], "replica_2_wal_segment_gap": [0, 5, 20, 50]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-19T14:00:00Z", "level": "WARN", "service": "api-gateway", "message": "User complaint: order status shows 'processing' but was already shipped"},
                {"timestamp": "2025-03-19T15:00:00Z", "level": "WARN", "service": "api-gateway", "message": "Inconsistent read: inventory count differs between sequential requests"},
            ],
            2: [
                {"timestamp": "2025-03-19T15:30:00Z", "level": "WARN", "service": "postgres-replica-2", "message": "Replication lag: 180 seconds behind primary — WAL receiver falling behind"},
                {"timestamp": "2025-03-19T15:35:00Z", "level": "INFO", "service": "postgres-replica-1", "message": "Replication lag: 2 seconds — within acceptable range"},
            ],
            3: [
                {"timestamp": "2025-03-19T15:45:00Z", "level": "ERROR", "service": "postgres-replica-2", "message": "IO wait 70% — disk subsystem severely degraded on /dev/sdb"},
                {"timestamp": "2025-03-19T15:50:00Z", "level": "WARN", "service": "node-exporter", "message": "SMART warning on /dev/sdb: reallocated sector count increasing — disk degradation"},
                {"timestamp": "2025-03-19T16:00:00Z", "level": "ERROR", "service": "postgres-replica-2", "message": "WAL segment gap: 50 segments behind — risk of replica becoming unrecoverable"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "StaleReadDetected", "severity": "warning", "source": "application", "message": "25% of read requests returning stale data", "fired_at": "2025-03-19T15:00:00Z"},
            ],
            2: [
                {"name": "ReplicationLagHigh", "severity": "critical", "source": "postgres-exporter", "message": "postgres-replica-2 lag > 120 seconds", "fired_at": "2025-03-19T15:30:00Z"},
            ],
            3: [
                {"name": "DiskDegradation", "severity": "critical", "source": "node-exporter", "message": "SMART warning on replica-2 disk", "fired_at": "2025-03-19T15:50:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-19T14:00:00Z", "event": "First user reports stale data", "source": "support"},
            ],
            2: [
                {"timestamp": "2025-03-19T15:30:00Z", "event": "Replica-2 replication lag identified", "source": "postgres-exporter"},
            ],
            3: [
                {"timestamp": "2025-03-19T15:50:00Z", "event": "Disk degradation on replica-2", "source": "node-exporter"},
                {"timestamp": "2025-03-19T16:00:00Z", "event": "Risk: replica may become unrecoverable", "source": "postgres"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "infrastructure",
            "remediation": "failover",
            "key_diagnosis_terms": ["replication", "lag", "replica", "stale", "disk", "degradation", "WAL"],
            "harmful_remediations": ["restart_service", "rollback_deploy"],
        },
        "grader": HARD_GRADER,
    },
    {
        "id": "hard_incident",
        "difficulty": "hard",
        "incident_id": "INC-3006",
        "timestamp": "2025-03-20T12:00:00Z",
        "severity_indicator": "P1",
        "title": "Canary Deploy Poisoning Production Traffic Routing",
        "description": "A canary deployment for the new recommendation engine is supposed to receive 5% of traffic. Instead, traffic routing is broken — 50% of users are hitting the unstable canary, causing widespread errors.",
        "affected_services": ["recommendation-service", "istio-ingress", "product-page"],
        "metrics_by_step": {
            1: {"canary_traffic_pct": [5, 20, 35, 50], "canary_error_rate_pct": [5, 15, 40, 65], "stable_error_rate_pct": [1, 1, 1, 1]},
            2: {"istio_virtualservice_weight_canary": [5, 5, 5, 5], "actual_routing_canary_pct": [5, 20, 40, 50], "envoy_config_sync_failures": [0, 2, 10, 25]},
            3: {"istio_pilot_push_errors": [0, 5, 20, 40], "istio_pilot_memory_mb": [512, 1024, 2048, 3800], "envoy_proxy_version_mismatch": [0, 0, 3, 8]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-20T10:00:00Z", "level": "INFO", "service": "deployment-bot", "message": "Canary deploy for recommendation-service-v3: 5% traffic weight configured"},
                {"timestamp": "2025-03-20T11:00:00Z", "level": "ERROR", "service": "product-page", "message": "Recommendation service returning 500 — affecting 50% of product page loads"},
                {"timestamp": "2025-03-20T11:30:00Z", "level": "WARN", "service": "istio-ingress", "message": "Traffic split anomaly: canary receiving 50% despite 5% weight config"},
            ],
            2: [
                {"timestamp": "2025-03-20T11:45:00Z", "level": "ERROR", "service": "istiod", "message": "Config push failed for 25 Envoy proxies — stale routing config retained"},
                {"timestamp": "2025-03-20T11:50:00Z", "level": "WARN", "service": "istiod", "message": "Pilot memory at 3.8GB (limit: 4GB) — config distribution degraded"},
            ],
            3: [
                {"timestamp": "2025-03-20T11:55:00Z", "level": "FATAL", "service": "istiod", "message": "Envoy proxy version mismatch: 8 proxies running v1.18, pilot pushing v1.20 config — incompatible"},
                {"timestamp": "2025-03-20T12:00:00Z", "level": "ERROR", "service": "istiod", "message": "Root cause: Istio control plane partially upgraded from v1.18 to v1.20 — mismatched proxies ignoring routing rules, falling back to round-robin"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "CanaryErrorRate", "severity": "critical", "source": "prometheus", "message": "Canary recommendation-service-v3 error rate 65%", "fired_at": "2025-03-20T11:00:00Z"},
            ],
            2: [
                {"name": "IstioConfigSyncFailure", "severity": "warning", "source": "istiod", "message": "25 Envoy proxies with stale config", "fired_at": "2025-03-20T11:45:00Z"},
            ],
            3: [
                {"name": "IstioVersionMismatch", "severity": "critical", "source": "istiod", "message": "Control plane / data plane version mismatch", "fired_at": "2025-03-20T11:55:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-20T10:00:00Z", "event": "Canary deploy started (5% weight)", "source": "deployment-bot"},
                {"timestamp": "2025-03-20T11:00:00Z", "event": "50% of users hitting canary errors", "source": "prometheus"},
            ],
            2: [
                {"timestamp": "2025-03-20T11:45:00Z", "event": "Envoy config sync failures detected", "source": "istiod"},
            ],
            3: [
                {"timestamp": "2025-03-20T11:55:00Z", "event": "Istio version mismatch identified", "source": "istiod"},
                {"timestamp": "2025-03-20T12:00:00Z", "event": "Root cause: partial Istio upgrade broke routing", "source": "istiod"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "configuration",
            "remediation": "rollback_deploy",
            "key_diagnosis_terms": ["canary", "Istio", "routing", "mismatch", "version", "envoy", "config"],
            "harmful_remediations": ["restart_service", "monitor"],
        },
        "grader": HARD_GRADER,
    },
    {
        "id": "hard_incident",
        "difficulty": "hard",
        "incident_id": "INC-3007",
        "timestamp": "2025-03-21T23:00:00Z",
        "severity_indicator": "P1",
        "title": "Time-Bomb Bug — Epoch Timestamp Overflow at Midnight UTC",
        "description": "At midnight UTC, multiple services began crashing with serialization errors. The issue seems time-dependent — services restarted before midnight work fine, but new instances after midnight crash immediately.",
        "affected_services": ["order-service", "billing-service", "analytics-service"],
        "metrics_by_step": {
            1: {"crash_rate_per_min": [0, 5, 20, 50], "successful_startups_after_midnight": [10, 5, 0, 0], "heap_dump_size_mb": [0, 0, 0, 500]},
            2: {"serialization_errors_per_min": [0, 10, 100, 500], "timestamp_parse_failures": [0, 10, 100, 500], "affected_services_count": [0, 1, 2, 3]},
            3: {"epoch_seconds_value": [1742515199, 1742515200, 1742515200, 1742515200], "int32_max_exceeded": [0, 0, 1, 1], "services_using_legacy_timestamp_lib": [3, 3, 3, 3]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-21T00:00:01Z", "level": "FATAL", "service": "order-service", "message": "CrashLoopBackOff: unhandled exception in DateTimeSerializer — cannot serialize timestamp"},
                {"timestamp": "2025-03-21T00:00:02Z", "level": "FATAL", "service": "billing-service", "message": "Startup failed: InvalidTimestampError in ScheduleManager.init()"},
                {"timestamp": "2025-03-21T00:01:00Z", "level": "ERROR", "service": "analytics-service", "message": "Serialization error: timestamp value 1742515200 exceeds expected range"},
            ],
            2: [
                {"timestamp": "2025-03-21T00:05:00Z", "level": "ERROR", "service": "order-service", "message": "DateTimeSerializer.toEpochSeconds() returned value > INT32_MAX in legacy date library v2.3.1"},
                {"timestamp": "2025-03-21T00:06:00Z", "level": "WARN", "service": "billing-service", "message": "Legacy timestamp library v2.3.1 uses 32-bit signed integer for epoch — overflows after 2025-03-21T00:00:00Z"},
            ],
            3: [
                {"timestamp": "2025-03-21T00:10:00Z", "level": "INFO", "service": "dependency-scanner", "message": "3 services depend on legacy-datetime v2.3.1 — known issue: epoch overflow at 1742515200 (2025-03-21)"},
                {"timestamp": "2025-03-21T00:11:00Z", "level": "INFO", "service": "dependency-scanner", "message": "Fix available: legacy-datetime v2.4.0 uses 64-bit timestamps — requires recompilation and redeploy"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "MultiServiceCrash", "severity": "critical", "source": "kubernetes", "message": "3 services in CrashLoopBackOff since midnight UTC", "fired_at": "2025-03-21T00:02:00Z"},
            ],
            2: [
                {"name": "TimestampSerializationErrors", "severity": "critical", "source": "application", "message": "500 serialization errors/min across 3 services", "fired_at": "2025-03-21T00:05:00Z"},
            ],
            3: [
                {"name": "LegacyDependencyBug", "severity": "critical", "source": "dependency-scanner", "message": "Known epoch overflow bug in legacy-datetime v2.3.1", "fired_at": "2025-03-21T00:10:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-21T00:00:00Z", "event": "Midnight UTC — crashes began", "source": "kubernetes"},
            ],
            2: [
                {"timestamp": "2025-03-21T00:05:00Z", "event": "Timestamp overflow identified", "source": "order-service"},
            ],
            3: [
                {"timestamp": "2025-03-21T00:10:00Z", "event": "Legacy library bug confirmed (v2.3.1)", "source": "dependency-scanner"},
                {"timestamp": "2025-03-21T00:11:00Z", "event": "Fix available in v2.4.0", "source": "dependency-scanner"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "application",
            "remediation": "rollback_deploy",
            "key_diagnosis_terms": ["epoch", "overflow", "timestamp", "32-bit", "legacy", "library", "midnight"],
            "harmful_remediations": ["restart_service", "monitor"],
        },
        "grader": HARD_GRADER,
    },
    {
        "id": "hard_incident",
        "difficulty": "hard",
        "incident_id": "INC-3008",
        "timestamp": "2025-03-22T08:00:00Z",
        "severity_indicator": "P1",
        "title": "Terraform State Corruption — Infrastructure Drift",
        "description": "Cloud infrastructure changes are failing. Terraform plan shows 47 resources to destroy that shouldn't be destroyed. A developer manually modified cloud resources outside Terraform, causing state drift. Production databases and load balancers at risk.",
        "affected_services": ["terraform", "cloud-infra", "postgres-primary", "load-balancer"],
        "metrics_by_step": {
            1: {"terraform_plan_destroy_count": [0, 10, 30, 47], "terraform_plan_create_count": [0, 5, 15, 22], "infra_drift_resources": [0, 5, 20, 35]},
            2: {"manual_cloud_changes_30d": [0, 3, 8, 15], "state_file_last_modified_hours_ago": [1, 12, 48, 96], "resources_in_state_not_in_cloud": [0, 5, 10, 12]},
            3: {"production_db_in_destroy_plan": [0, 0, 1, 1], "lb_in_destroy_plan": [0, 0, 1, 1], "state_lock_conflicts_24h": [0, 2, 5, 8]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-22T07:00:00Z", "level": "ERROR", "service": "terraform", "message": "terraform plan: 47 to destroy, 22 to create, 0 to change — UNEXPECTED"},
                {"timestamp": "2025-03-22T07:05:00Z", "level": "WARN", "service": "terraform", "message": "Resource aws_rds_instance.production shows 'must be replaced' — THIS IS THE PRODUCTION DATABASE"},
            ],
            2: [
                {"timestamp": "2025-03-22T07:30:00Z", "level": "WARN", "service": "cloud-audit", "message": "15 manual AWS console changes detected in past 30 days — resources not tracked in Terraform state"},
                {"timestamp": "2025-03-22T07:35:00Z", "level": "ERROR", "service": "terraform", "message": "State drift: 12 resources exist in state but not in cloud (manually deleted?) — 23 resources in cloud but not in state (manually created)"},
            ],
            3: [
                {"timestamp": "2025-03-22T07:50:00Z", "level": "FATAL", "service": "terraform", "message": "CRITICAL: Running terraform apply with current plan would destroy aws_rds_instance.production and aws_lb.main"},
                {"timestamp": "2025-03-22T07:55:00Z", "level": "WARN", "service": "terraform", "message": "State file has 8 lock conflicts in past 24h — multiple engineers running terraform concurrently without coordination"},
                {"timestamp": "2025-03-22T08:00:00Z", "level": "INFO", "service": "terraform", "message": "Recommended: terraform import for manually created resources, terraform state rm for deleted resources, then re-plan"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "TerraformDestructivePlan", "severity": "critical", "source": "ci-cd", "message": "Terraform plan would destroy 47 resources", "fired_at": "2025-03-22T07:00:00Z"},
            ],
            2: [
                {"name": "InfrastructureDrift", "severity": "critical", "source": "cloud-audit", "message": "35 resources drifted from Terraform state", "fired_at": "2025-03-22T07:30:00Z"},
            ],
            3: [
                {"name": "ProductionDBAtRisk", "severity": "critical", "source": "terraform", "message": "Production database in destroy plan", "fired_at": "2025-03-22T07:50:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-22T07:00:00Z", "event": "Destructive terraform plan detected", "source": "ci-cd"},
            ],
            2: [
                {"timestamp": "2025-03-22T07:30:00Z", "event": "Manual cloud changes identified", "source": "cloud-audit"},
            ],
            3: [
                {"timestamp": "2025-03-22T07:50:00Z", "event": "Production DB in destroy plan confirmed", "source": "terraform"},
                {"timestamp": "2025-03-22T08:00:00Z", "event": "State reconciliation recommended", "source": "terraform"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "configuration",
            "remediation": "update_config",
            "key_diagnosis_terms": ["Terraform", "state", "drift", "manual", "destroy", "import", "reconcil"],
            "harmful_remediations": ["restart_service", "rollback_deploy"],
        },
        "grader": HARD_GRADER,
    },
]


HARD_TASK_METADATA = {
    "id": HARD_TASK_ID,
    "name": "Hard Incident Triage",
    "difficulty": "hard",
    "description": "Diagnose complex incidents with misleading signals, cascading failures, security breaches, and infrastructure corruption.",
    "grader": HARD_GRADER,
    "num_variants": len(HARD_TASKS),
}


def get_hard_task():
    return random.choice(HARD_TASKS)
