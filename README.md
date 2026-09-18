# FALL3DUTIL Package

fall3dutil is an open source project and Python package that includes a set of utilities for downloading and pre-processing the meteorological fields required by the FALL3D model

## Testing and releasing

The commands below should be run from the repository root.

### 1. Create and activate a virtual environment

It is recommended to build and test the package inside a virtual environment, not in the system Python installation.

Using the standard library `venv`:

```bash
python3 -m venv /path/to/my/env
source /path/to/my/env/bin/activate
```

After activation, check that you are inside the expected environment:

```bash
which python
which pip
```

When the virtual environment is active, commands such as:

```bash
python3 -m pip install .
python3 -m pip install --upgrade build twine
```

modify only that virtual environment. They do not install the package into the system Python.

If no virtual environment is active, these commands may modify your user/system Python environment, depending on your Python and pip configuration.

### 2. If using `uv`

If you use `uv`, prefer running commands through the `uv` environment instead of using global `pip`.

For example:

```bash
uv venv
uv pip install .
```

or run commands directly with:

```bash
uv run python tests/cerra_sfc.py --help
```

With `uv`, packages are installed into the project environment managed by `uv`, typically `.venv`, rather than into the system Python.

For editable local development/testing, you can use:

```bash
uv pip install -e .
```

Editable mode links the installed package to the local source tree, so changes in `src/` are picked up without reinstalling.

### 3. Test the package locally

Install the package into the active environment:

```bash
python3 -m pip install .
```

Then run basic checks, for example:

```bash
python tests/carra_sfc.py --help
python tests/carra_pl.py --help
python tests/carra_ml.py --help
python tests/cerra_sfc.py --help
python tests/cerra_pl.py --help
python tests/cerra_ml.py --help
```

For quick source-tree testing without installing the package, you can also use:

```bash
PYTHONPATH=src python tests/cerra_sfc.py --help
```

A real download test can be run with valid CDS credentials, for example:

```bash
python tests/cerra_sfc.py \
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

Install or upgrade the build tool inside the active environment:

```bash
python3 -m pip install --upgrade build
```

Build the source distribution and wheel:

```bash
python3 -m build
```

This creates new files under `dist/`.

### 7. Check the built distributions

Install or upgrade `twine`:

```bash
python3 -m pip install --upgrade twine
```

Check the generated files:

```bash
python3 -m twine check dist/*
```

Only continue if the check passes.

### 8. Upload to PyPI

Upload the new files:

```bash
python3 -m twine upload --verbose dist/*
```

This is safe if `dist/` was cleaned before building. Otherwise, `dist/*` may include older release files.
