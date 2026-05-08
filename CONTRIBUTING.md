# Contributing Guidelines

Thank you for contributing to the ATLS Enterprise Farm ERP. This project uses a strict engineering governance model to ensure stability and maintainability.

## Development Constraints

1. **Incremental Changes:** Do not submit repository-wide formatting sweeps. Keep PRs small and focused on the feature or bug fix. Legacy technical debt should be cleaned up gradually within the files you touch.
2. **Architecture Compliance:** Review the architecture documents in `docs/00-core/` before introducing new dependencies, patterns, or data structures.
3. **Frontend Rules:** 
   - No direct `axios` or `fetch` calls inside React Components or Pages. Use the dedicated `services/` layer.
   - Use the pre-commit hooks to format files (`npm run lint:staged` is run automatically).
4. **Backend Rules:** 
   - Maintain standard Django App boundaries and avoid cross-domain coupling.
   - Ruff handles linting. Pre-commit hooks will check your staged files.

## PR Process

1. Create a branch logically named, e.g., `feat/name`, `fix/name`, or `chore/name`.
2. Commit in logical, functional chunks.
3. Ensure the GitHub Actions CI pipeline passes on your branch before requesting review.
4. Fill out the Pull Request template completely to aid reviewers.
