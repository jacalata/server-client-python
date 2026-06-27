try:
    import tomllib
except ImportError:
    import tomli as tomllib

from pathlib import Path
import importlib.metadata

with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
    toml = tomllib.load(f)

project = toml["project"]["name"]
release = importlib.metadata.version(project)
version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = []
