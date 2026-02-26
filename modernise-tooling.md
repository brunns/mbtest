# Modernise mbtest tooling: tox → uv

*2026-02-26T10:59:10Z by Showboat 0.6.1*
<!-- showboat-id: 35c5217d-6748-46bc-96b8-e52a82dd49a7 -->

## Overview

This plan mirrors the tooling modernisation applied to brunns-matchers
(commit eb811b2607b98e25bbe17e8fdb4d4e243bb47c1e):

- Consolidate **setup.py + setup.cfg + tox.ini** into a single **pyproject.toml**
- Replace **tox** with **uv** for dependency management and test running
- Update **Makefile** to use uv commands
- Update **GitHub Actions CI** to use uv (astral-sh/setup-uv)
- Add an automated **release workflow** (tag-triggered, OIDC publish to PyPI)
- Update **dependabot.yml** to watch the uv ecosystem
- Generate **uv.lock**
- Delete the now-redundant setup.py, setup.cfg, tox.ini, and requirements.txt

mbtest-specific considerations vs brunns-matchers:
- CI must still install Node.js and Mountebank before running tests
- Docker (colima locally, Docker service in CI) is needed for integration tests
- Uses **pyright** for type checking, not mypy
- Has a Mountebank-version matrix job in CI that must be preserved

## Step 1 — Confirm current state

```bash
ls /Users/brunns/dev/brunns/mbtest/setup.py /Users/brunns/dev/brunns/mbtest/setup.cfg /Users/brunns/dev/brunns/mbtest/tox.ini /Users/brunns/dev/brunns/mbtest/requirements.txt /Users/brunns/dev/brunns/mbtest/pyproject.toml 2>&1
```

```output
/Users/brunns/dev/brunns/mbtest/pyproject.toml
/Users/brunns/dev/brunns/mbtest/requirements.txt
/Users/brunns/dev/brunns/mbtest/setup.cfg
/Users/brunns/dev/brunns/mbtest/setup.py
/Users/brunns/dev/brunns/mbtest/tox.ini
```

All five files exist. After this migration, setup.py, setup.cfg, tox.ini, and requirements.txt will be deleted, with everything consolidated into pyproject.toml.

## Step 2 — New pyproject.toml

Expand the existing pyproject.toml (currently only ruff config) to include:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mbtest"
version = "2.14.0"          # keep in sync; no longer scattered across setup.py
description = "Python wrapper & utils for the Mountebank over the wire test double tool."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [{ name = "Simon Brunning", email = "simon@brunn.ing" }]
classifiers = [ ... ]        # copy from setup.py

dependencies = [
    "pyhamcrest>=2.0",
    "Deprecated>=1.2",
    "brunns-matchers>=2.9",
    "yarl>=1.9",
    "httpx>=0.28",
]

[dependency-groups]
dev = [
    "pytest>=9.0",
    "pytest-docker~=3.1",
    "contexttimer>=0.3",
    "brunns-builder>=1.1",
    "trustme>=0.9",
    "furl>=2.0",
    "pytest-cov>=2.5",
    "sphinx>=3.0",
    "sphinx-autodoc-typehints>=1.10",
    "furo",
    "ruff",
    "pyright==1.1.391",
    "types-requests",
    "mutmut",
    "pipdeptree",
]

[project.urls]
Homepage = "https://github.com/brunns/mbtest/"
Repository = "https://github.com/brunns/mbtest/"
Issues = "https://github.com/brunns/mbtest/issues"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"*" = ["py.typed"]

[tool.pytest.ini_options]
log_cli = true

[tool.coverage.run]
branch = true
omit = ["*/matcher.py"]

[tool.coverage.report]
fail_under = 100
show_missing = true

[tool.mutmut]
paths_to_mutate = "src/"
backup = false
runner = "uv run pytest"
tests_dir = "tests/"
```

The existing ruff config blocks stay unchanged.

## Step 3 — Generate uv.lock

```bash
uv sync --all-groups
```

This creates uv.lock and installs the project into a .venv. The lock file is committed to the repo.

## Step 4 — New Makefile

Replace all tox invocations with uv equivalents. Key changes:

| Old | New |
|-----|-----|
| `tox -e py310,py314,pypy3.11` | `uv run pytest tests/unit/ tests/integration/` |
| `tox -e coverage` | `uv run pytest --cov src/mbtest --cov-report=term-missing` |
| `tox -e check-format` | `uv run ruff format . --check && uv run ruff check .` |
| `tox -e format` | `uv run ruff format . && uv run ruff check . --fix` |
| `tox -e pyright` | `uv run pyright src/` |
| `tox -e docs` | `uv run sphinx-build docs build_docs --color -W -bhtml` |
| `tox --recreate` | `uv sync --all-groups` |
| `tox -e py314 -- python` | `uv run python` |
| `tox -e py314 -- pip list -o` | `uv pip list --outdated` |

Add a new `sync` target:

```makefile
.PHONY: sync
sync: ## Install/sync dependencies
\tuv sync --all-groups
```

The `jsdeps` and `colima` targets remain unchanged — Mountebank still needs npm.

## Step 5 — Update GitHub Actions CI (.github/workflows/ci.yml)

Replace the pip+tox install pattern with uv in every job. Node.js and Mountebank
steps must be preserved since mbtest tests against a live mb server.

Per-job changes (replicated across all five jobs: test, test-py-versions,
test-mb-versions, test-oses, coverage):

```yaml
# Remove:
- name: Install build tools
  run: python3 -m pip install --upgrade pip setuptools wheel tox~=3.0

# Add:
- name: Install uv
  uses: astral-sh/setup-uv@v7
- name: Install dependencies
  run: uv sync --all-groups
```

Test run commands:

```yaml
# Remove:
run: tox -e py

# Add:
run: uv run pytest tests/unit/ tests/integration/
```

Coverage job:

```yaml
# Remove:
run: tox -e coverage

# Add:
run: uv run pytest --cov src/mbtest --cov-report=term-missing
```

lint-etc job (no Mountebank needed here):

```yaml
# Remove pip+tox install; add uv setup
# Remove: tox -e check-format / tox -e pyright / tox -e docs
# Add separate steps:
- run: uv run ruff format . --check
- run: uv run ruff check .
- run: uv run pyright src/
- run: uv run sphinx-build docs build_docs --color -W -bhtml
```

Also bump actions/checkout to v4 → already at v4; leave as-is or bump to v4.

## Step 6 — Add release workflow (.github/workflows/release.yml)

New workflow triggered on tag push matching `v*.*.*`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: write
  id-token: write    # required for OIDC PyPI publish

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.14' }
      - uses: actions/setup-node@v4
        with: { node-version: '24.x' }
      - run: npm install mountebank@2.9 --omit=dev
      - uses: astral-sh/setup-uv@v7
      - run: uv sync --all-groups
      - run: uv run pytest tests/unit/ tests/integration/
      - run: uv run pytest --cov src/mbtest --cov-report=term-missing
      - run: uv build
      - uses: actions/upload-artifact@v4
        with: { name: python-package-distributions, path: dist/ }

  publish-to-pypi:
    needs: build
    environment:
      name: pypi
      url: https://pypi.org/p/mbtest
    steps:
      - uses: actions/download-artifact@v4
        with: { name: python-package-distributions, path: dist/ }
      - uses: pypa/gh-action-pypi-publish@release/v1   # OIDC — no token needed

  github-release:
    needs: publish-to-pypi
    steps:
      - uses: actions/download-artifact@v4
        with: { name: python-package-distributions, path: dist/ }
      - run: gh release create '${{ github.ref_name }}' --repo '${{ github.repository }}' --generate-notes
      - run: gh release upload '${{ github.ref_name }}' dist/** --repo '${{ github.repository }}'
```

The manual release steps in README.md (using twine) should be simplified to:
tag the commit as `vN.N.N`, push the tag, and the workflow does the rest.

**Pre-requisite**: configure a `pypi` environment in GitHub repo settings with
OIDC trusted publishing enabled on PyPI.

## Step 7 — Update dependabot.yml

Replace the pip ecosystem entry with uv, and add a github-actions entry:

```yaml
version: 2
updates:
  - package-ecosystem: "uv"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "python"
    commit-message:
      prefix: "chore(deps)"
    open-pull-requests-limit: 10

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
    commit-message:
      prefix: "chore(ci)"
```

## Step 8 — Update README.md

The Releasing section currently documents a manual twine workflow. Replace it with:

```
## Releasing

Update the version number in pyproject.toml, commit, then:

```sh
version="n.n.n"
git checkout -b "release-$version"
make precommit && git commit -am"Release $version" && git push --set-upstream origin "release-$version"
git tag "v$version" && git push origin "v$version"
```

Pushing the tag triggers the release workflow, which builds, tests, publishes
to PyPI via OIDC, and creates the GitHub release automatically.

```

Also update the Contributing section to replace tox setup with uv:

```sh
brew install pyenv colima docker uv
pyenv install -s 3.10 3.14
pyenv local 3.10 3.14
colima status || colima start
uv sync --all-groups
npm install mountebank@2.9 --omit=dev
```

## Step 9 — Update CLAUDE.md

Revise the Commands section to reflect uv-based workflow (all the tox commands
become uv equivalents, as shown in the Makefile step above). Also note that
`make recreate` becomes `make sync` / `uv sync --all-groups`.

## Step 10 — Delete redundant files

```bash
rm setup.py setup.cfg tox.ini requirements.txt
```

Verify nothing else imports from these files before deleting.

## Step 11 — Smoke-test locally

```bash
uv sync --all-groups
uv run pytest tests/unit/        # fast, no Docker/mb needed
uv run ruff format . --check
uv run ruff check .
uv run pyright src/
```

Integration tests require Mountebank and Docker:

```bash
colima status || colima start
npm install mountebank@2.9 --omit=dev   # if not already installed
uv run pytest tests/unit/ tests/integration/
```

## Order of execution

1. pyproject.toml — add all project metadata + tool config
2. uv sync — generate uv.lock
3. Makefile — swap tox for uv
4. .github/workflows/ci.yml — swap pip+tox for uv (preserve Node/mb steps)
5. .github/workflows/release.yml — new file
6. .github/dependabot.yml — swap pip for uv + add github-actions
7. README.md — update Contributing and Releasing sections
8. CLAUDE.md — update Commands section
9. rm setup.py setup.cfg tox.ini requirements.txt
10. Smoke-test unit tests + linting locally

## Step 7a — Configure PyPI trusted publishing

Before the release workflow can publish to PyPI, a one-time setup is required
on PyPI's side. Add the following instructions to README.md under a new
"PyPI trusted publishing setup" subsection of Releasing:

### On PyPI

1. Log in to https://pypi.org and navigate to the mbtest project.
2. Go to **Manage → Publishing**.
3. Under **Add a new pending publisher**, fill in:
   - **PyPI project name**: mbtest
   - **Owner**: brunns
   - **Repository name**: mbtest
   - **Workflow name**: release.yml
   - **Environment name**: pypi
4. Click **Add**.

### On GitHub

In the repository **Settings → Environments**, create an environment named `pypi`.
No secrets are needed — OIDC handles authentication automatically.

Once both are configured, pushing a tag of the form `vN.N.N` is all that is
needed to trigger a fully automated build, test, PyPI publish, and GitHub
release.
