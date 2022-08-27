from pathlib import Path


def get_project_dir() -> Path:
    current_path = Path().absolute()
    parts = current_path.parts
    dir_index = parts.index("beer-scraper")
    project_path = Path(*parts[: dir_index + 1])
    return project_path
