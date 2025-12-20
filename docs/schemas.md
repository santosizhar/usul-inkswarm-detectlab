# Schemas

Schemas are versioned and treated as a contract.

- `login_attempt` — includes embedded support fields (support is not a separate event table).
- `checkout_attempt` — planned, but defined early for stability.

Use:
```bash
detectlab schemas list
detectlab schemas show login_attempt
```
