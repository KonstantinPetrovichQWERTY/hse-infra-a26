import tomli


def get_service_name():
    """Retrieves the service name from project metadata."""
    try:
        with open("pyproject.toml", "rb") as project_file:
            name = tomli.load(project_file)["project"]["name"]
    except (KeyError, OSError, tomli.TOMLDecodeError) as e:
        print(e)
        name = "test-name"
    return name
