import os
import pathlib
import shutil


def goto_workspace(arch: str, name: str) -> pathlib.Path:
    workspace = pathlib.Path('storage') / arch / name
    if not workspace.exists():
        workspace.mkdir()
    os.chdir(workspace)
    return pathlib.Path.cwd()


def check_program(program_name: str, path: pathlib.Path | None = None) -> pathlib.Path:
    program = shutil.which(program_name, path=path)
    if program is None:
        raise FileNotFoundError(f'Program `{program_name}` not found, please install it \
before proceeding')
    return pathlib.Path(program)
