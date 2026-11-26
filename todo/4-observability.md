# 4-observability

## Goal
Добавить observability и monitoring для CI инфраструктуры: логирование релизов, dashboard, alerting.

## Context
Текущая инфраструктура работает, но нет полной видимости:
- Не понятно, какие проекты часто делают релизы
- Нет истории релизов по всем проектам
- Нет alerting если что-то сломалось
- Сложно отследить тренды (frequency, success rate, time)

Нужно:
- Логировать каждый релиз (версия, project, duration, status)
- Собирать метрики в central store (Prometheus, CloudWatch, etc)
- Dashboard для видимости
- Alerting для failures

## Implementation Plan

### 1. Logging layer

Create `release__log_io` action with inputs and JSON output

### 2. Event stream options

**Recommended: Option A (Webhook)** for simplicity:
- Each release posts JSON to configured webhook
- Webhook receives and stores
- Backend aggregates metrics

### 3. Webhook receiver (serverless function)

Example: AWS Lambda + DynamoDB

### 4. Dashboard (Grafana or similar)

Queries:
- Releases per project
- Success rate trends
- Release frequency heatmap
- Failed releases in past 24h

### 5. Alerting

Conditions:
- Release failed
- Unusual slowness (>1 hour)
- Project dormant (no releases in 30 days)
- Multiple failures

### 6. Configuration and secrets

```
OBSERVABILITY_WEBHOOK_URL = https://metrics.example.com/webhook
OBSERVABILITY_ENABLED = true
```

## Acceptance Criteria
- ✓ Logging infrastructure working
- ✓ Logs stored and queryable
- ✓ Dashboard displays metrics
- ✓ Alerts configured for failures
- ✓ INTEGRATION.md documents setup
- ✓ Privacy/retention policies documented

## Effort Estimate
8-12 hours

## Blocking Issues
- Need backend service for webhook

## Notes
- Start simple (logging only), add alerting later
- Privacy: never log source code, only metadata
