"""
Easy incident tasks — obvious root causes with clear signals.
Single-step solvable. Metrics and logs directly point to the issue.
"""
import random

EASY_TASK_ID = "easy_incident"
EASY_GRADER = "tasks.grader.grade_easy"

EASY_TASKS = [
    {
        "id": "easy_incident",
        "difficulty": "easy",
        "incident_id": "INC-1001",
        "timestamp": "2025-03-15T03:22:00Z",
        "severity_indicator": "P1",
        "title": "API Gateway — 100% 5xx After Deploy",
        "description": "All API requests returning HTTP 500 since deployment v2.14.0 was pushed 10 minutes ago. Customer-facing services are fully down.",
        "affected_services": ["api-gateway", "web-frontend", "mobile-backend"],
        "metrics_by_step": {
            1: {"error_rate_pct": [2.0, 5.0, 98.0, 100.0], "latency_p99_ms": [120, 450, 9999, 9999], "requests_per_sec": [1200, 800, 50, 10]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-15T03:12:00Z", "level": "INFO", "service": "deploy-bot", "message": "Deployment v2.14.0 started for api-gateway"},
                {"timestamp": "2025-03-15T03:14:00Z", "level": "INFO", "service": "deploy-bot", "message": "Deployment v2.14.0 completed — all pods healthy"},
                {"timestamp": "2025-03-15T03:15:01Z", "level": "ERROR", "service": "api-gateway", "message": "NullPointerException in AuthMiddleware.validate() — v2.14.0"},
                {"timestamp": "2025-03-15T03:15:02Z", "level": "FATAL", "service": "api-gateway", "message": "Unhandled exception: AuthMiddleware crash loop, pod restarting"},
                {"timestamp": "2025-03-15T03:20:00Z", "level": "ERROR", "service": "api-gateway", "message": "CrashLoopBackOff: 12 restarts in 5 minutes"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "HighErrorRate", "severity": "critical", "source": "prometheus", "message": "api-gateway error rate > 95% for 5 min", "fired_at": "2025-03-15T03:20:00Z"},
                {"name": "DeploymentFailed", "severity": "critical", "source": "argocd", "message": "Deployment v2.14.0 pods in CrashLoopBackOff", "fired_at": "2025-03-15T03:18:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-15T03:12:00Z", "event": "Deployment v2.14.0 initiated", "source": "deploy-bot"},
                {"timestamp": "2025-03-15T03:14:00Z", "event": "Deployment rolled out to all pods", "source": "argocd"},
                {"timestamp": "2025-03-15T03:15:00Z", "event": "Error rate spike detected", "source": "prometheus"},
                {"timestamp": "2025-03-15T03:20:00Z", "event": "PagerDuty alert fired — P1 incident", "source": "pagerduty"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "application",
            "remediation": "rollback_deploy",
            "key_diagnosis_terms": ["deploy", "v2.14", "crash", "rollback", "AuthMiddleware"],
            "harmful_remediations": ["restart_service"],
        },
        "grader": EASY_GRADER,
    },
    {
        "id": "easy_incident",
        "difficulty": "easy",
        "incident_id": "INC-1002",
        "timestamp": "2025-03-16T14:05:00Z",
        "severity_indicator": "P1",
        "title": "Database Server — Disk Full",
        "description": "Primary PostgreSQL database server has run out of disk space. Write operations are failing, causing cascading errors across all services.",
        "affected_services": ["postgres-primary", "order-service", "user-service", "payment-service"],
        "metrics_by_step": {
            1: {"disk_usage_pct": [72.0, 85.0, 95.0, 100.0], "db_write_errors_per_sec": [0, 0, 5, 120], "db_connections_active": [50, 50, 48, 2]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-16T12:00:00Z", "level": "WARN", "service": "postgres-primary", "message": "Disk usage at 85% on /var/lib/postgresql/data"},
                {"timestamp": "2025-03-16T13:30:00Z", "level": "WARN", "service": "postgres-primary", "message": "Disk usage at 95% — approaching critical threshold"},
                {"timestamp": "2025-03-16T14:00:00Z", "level": "FATAL", "service": "postgres-primary", "message": "PANIC: could not write to file pg_wal/000000010000000100000042: No space left on device"},
                {"timestamp": "2025-03-16T14:01:00Z", "level": "ERROR", "service": "order-service", "message": "Database write failed: SQLSTATE 53100 — disk full"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "DiskSpaceCritical", "severity": "critical", "source": "node-exporter", "message": "postgres-primary disk usage 100%", "fired_at": "2025-03-16T14:00:00Z"},
                {"name": "DatabaseWriteFailures", "severity": "critical", "source": "prometheus", "message": "Write error rate > 100/sec on postgres-primary", "fired_at": "2025-03-16T14:02:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-16T12:00:00Z", "event": "Disk usage warning at 85%", "source": "monitoring"},
                {"timestamp": "2025-03-16T13:30:00Z", "event": "Disk usage critical at 95%", "source": "monitoring"},
                {"timestamp": "2025-03-16T14:00:00Z", "event": "Disk full — PostgreSQL write-ahead log failed", "source": "postgres"},
                {"timestamp": "2025-03-16T14:02:00Z", "event": "Cascading write failures across services", "source": "prometheus"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "infrastructure",
            "remediation": "scale_up",
            "key_diagnosis_terms": ["disk", "full", "space", "postgres", "storage", "WAL"],
            "harmful_remediations": ["restart_service"],
        },
        "grader": EASY_GRADER,
    },
    {
        "id": "easy_incident",
        "difficulty": "easy",
        "incident_id": "INC-1003",
        "timestamp": "2025-03-17T08:30:00Z",
        "severity_indicator": "P2",
        "title": "SSL Certificate Expired — HTTPS Failures",
        "description": "TLS handshake failures across all HTTPS endpoints. Users seeing ERR_CERT_DATE_INVALID in browsers. Certificate expired 2 hours ago.",
        "affected_services": ["nginx-ingress", "web-frontend", "api-gateway"],
        "metrics_by_step": {
            1: {"tls_handshake_failures_per_sec": [0, 0, 5, 450], "successful_requests_pct": [100, 100, 60, 5], "http_vs_https_ratio": [0.01, 0.01, 0.3, 0.95]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-17T06:30:00Z", "level": "WARN", "service": "cert-manager", "message": "Certificate for *.example.com expires in 2 hours — renewal FAILED (ACME challenge failed)"},
                {"timestamp": "2025-03-17T08:30:00Z", "level": "ERROR", "service": "nginx-ingress", "message": "SSL_ERROR_EXPIRED_CERT_ALERT: certificate for *.example.com expired at 2025-03-17T08:00:00Z"},
                {"timestamp": "2025-03-17T08:31:00Z", "level": "ERROR", "service": "nginx-ingress", "message": "TLS handshake failure rate: 450/sec — all HTTPS connections rejected"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "SSLCertExpired", "severity": "critical", "source": "cert-manager", "message": "Certificate *.example.com has expired", "fired_at": "2025-03-17T08:00:00Z"},
                {"name": "TLSHandshakeFailures", "severity": "critical", "source": "nginx", "message": "TLS failure rate > 400/sec", "fired_at": "2025-03-17T08:31:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-17T06:30:00Z", "event": "Certificate renewal attempt failed", "source": "cert-manager"},
                {"timestamp": "2025-03-17T08:00:00Z", "event": "Certificate expired", "source": "cert-manager"},
                {"timestamp": "2025-03-17T08:30:00Z", "event": "TLS handshake failures began", "source": "nginx"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "configuration",
            "remediation": "update_config",
            "key_diagnosis_terms": ["SSL", "TLS", "certificate", "expired", "cert", "renewal"],
            "harmful_remediations": ["restart_service", "rollback_deploy"],
        },
        "grader": EASY_GRADER,
    },
    {
        "id": "easy_incident",
        "difficulty": "easy",
        "incident_id": "INC-1004",
        "timestamp": "2025-03-18T22:15:00Z",
        "severity_indicator": "P1",
        "title": "Kubernetes Node OOMKilled — Pod Evictions",
        "description": "Multiple critical pods evicted due to OOMKilled on worker node k8s-node-07. Services degraded as pods fail to reschedule.",
        "affected_services": ["order-service", "inventory-service", "k8s-node-07"],
        "metrics_by_step": {
            1: {"memory_usage_pct": [65.0, 80.0, 95.0, 100.0], "pod_restarts": [0, 2, 8, 15], "evicted_pods": [0, 0, 3, 7]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-18T21:45:00Z", "level": "WARN", "service": "kubelet", "message": "Node k8s-node-07 memory pressure — 95% used"},
                {"timestamp": "2025-03-18T22:00:00Z", "level": "ERROR", "service": "kubelet", "message": "OOMKilled: order-service-7f8d9 — container exceeded memory limit (2Gi)"},
                {"timestamp": "2025-03-18T22:05:00Z", "level": "ERROR", "service": "kubelet", "message": "Evicting pod inventory-service-3a2b1 due to node memory pressure"},
                {"timestamp": "2025-03-18T22:10:00Z", "level": "FATAL", "service": "kubelet", "message": "Node k8s-node-07: 7 pods evicted, node NotReady"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "NodeMemoryPressure", "severity": "critical", "source": "kubernetes", "message": "k8s-node-07 under memory pressure — 100% used", "fired_at": "2025-03-18T22:00:00Z"},
                {"name": "PodEvictions", "severity": "critical", "source": "kubernetes", "message": "7 pods evicted from k8s-node-07", "fired_at": "2025-03-18T22:10:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-18T21:45:00Z", "event": "Node memory pressure warning", "source": "kubelet"},
                {"timestamp": "2025-03-18T22:00:00Z", "event": "First pod OOMKilled", "source": "kubelet"},
                {"timestamp": "2025-03-18T22:10:00Z", "event": "7 pods evicted, node NotReady", "source": "kubernetes"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "infrastructure",
            "remediation": "scale_up",
            "key_diagnosis_terms": ["OOM", "memory", "evict", "node", "pod", "pressure"],
            "harmful_remediations": [],
        },
        "grader": EASY_GRADER,
    },
    {
        "id": "easy_incident",
        "difficulty": "easy",
        "incident_id": "INC-1005",
        "timestamp": "2025-03-19T11:00:00Z",
        "severity_indicator": "P3",
        "title": "CDN Provider Outage — Static Assets Failing",
        "description": "Third-party CDN (CloudFast) reporting degraded service. Static assets (JS, CSS, images) returning 503. Application functional but UI broken.",
        "affected_services": ["web-frontend", "cloudfast-cdn"],
        "metrics_by_step": {
            1: {"cdn_error_rate_pct": [0, 0, 45, 80], "page_load_time_sec": [1.2, 1.5, 8.0, 15.0], "cdn_cache_hit_ratio": [0.95, 0.90, 0.10, 0.02]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-19T10:45:00Z", "level": "WARN", "service": "web-frontend", "message": "CDN returning 503 for bundle.js — retrying"},
                {"timestamp": "2025-03-19T10:50:00Z", "level": "ERROR", "service": "web-frontend", "message": "Static asset load failure rate: 80% — CloudFast CDN unresponsive"},
                {"timestamp": "2025-03-19T10:55:00Z", "level": "INFO", "service": "statuspage", "message": "CloudFast status page: 'Investigating increased error rates in US-East region'"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "CDNErrorRate", "severity": "warning", "source": "synthetic-monitor", "message": "CDN error rate > 75% for static assets", "fired_at": "2025-03-19T10:50:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-19T10:45:00Z", "event": "CDN 503 errors began", "source": "web-frontend"},
                {"timestamp": "2025-03-19T10:55:00Z", "event": "CloudFast acknowledges issue on status page", "source": "statuspage"},
            ],
        },
        "expected": {
            "triage_priority": "P3",
            "root_cause_category": "external",
            "remediation": "failover",
            "key_diagnosis_terms": ["CDN", "CloudFast", "external", "third-party", "503", "static"],
            "harmful_remediations": ["restart_service", "rollback_deploy"],
        },
        "grader": EASY_GRADER,
    },
    {
        "id": "easy_incident",
        "difficulty": "easy",
        "incident_id": "INC-1006",
        "timestamp": "2025-03-20T16:45:00Z",
        "severity_indicator": "P2",
        "title": "Redis Cache Crash — Session Store Unavailable",
        "description": "Redis primary node crashed. All session lookups failing, users being logged out. Service returning authentication errors.",
        "affected_services": ["redis-primary", "auth-service", "session-store"],
        "metrics_by_step": {
            1: {"redis_connections": [500, 500, 0, 0], "auth_failures_per_sec": [2, 5, 300, 450], "session_hits": [1000, 1000, 0, 0]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-20T16:40:00Z", "level": "FATAL", "service": "redis-primary", "message": "FATAL: Redis process terminated — signal 9 (OOMKiller)"},
                {"timestamp": "2025-03-20T16:41:00Z", "level": "ERROR", "service": "auth-service", "message": "Connection refused: redis-primary:6379 — session lookup failed"},
                {"timestamp": "2025-03-20T16:42:00Z", "level": "ERROR", "service": "auth-service", "message": "401 Unauthorized — cannot validate session token (redis unavailable)"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "RedisDown", "severity": "critical", "source": "prometheus", "message": "redis-primary is unreachable", "fired_at": "2025-03-20T16:41:00Z"},
                {"name": "AuthFailureSpike", "severity": "critical", "source": "prometheus", "message": "Authentication failures > 400/sec", "fired_at": "2025-03-20T16:43:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-20T16:40:00Z", "event": "Redis primary killed by OOMKiller", "source": "syslog"},
                {"timestamp": "2025-03-20T16:41:00Z", "event": "Auth service lost redis connection", "source": "auth-service"},
                {"timestamp": "2025-03-20T16:43:00Z", "event": "Mass authentication failures detected", "source": "prometheus"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "infrastructure",
            "remediation": "restart_service",
            "key_diagnosis_terms": ["Redis", "crash", "OOM", "session", "cache", "authentication"],
            "harmful_remediations": ["rollback_deploy"],
        },
        "grader": EASY_GRADER,
    },
    {
        "id": "easy_incident",
        "difficulty": "easy",
        "incident_id": "INC-1007",
        "timestamp": "2025-03-21T09:20:00Z",
        "severity_indicator": "P2",
        "title": "Payment Gateway — Webhook URL Misconfigured",
        "description": "Payment confirmations not arriving. Webhook endpoint changed during config update but new URL has a typo. All payment callbacks returning 404.",
        "affected_services": ["payment-service", "order-service"],
        "metrics_by_step": {
            1: {"webhook_success_rate_pct": [100, 100, 0, 0], "pending_payments": [5, 10, 85, 200], "payment_confirmation_latency_sec": [2, 3, 9999, 9999]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-21T08:55:00Z", "level": "INFO", "service": "config-manager", "message": "Config update applied: payment.webhook_url changed to https://api.example.com/webhokos/payment"},
                {"timestamp": "2025-03-21T09:00:00Z", "level": "ERROR", "service": "payment-gateway", "message": "Webhook delivery failed: POST https://api.example.com/webhokos/payment — 404 Not Found"},
                {"timestamp": "2025-03-21T09:10:00Z", "level": "WARN", "service": "order-service", "message": "200 pending payments awaiting confirmation — webhook delivery failing"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "WebhookDeliveryFailure", "severity": "warning", "source": "payment-gateway", "message": "Webhook success rate dropped to 0%", "fired_at": "2025-03-21T09:05:00Z"},
                {"name": "PendingPaymentsHigh", "severity": "warning", "source": "prometheus", "message": "200+ pending payments without confirmation", "fired_at": "2025-03-21T09:15:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-21T08:55:00Z", "event": "Config update changed webhook URL (typo: webhokos)", "source": "config-manager"},
                {"timestamp": "2025-03-21T09:00:00Z", "event": "Webhook delivery failures began", "source": "payment-gateway"},
                {"timestamp": "2025-03-21T09:15:00Z", "event": "200+ pending payments alert fired", "source": "prometheus"},
            ],
        },
        "expected": {
            "triage_priority": "P2",
            "root_cause_category": "configuration",
            "remediation": "update_config",
            "key_diagnosis_terms": ["webhook", "config", "typo", "URL", "404", "misconfigured"],
            "harmful_remediations": ["restart_service", "rollback_deploy"],
        },
        "grader": EASY_GRADER,
    },
    {
        "id": "easy_incident",
        "difficulty": "easy",
        "incident_id": "INC-1008",
        "timestamp": "2025-03-22T02:10:00Z",
        "severity_indicator": "P1",
        "title": "DNS Resolution Failure — Complete Service Outage",
        "description": "Internal DNS server unresponsive. All inter-service communication failing because services cannot resolve hostnames. Total platform outage.",
        "affected_services": ["coredns", "all-services"],
        "metrics_by_step": {
            1: {"dns_query_failures_per_sec": [0, 10, 500, 1200], "service_to_service_errors": [0, 20, 800, 2000], "dns_response_time_ms": [2, 50, 9999, 9999]},
        },
        "logs_by_step": {
            1: [
                {"timestamp": "2025-03-22T02:05:00Z", "level": "FATAL", "service": "coredns", "message": "CoreDNS process exited — OOM killed (exceeded 512Mi memory limit)"},
                {"timestamp": "2025-03-22T02:06:00Z", "level": "ERROR", "service": "api-gateway", "message": "DNS resolution failed for order-service.svc.cluster.local"},
                {"timestamp": "2025-03-22T02:07:00Z", "level": "ERROR", "service": "payment-service", "message": "DNS resolution failed for postgres-primary.svc.cluster.local"},
            ],
        },
        "alerts_by_step": {
            1: [
                {"name": "DNSResolutionFailure", "severity": "critical", "source": "kubernetes", "message": "CoreDNS pods are not running", "fired_at": "2025-03-22T02:06:00Z"},
                {"name": "CrossServiceFailures", "severity": "critical", "source": "prometheus", "message": "Inter-service error rate > 90%", "fired_at": "2025-03-22T02:08:00Z"},
            ],
        },
        "timeline_by_step": {
            1: [
                {"timestamp": "2025-03-22T02:05:00Z", "event": "CoreDNS OOM killed", "source": "kubelet"},
                {"timestamp": "2025-03-22T02:06:00Z", "event": "DNS queries failing platform-wide", "source": "prometheus"},
                {"timestamp": "2025-03-22T02:08:00Z", "event": "Total inter-service communication failure", "source": "prometheus"},
            ],
        },
        "expected": {
            "triage_priority": "P1",
            "root_cause_category": "network",
            "remediation": "restart_service",
            "key_diagnosis_terms": ["DNS", "CoreDNS", "resolution", "OOM", "hostname", "cluster"],
            "harmful_remediations": ["rollback_deploy"],
        },
        "grader": EASY_GRADER,
    },
]


EASY_TASK_METADATA = {
    "id": EASY_TASK_ID,
    "name": "Easy Incident Triage",
    "difficulty": "easy",
    "description": "Triage incidents with obvious root causes — clear logs, direct metric signals, single-step diagnosis.",
    "grader": EASY_GRADER,
    "num_variants": len(EASY_TASKS),
}


def get_easy_task():
    return random.choice(EASY_TASKS)
