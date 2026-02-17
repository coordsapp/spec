# Event Discipline Instructions

## Principle

> Every state change emits an immutable, versioned, tenant-scoped event.

This enables:
- Audit trails for compliance
- Event sourcing / replay
- Real-time notifications
- Analytics pipelines

## Schema Addition

Add to `storage/schema_phase9_coordination.sql`:

```sql
-- Immutable event log for coordination domain
CREATE TABLE IF NOT EXISTS coordination_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    aggregate_type TEXT NOT NULL,  -- 'dock', 'carrier', 'assignment', 'notification'
    aggregate_id UUID NOT NULL,
    event_type TEXT NOT NULL,
    event_version INTEGER NOT NULL DEFAULT 1,
    event_data JSONB NOT NULL,
    correlation_id UUID,           -- For tracing related events
    caused_by UUID,                -- Reference to triggering event
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT                -- user_sub who triggered
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_coordination_events_aggregate
    ON coordination_events(org_id, aggregate_type, aggregate_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_coordination_events_type
    ON coordination_events(org_id, event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_coordination_events_correlation
    ON coordination_events(correlation_id)
    WHERE correlation_id IS NOT NULL;
```

## Event Types

| Event Type | Aggregate | Trigger |
|------------|-----------|----------|
| `dock.status_changed` | dock | Status transitions |
| `assignment.created` | assignment | AssignDock |
| `assignment.arrived` | assignment | Carrier checks in |
| `assignment.completed` | assignment | Carrier departs |
| `assignment.cancelled` | assignment | Manual cancellation |
| `notification.queued` | notification | ArrivalAlert |
| `notification.sent` | notification | Worker processes |
| `sla.breach_detected` | assignment | SLA worker |

## Event Structure

```go
type Event struct {
    ID            string          `json:"id"`
    OrgID         string          `json:"org_id"`
    AggregateType string          `json:"aggregate_type"`
    AggregateID   string          `json:"aggregate_id"`
    EventType     string          `json:"event_type"`
    EventVersion  int             `json:"event_version"`
    EventData     json.RawMessage `json:"event_data"`
    CorrelationID *string         `json:"correlation_id,omitempty"`
    CausedBy      *string         `json:"caused_by,omitempty"`
    CreatedAt     time.Time       `json:"created_at"`
    CreatedBy     string          `json:"created_by"`
}
```

## Implementation Pattern

### 1. Add event emitter to service

```go
// internal/coordination/service_events.go

func (s *Service) emitEvent(
    ctx context.Context,
    orgID string,
    aggregateType string,
    aggregateID string,
    eventType string,
    data any,
) error {
    eventData, err := json.Marshal(data)
    if err != nil {
        return fmt.Errorf("marshal event data: %w", err)
    }

    var createdBy string
    if claims, ok := auth.ClaimsFromContext(ctx); ok {
        createdBy = claims.Sub
    }

    var correlationID *string
    if cid := getCorrelationID(ctx); cid != "" {
        correlationID = &cid
    }

    _, err = s.db.ExecContext(ctx, `
        INSERT INTO coordination_events (
            org_id, aggregate_type, aggregate_id, event_type, event_data, 
            correlation_id, created_by
        )
        VALUES ($1::uuid, $2, $3::uuid, $4, $5, $6, $7)
    `, orgID, aggregateType, aggregateID, eventType, eventData, correlationID, createdBy)

    return err
}
```

### 2. Emit on state changes

```go
// In AssignDock, after successful insert:

if err := s.emitEvent(ctx, orgID, "assignment", item.ID, "assignment.created", map[string]any{
    "dock_id":      item.DockID,
    "dock_handle":  item.DockHandle,
    "carrier_name": item.CarrierName,
    "carrier_ref":  item.CarrierRef,
    "vehicle_type": item.VehicleType,
    "planned_at":   item.PlannedArrivalAt,
}); err != nil {
    // Log but don't fail the main operation
    log.Printf("failed to emit assignment.created event: %v", err)
}
```

### 3. Query events for audit

```go
// GET /v1/coordination/events?aggregate_type=assignment&aggregate_id=xxx

func (s *Service) ListEvents(ctx context.Context, orgID string, query EventQuery) ([]Event, error) {
    rows, err := s.db.QueryContext(ctx, `
        SELECT id, org_id, aggregate_type, aggregate_id, event_type, 
               event_version, event_data, correlation_id, caused_by, 
               created_at, created_by
        FROM coordination_events
        WHERE org_id = $1::uuid
          AND ($2 = '' OR aggregate_type = $2)
          AND ($3 = '' OR aggregate_id::text = $3)
          AND ($4 = '' OR event_type = $4)
        ORDER BY created_at DESC
        LIMIT $5 OFFSET $6
    `, orgID, query.AggregateType, query.AggregateID, query.EventType, query.Limit, query.Offset)
    // ... scan and return
}
```

## Correlation IDs

Use correlation IDs to trace related events across a workflow:

```go
// Middleware to extract/generate correlation ID
func correlationMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        correlationID := r.Header.Get("X-Correlation-ID")
        if correlationID == "" {
            correlationID = uuid.New().String()
        }
        ctx := context.WithValue(r.Context(), correlationKey, correlationID)
        w.Header().Set("X-Correlation-ID", correlationID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## Testing Checklist

- [ ] Events table created with proper indexes
- [ ] assignment.created event emitted on AssignDock
- [ ] Events are tenant-scoped (org_id filter)
- [ ] Events are immutable (no UPDATE/DELETE)
- [ ] Correlation ID propagates through request lifecycle
- [ ] Event listing API respects RBAC
