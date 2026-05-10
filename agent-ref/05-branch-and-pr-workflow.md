# Branch And PR Workflow

Default branch:

- `main`

`main` is protected on GitHub. Normal work should use:

```text
feature branch -> pull request -> merge into main
```

Preferred workflow:

1. Create a feature branch from the latest `main`.
2. Make scoped changes on that branch.
3. Commit only files relevant to the task.
4. Push the feature branch.
5. Open a pull request into `main`.
6. Merge through the PR after review.

Do not push directly to `main` for normal project work. The user remains repository admin and can override or repair the repo if needed.

When local uncommitted files exist, especially deleted generated presentations or user edits, do not stage them unless the user explicitly asks.

