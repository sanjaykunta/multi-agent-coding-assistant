# Security Notes

This project is designed as a local development system, not a hosted multi-tenant service.

## Secret Handling

- Do not commit `.env`.
- Use `.env.example` for documented configuration only.
- Use Google Application Default Credentials locally.
- Use Secret Manager or platform environment variables for deployment.

## Tool Safety

Repository file access is constrained to `WORKSPACE_ROOT`. The repository tool rejects paths that escape the configured workspace.

## Model Output Safety

Generated code should be reviewed before use in production. The current workflow includes a Review Agent and tests, but a real deployment should also run static analysis, dependency scanning, and generated test execution inside an isolated environment.
