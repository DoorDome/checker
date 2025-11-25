from __future__ import annotations

import pathlib
import subprocess

from checker.utils import print_info

from .base import PluginABC, PluginOutput


class LoadDepsPlugin(PluginABC):
    name = "load_deps"

    class Args(PluginABC.Args):
        deps: list[str]
        root: str
        task_path: str

    # type: ignore[override]
    def _run(self, args: Args, *, verbose: bool = False) -> PluginOutput:
        LoadDepsPlugin._load_deps(
            deps=args.deps,
            root=args.root,
            task_path=args.task_path,
            verbose=verbose,
        )
        return PluginOutput(output="Dependencies were updated")

    @staticmethod
    def _load_deps(
        deps: list[str], root: str, task_path: str, verbose: bool = False
    ) -> None:
        remote = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
            cwd=root
        ).stdout.strip()

        for dep in deps:
            dep_branch = f"submit/{dep}"
            dep_path = pathlib.Path(task_path) / "_deps" / dep
            if verbose:
                print_info(f"Clone branch {dep_branch} at {str(dep_path)}\n")

            subprocess.run(
                ["git", "clone", "--branch", dep_branch, remote, str(dep_path)],
                capture_output=True,
                text=True,
                check=True,
                cwd=root
            )
