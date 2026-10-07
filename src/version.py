import tomli

try:
    with open("pyproject.toml", "rb") as project_file:
        __version__ = tomli.load(project_file)["project"]["version"]
except (KeyError, OSError, tomli.TOMLDecodeError) as e:
    print(e)
    __version__ = "test"
