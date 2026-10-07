import tomli


def _load_project_metadata() -> dict[str, str]:
    """Load project metadata from pyproject.toml."""
    try:
        with open("pyproject.toml", "rb") as project_file:
            project = tomli.load(project_file)["project"]
        return {
            "name": project["name"],
            "version": project["version"],
        }
    except (KeyError, OSError, tomli.TOMLDecodeError) as error:
        print(error)
        return {"name": "test-name", "version": "test"}


_PROJECT_METADATA = _load_project_metadata()
__version__ = _PROJECT_METADATA["version"]


def get_service_name() -> str:
    """Return the service name from project metadata."""
    return _PROJECT_METADATA["name"]
