from __future__ import annotations

from pathlib import Path

import yaml
from click.testing import CliRunner

from checker.__main__ import cli
from checker.configs.manytask import ManytaskConfig


def test_export_private_with_review_config(tmp_path: Path) -> None:
    """Exercise the Docker build command with the review-process YAML contract."""
    source = tmp_path / "source"
    source.mkdir()
    stages = [["written"], ["oral", "written"], ["oral"], ["written", "oral"]]
    tasks = [{"task": f"task{i}", "score": 10, "review_stages": value} for i, value in enumerate(stages)]
    config = {
        "version": 1,
        "settings": {
            "course_name": "test",
            "gitlab_base_url": "https://gitlab.example.com",
            "public_repo": "course/public",
            "students_group": "course/students",
        },
        "ui": {"task_url_template": "https://gitlab.example.com/$TASK_NAME"},
        "deadlines": {
            "timezone": "UTC",
            "oral_attempt_limit": 5,
            "schedule": [
                {"group": "group", "start": "2020-01-01 00:00:00", "end": "2100-01-01 00:00:00", "tasks": tasks},
            ],
        },
    }
    (source / ".manytask.yml").write_text(yaml.safe_dump(config))
    (source / ".checker.yml").write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "structure": {"private_patterns": [".manytask.yml", ".checker.yml", ".task.yml", "private.txt"]},
                "export": {"destination": "https://gitlab.example.com/course/public"},
                "testing": {},
            }
        )
    )
    for task in tasks:
        folder = source / task["task"]
        folder.mkdir()
        (folder / ".task.yml").write_text("version: 1\n")
        (folder / "private.txt").write_text("private test data")

    destination = tmp_path / "export"
    result = CliRunner().invoke(cli, ["export-private", str(source), str(destination)])
    assert result.exit_code == 0, result.output
    exported = ManytaskConfig.from_yaml(destination / ".manytask.yml")
    assert exported.deadlines.oral_attempt_limit == 5
    assert [task.model_dump(mode="json")["review_stages"] for task in exported.get_tasks()] == stages
    for task in tasks:
        assert (destination / task["task"] / "private.txt").read_text() == "private test data"
