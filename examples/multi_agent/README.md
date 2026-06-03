# aidentity — multi_agent example

Identity structure for a team of AI agents sharing organizational context
while maintaining role-specific experience.

## Quickstart

1. Copy `identity/` into your project
2. Validate: `aidentity validate ./identity/`
3. Load for a specific role (in your agent's CLAUDE.md or equivalent):
   - First: `identity/core/iframe_v001.yaml` (shared context)
   - Then: `identity/core/roles/{your_role}/role_iframe_v001.yaml` (role context)
   - Then: latest pframe from `identity/sessions/{your_role}/` (session delta)

## What's here

| File | Purpose |
|---|---|
| `identity/core/iframe_v001.yaml` | Shared organizational context — all roles load this |
| `identity/core/roles/developer/role_iframe_v001.yaml` | Developer role experience |
| `identity/core/roles/reviewer/role_iframe_v001.yaml` | Reviewer role experience |
| `identity/core/roles/coordinator/role_iframe_v001.yaml` | Coordinator role experience |
| `identity/sessions/developer/session_001.yaml` | Example pframe for the developer role |

## Boot sequence

```
core/iframe_v001.yaml              ← organizational baseline (all roles)
  └─ roles/{role}/role_iframe_v001.yaml   ← role-specific history
       └─ sessions/{role}/latest.yaml      ← session delta (today's changes)
```

Each role only loads its own role_iframe and session history.
All roles share the same core iframe.

## Adding a new role

```bash
mkdir -p identity/core/roles/my_new_role
# Create role_iframe_v001.yaml following the structure in existing role examples
aidentity validate identity/core/roles/my_new_role/role_iframe_v001.yaml
```

## Validation

```bash
aidentity validate ./identity/
```
