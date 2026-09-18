# FALL3DUTIL Package

fall3dutil is an open source project and Python package that includes a set of utilities for downloading and pre-processing the meteorological fields required by the FALL3D model.

## Testing and releasing with `uv`

The commands below should be run from the repository root.

This project uses `uv` for local testing, building, and releasing. Use a project-local `.venv` environment to avoid modifying the system Python installation or another unrelated virtual environment.

### 1. Create the project `.venv`

Create the virtual environment:

```bash
uv venv
```

This creates a local environment at:

```text
.venv/
```

You do not need to activate it if you use `uv run` and `uv pip`, but you may activate it if desired:

```bash
source .venv/bin/activate
```

If another environment is already active, for example `.my_env`, deactivate it first to avoid confusion:

```bash
deactivate
```

Then check that `uv` is using the project environment:

```bash
uv run python --version
```

### 2. Install the package locally

Install the package into the `.venv` environment:

```bash
uv pip install .
```

For editable local development/testing, use:

```bash
uv pip install -e .
```

Editable mode links the installed package to the local source tree, so changes in `src/` are picked up without reinstalling.

### 3. Test the package locally

Run basic checks:

```bash
uv run python tests/carra_sfc.py --help
uv run python tests/carra_pl.py --help
uv run python tests/carra_ml.py --help
uv run python tests/cerra_sfc.py --help
uv run python tests/cerra_pl.py --help
uv run python tests/cerra_ml.py --help
```

For quick source-tree testing without installing the package, use:

```bash
PYTHONPATH=src uv run python tests/cerra_sfc.py --help
```

A real download test can be run with valid CDS credentials, for example:

```bash
uv run python tests/cerra_sfc.py \
  --date 20180918 20180919 \
  --lon -10 10 \
  --lat 35 45 \
  --res 0.1 \
  --step 3 \
  --format grib \
  --verbose
```

### 4. Clean old build artifacts

Before building a new release, remove old build outputs:

```bash
rm -rf dist/ build/ src/*.egg-info
```

This avoids accidentally uploading files from previous releases.

### 5. Update the version

Before building, update the package version in `pyproject.toml`:

```toml
[project]
version = "x.y.z"
```

PyPI does not allow uploading the same version twice.

### 6. Build the package

Use `build` as a one-off tool through `uv`:

```bash
uv run --with build python -m build
```

This creates new source distribution and wheel files under `dist/`.

### 7. Check the built distributions

Use `twine` as a one-off tool through `uv`:

```bash
uv run --with twine python -m twine check dist/*
```

Only continue if the check passes.

### 8. Upload to PyPI

Upload the new files with `twine` through `uv`:

```bash
uv run --with twine python -m twine upload --verbose dist/*
```

This is safe if `dist/` was cleaned before building. Otherwise, `dist/*` may include older release files.
