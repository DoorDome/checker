from pathlib import Path


def is_file_for_style(path: str) -> bool:
    return not ("_deps" in Path(path).parts)