# Deployment

Project India should deploy as a Streamlit app backed by hosted Postgres.

```text
GitHub repo -> Streamlit Community Cloud -> hosted Postgres
```

GitHub contains app code, schema, tests, CI, and project documentation. Postgres contains research data.

## Production Components

- Streamlit Community Cloud app
- Hosted Postgres database, such as Supabase, Neon, Railway, Render, Aiven, or RDS
- Streamlit secrets for the production database URL
- `db/schema.sql` as the baseline schema
- `dashboard.py` as the Streamlit entrypoint

## Hosted Postgres Setup

1. Create a hosted Postgres project.
2. Copy the production connection string.
3. Require SSL when the provider supports it.
4. Apply the schema:

```bash
psql "$PROJECT_INDIA_DATABASE_URL" -f db/schema.sql
```

Do not commit production connection strings, `.env`, `.streamlit/secrets.toml`, or research exports.

## Streamlit Secrets

For local development, use `.streamlit/secrets.toml` or `.env`; keep both uncommitted.

For Streamlit Community Cloud, paste secrets in the app's Advanced settings.

```toml
PROJECT_INDIA_DATABASE_URL = "postgresql://user:password@host:5432/database?sslmode=require"
```

The app should read `PROJECT_INDIA_DATABASE_URL` and connect to Postgres. The local default remains:

```text
postgresql://project_india:project_india_local@localhost:5433/project_india
```

## Streamlit App Deployment

1. Go to `share.streamlit.io`.
2. Create a new app.
3. Select repository: `knirantar/Project-India`.
4. Select branch: `main`.
5. Set main file path: `dashboard.py`.
6. Select Python 3.11 or newer.
7. Add `PROJECT_INDIA_DATABASE_URL` in Advanced settings secrets.
8. Deploy.

After the first deployment, code changes are deployed from GitHub. Research changes should happen in Postgres.

## Recommended Workflow

Development flow:

```text
feature branch
  -> local Postgres
  -> local Streamlit test
  -> pull request
  -> CI
  -> merge to main
  -> Streamlit redeploys app code
```

Research data flow:

```text
research ingestion or admin tool
  -> Postgres
  -> dashboard reads approved records
```

## Deployment Rules

- Keep CI as the only GitHub workflow until deployment is stable.
- Do not add placeholder deploy jobs.
- Do not put research data in GitHub.
- Do not put secrets in GitHub.
- Keep database migrations or schema changes in pull requests.
- Apply production schema changes deliberately after review.
