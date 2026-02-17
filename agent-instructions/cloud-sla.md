# SLA Monitoring Instructions

## Overview

SLA monitoring tracks carrier arrival times against planned schedules:
- On-time vs late arrivals
- Compliance percentages by carrier/dock
- Breach detection and alerting

## Schema (existing)

```sql
-- From schema_phase4_sla.sql
CREATE TABLE IF NOT EXISTS sla_checks (...);
CREATE TABLE IF NOT EXISTS sla_incidents (...);
CREATE TABLE IF NOT EXISTS sla_periods (...);
CREATE TABLE IF NOT EXISTS sla_credits (...);
```

## Compliance Calculation

### Grace Period

Arrivals within `grace_minutes` of `planned_arrival_at` are considered on-time.

```sql
-- On-time: actual_arrival <= planned_arrival + grace
WHERE actual_arrival_at <= planned_arrival_at + INTERVAL '15 minutes'
```

### API: GET /v1/analytics/sla-compliance

**Query Parameters:**
| Param | Default | Description |
|-------|---------|-------------|
| days | 30 | Lookback period |
| grace_minutes | 15 | Grace period for on-time |
| limit | 50 | Max records |
| offset | 0 | Pagination |

**Response:**
```json
{
  "items": [
    {
      "carrier_name": "FastFreight",
      "dock_id": "uuid",
      "dock_handle": "@acme/dock-1",
      "total_assignments": 45,
      "on_time_assignments": 42,
      "late_assignments": 3,
      "on_time_rate": 0.933,
      "average_delay_sec": 120
    }
  ],
  "days": 30,
  "grace_minutes": 15,
  "total_assignments": 150,
  "on_time_assignments": 140,
  "late_assignments": 10,
  "limit": 50,
  "offset": 0
}
```

### Implementation

```go
// internal/coordination/service_analytics.go

func (s *Service) ListSLACompliance(ctx context.Context, orgID string, query SLAComplianceQuery) (SLAComplianceSummary, error) {
    graceDuration := time.Duration(query.GraceMinutes) * time.Minute
    cutoff := time.Now().UTC().AddDate(0, 0, -query.Days)

    rows, err := s.db.QueryContext(ctx, `
        SELECT 
            ca.carrier_name,
            ca.dock_id::text,
            d.handle AS dock_handle,
            COUNT(*) AS total_assignments,
            COUNT(*) FILTER (
                WHERE op.arrived_at <= ca.planned_arrival_at + $3::interval
            ) AS on_time_assignments,
            COUNT(*) FILTER (
                WHERE op.arrived_at > ca.planned_arrival_at + $3::interval
            ) AS late_assignments,
            COALESCE(
                AVG(
                    EXTRACT(EPOCH FROM (op.arrived_at - ca.planned_arrival_at))
                ) FILTER (WHERE op.arrived_at > ca.planned_arrival_at),
                0
            )::bigint AS average_delay_sec
        FROM coordination_assignments ca
        JOIN docks d ON d.id = ca.dock_id
        JOIN warehouses w ON w.id = ca.warehouse_id
        LEFT JOIN dock_operations op ON op.dock_id = ca.dock_id 
            AND op.arrived_at BETWEEN ca.created_at AND ca.created_at + INTERVAL '24 hours'
        WHERE w.org_id = $1::uuid
          AND ca.created_at >= $2
          AND ca.status IN ('arrived', 'completed')
          AND ca.planned_arrival_at IS NOT NULL
        GROUP BY ca.carrier_name, ca.dock_id, d.handle
        ORDER BY late_assignments DESC, total_assignments DESC
        LIMIT $4 OFFSET $5
    `, orgID, cutoff, graceDuration, query.Limit, query.Offset)
    // ... scan and aggregate
}
```

## SLA Breach Detection

### Background Worker

```go
// internal/sla/worker.go

type Worker struct {
    db            *sql.DB
    checkInterval time.Duration
    coordinator   *coordination.Service
    notifier      NotificationService
}

func (w *Worker) Run(ctx context.Context) {
    ticker := time.NewTicker(w.checkInterval)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            w.checkBreaches(ctx)
        }
    }
}

func (w *Worker) checkBreaches(ctx context.Context) {
    // Find assignments where:
    // - status = 'assigned' (not yet arrived)
    // - planned_arrival_at + grace < NOW()
    // - no breach event emitted yet
    
    rows, err := w.db.QueryContext(ctx, `
        SELECT ca.id, ca.org_id, ca.dock_id, ca.carrier_name, ca.planned_arrival_at
        FROM coordination_assignments ca
        WHERE ca.status = 'assigned'
          AND ca.planned_arrival_at + INTERVAL '15 minutes' < NOW()
          AND NOT EXISTS (
              SELECT 1 FROM coordination_events ce
              WHERE ce.aggregate_id = ca.id
                AND ce.event_type = 'sla.breach_detected'
          )
    `)
    // ...
    
    for rows.Next() {
        // Emit breach event
        w.coordinator.EmitEvent(ctx, orgID, "assignment", assignmentID, "sla.breach_detected", map[string]any{
            "carrier_name":       carrierName,
            "planned_arrival_at": plannedAt,
            "detected_at":        time.Now().UTC(),
            "delay_minutes":      delayMinutes,
        })
        
        // Optionally trigger notification
        w.notifier.SendSLABreachAlert(ctx, orgID, assignmentID)
    }
}
```

### Escalation Clock

Implement escalation tiers:

| Delay | Action |
|-------|--------|
| +15 min | Warning event |
| +30 min | Breach event + notify operator |
| +60 min | Critical breach + notify org_admin |
| +120 min | Escalate to external systems |

```go
type EscalationTier struct {
    DelayMinutes int
    EventType    string
    NotifyRoles  []string
}

var escalationTiers = []EscalationTier{
    {15, "sla.warning", []string{}},
    {30, "sla.breach_detected", []string{"operator"}},
    {60, "sla.critical_breach", []string{"operator", "org_admin"}},
    {120, "sla.escalated", []string{"operator", "org_admin", "external"}},
}
```

## Dashboard Metrics

### Real-time Stats

```go
func (s *Service) GetDashboardStats(ctx context.Context, orgID string) (DashboardStats, error) {
    var stats DashboardStats
    
    // Count docks by state
    s.db.QueryRowContext(ctx, `
        SELECT 
            COUNT(*) FILTER (WHERE state = 'available'),
            COUNT(*) FILTER (WHERE state = 'occupied'),
            COUNT(*) FILTER (WHERE state = 'assigned'),
            COUNT(*) FILTER (WHERE state = 'cleaning')
        FROM (...dock status subquery...)
        WHERE org_id = $1::uuid
    `, orgID).Scan(&stats.Available, &stats.Occupied, &stats.Assigned, &stats.Cleaning)
    
    // Active carriers (assignments in 'assigned' or 'arrived' status)
    // Pending arrivals (assignments due in next 2 hours)
    // Current SLA compliance (last 24 hours)
    
    return stats, nil
}
```

## Testing Checklist

- [ ] SLA compliance calculation respects grace_minutes
- [ ] On-time rate calculated correctly
- [ ] Average delay only counts late arrivals
- [ ] Breach detection worker runs at configured interval
- [ ] Breach events are idempotent (no duplicates)
- [ ] Escalation tiers trigger correct notifications
- [ ] Dashboard stats update in real-time
