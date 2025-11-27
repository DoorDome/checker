from __future__ import annotations

from pathlib import Path

from checker.exceptions import PluginExecutionFailed
from checker.plugins.cpp.blacklist import get_cpp_blacklist
from checker.plugins.cpp.style_path import is_file_for_style
from checker.plugins.firejail import SafeRunScriptPlugin
from checker.utils import print_info

from .base import PluginABC, PluginOutput


class CppForbiddenPlugin(PluginABC):
    name = "cpp_forbidden"

    class Args(PluginABC.Args):
        reference_root: Path
        task_path: Path
        allow_change: list[str]
        lint_patterns: list[str]
        white_list: list[str]
        forbidden: list[str] = []
        forbidden_files: list[str] = []
        forbidden_checker: str

    # type: ignore[override]
    def _run(self, args: Args, *, verbose: bool = False) -> PluginOutput:
        changed_files: set[str] = set()
        for r in args.allow_change:
            changed_files |= set([p for p in map(str,
                                  args.task_path.glob(r))])
        lint_files: set[str] = set()
        for r in args.lint_patterns:
            lint_files |= set([p for p in map(str,
                               args.task_path.glob(r)) if is_file_for_style(p)])
        white_files: set[str] = set()
        for r in args.white_list:
            white_files |= set([p for p in map(str, args.task_path.glob(r))])
        files = list(changed_files.intersection(
            lint_files).difference(white_files))

        forbidden: list[str] = []
        for f in args.forbidden:
            forbidden += ["-f", f]
        for f in args.forbidden_files:
            forbidden += ["-ff", f]

        checker_args = forbidden + files
        if not checker_args:
            raise PluginExecutionFailed("No arguments for the checker")

        run_args = SafeRunScriptPlugin.Args(
            origin=str(args.reference_root / "build-relwithdebinfo"),
            script=[args.forbidden_checker, "-p", ".", *checker_args],
            paths_whitelist=[str(args.reference_root)],
            paths_blacklist=get_cpp_blacklist(args.reference_root),
        )
        output = SafeRunScriptPlugin()._run(run_args, verbose=verbose).output
        print_info(output)
        return PluginOutput(output="[No issues]")
