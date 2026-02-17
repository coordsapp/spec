# RBAC Implementation Instructions

## Permission Model

### Roles

| Role | Description | Scope |
|------|-------------|-------|
| `super_admin` | Platform-wide access | Global |
| `org_admin` | Full org access | Tenant |
| `operator` | Operational access | Tenant |
| `viewer` | Read-only access | Tenant |
| `carrier_viewer` | Limited dock visibility | Tenant |

### Permissions

| Permission | super_admin | org_admin | operator | viewer | carrier_viewer |
|------------|:-----------:|:---------:|:--------:|:------:|:--------------:|
| ViewWarehouses | ✓ | ✓ | ✓ | ✓ | ✓ (limited) |
| ManageWarehouses | ✓ | ✓ | ✓ | ✗ | ✗ |
| ManageBilling | ✓ | ✓ | ✗ | ✗ | ✗ |
| ManageDomains | ✓ | ✓ | ✗ | ✗ | ✗ |
| ManageMembers | ✓ | ✓ | ✗ | ✗ | ✗ |
| ViewAnalytics | ✓ | ✓ | ✓ | ✓ | ✗ |

## Implementation

### Auth Middleware (existing)

```go
// internal/auth/middleware.go

func (m *Middleware) Require(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        claims, err := m.manager.ParseRequest(r)
        if err != nil {
            writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "unauthorized"})
            return
        }
        next.ServeHTTP(w, r.WithContext(WithClaims(r.Context(), claims)))
    })
}

func (m *Middleware) RequirePermission(permission Permission, next http.Handler) http.Handler {
    return m.Require(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        claims, ok := ClaimsFromContext(r.Context())
        if !ok || !Can(claims.Role, permission) {
            writeJSON(w, http.StatusForbidden, map[string]string{"error": "forbidden"})
            return
        }
        next.ServeHTTP(w, r)
    }))
}
```

### Permission Check Function

```go
// internal/auth/permissions.go

type Permission string

const (
    PermissionViewWarehouses   Permission = "view_warehouses"
    PermissionManageWarehouses Permission = "manage_warehouses"
    PermissionManageBilling    Permission = "manage_billing"
    PermissionManageDomains    Permission = "manage_domains"
    PermissionManageMembers    Permission = "manage_members"
    PermissionViewAnalytics    Permission = "view_analytics"
)

var rolePermissions = map[string][]Permission{
    "super_admin": {
        PermissionViewWarehouses, PermissionManageWarehouses,
        PermissionManageBilling, PermissionManageDomains,
        PermissionManageMembers, PermissionViewAnalytics,
    },
    "org_admin": {
        PermissionViewWarehouses, PermissionManageWarehouses,
        PermissionManageBilling, PermissionManageDomains,
        PermissionManageMembers, PermissionViewAnalytics,
    },
    "operator": {
        PermissionViewWarehouses, PermissionManageWarehouses,
        PermissionViewAnalytics,
    },
    "viewer": {
        PermissionViewWarehouses, PermissionViewAnalytics,
    },
    "carrier_viewer": {
        PermissionViewWarehouses, // Limited scope
    },
}

func Can(role string, permission Permission) bool {
    perms, ok := rolePermissions[role]
    if !ok {
        return false
    }
    for _, p := range perms {
        if p == permission {
            return true
        }
    }
    return false
}
```

## Tenant Isolation

### Claims Structure

```go
type Claims struct {
    Sub    string `json:"sub"`     // User ID
    Email  string `json:"email"`
    Role   string `json:"role"`
    OrgID  string `json:"org_id"` // Tenant ID
    Exp    int64  `json:"exp"`
}
```

### Enforcing Tenant Scope

**CRITICAL:** Every database query MUST include `org_id` filter.

```go
// CORRECT - Tenant-scoped query
rows, err := s.db.QueryContext(ctx, `
    SELECT * FROM docks d
    JOIN warehouses w ON w.id = d.warehouse_id
    WHERE w.org_id = $1::uuid
`, claims.OrgID)

// WRONG - No tenant filter (data leak!)
rows, err := s.db.QueryContext(ctx, `
    SELECT * FROM docks
`)
```

### Service Pattern

```go
// All service methods take orgID as first parameter
func (s *Service) GetDockStatus(ctx context.Context, orgID, dockID string) (DockStatus, error) {
    // Validate orgID matches claims
    claims, ok := auth.ClaimsFromContext(ctx)
    if !ok || claims.OrgID != orgID {
        return DockStatus{}, ErrUnauthorized
    }
    
    // Query with tenant filter
    // ...
}
```

## Route Registration Pattern

```go
// cmd/resolver/routes_enterprise.go

mux.Handle("/v1/coordination/assign-dock", 
    authMiddleware.Require(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        claims, ok := auth.ClaimsFromContext(r.Context())
        if !ok {
            writeJSON(w, http.StatusUnauthorized, errorResponse{Error: "unauthorized"})
            return
        }
        
        // Check org-level permission
        if _, ok := authorizeOrgAction(w, r, phase3Service, claims, auth.PermissionManageWarehouses); !ok {
            return
        }
        
        coordinationRoutes.AssignDock(w, r)
    })))
```

## carrier_viewer Special Rules

`carrier_viewer` has limited access:

1. Can only see docks they have assignments for
2. Cannot see other carriers' information
3. Cannot modify dock status

```go
func (s *Service) GetDocksForCarrier(ctx context.Context, orgID, carrierRef string) ([]Dock, error) {
    rows, err := s.db.QueryContext(ctx, `
        SELECT DISTINCT d.*
        FROM docks d
        JOIN coordination_assignments ca ON ca.dock_id = d.id
        JOIN warehouses w ON w.id = d.warehouse_id
        WHERE w.org_id = $1::uuid
          AND ca.carrier_ref = $2
          AND ca.status IN ('assigned', 'arrived')
    `, orgID, carrierRef)
    // ...
}
```

## Testing Checklist

- [ ] Unauthenticated requests return 401
- [ ] Wrong role requests return 403
- [ ] Tenant A cannot access Tenant B data
- [ ] carrier_viewer sees only their assigned docks
- [ ] super_admin can access all tenants (if applicable)
- [ ] Claims include org_id for tenant scoping
