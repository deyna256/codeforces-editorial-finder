# Contributing to Codeforces Editorial Finder

Thank you for your interest in contributing! 🎉

## Getting Started

1. **Fork the repository** (so you don't clutter the main repository)
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/codeforces-editorial-finder.git
   cd codeforces-editorial-finder
   ```

3. **Install dependencies**
   ```bash
   uv sync --group dev
   uv run playwright install chromium
   ```

## Development Workflow

### 1. Create a branch for your issue

Branch name should match the issue number:

```bash
git checkout -b 42  # For issue #42
```

### 2. Make your changes

- Write clean, readable code
- Follow existing code style
- Add tests if applicable
- If you opened a PR but are still working on it, add **WIP** to the PR title.

### 3. Commit your changes

Start each commit message with the issue number to maintain clear traceability:

```bash
git commit -m "#42: Add support for custom wait time"
```

### 4. Run checks locally

Before pushing, ensure all checks pass. Maintainers may ignore PRs with failing checks.
Command for tests and style are in `Justfile`:

```bash
just format    # Keep code formatted
just lint      # Run linting
just typecheck # Type checking
just test      # Run tests
```

### 5. Push and create a Pull Request

```bash
git push origin 42
```

Then open a PR targeting the `main` branch.

## Pull Request Guidelines

- **Title**: Brief description (add **WIP** if not finished)
- **Description**:
  - Reference the issue: `Resolve #42` or `Closes #42`
  - Explain what and why
- **Checks**: All checks must be green ✅
- **Review**: Tag the maintainers once you've finished your work and are ready for review

Open an issue or ask in your PR! We're here to help. 🚀
