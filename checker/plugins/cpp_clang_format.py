from __future__ import annotations

from pathlib import Path

from checker.exceptions import PluginExecutionFailed
from checker.plugins.cpp.blacklist import get_cpp_blacklist
from checker.plugins.cpp.style_path import is_file_for_style
from checker.plugins.firejail import SafeRunScriptPlugin
from checker.utils import print_info

from .base import PluginABC, PluginOutput


class CppClangFormatPlugin(PluginABC):
    name = "cpp_clang_format"

    class Args(PluginABC.Args):
        reference_root: Path
        task_path: Path
        lint_patterns: list[str]

    # type: ignore[override]
    def _run(self, args: Args, *, verbose: bool = False) -> PluginOutput:
        lint_files = []
        for f in args.lint_patterns:
            lint_files += list([p for p in map(str,
                               args.task_path.glob(f)) if is_file_for_style(p)])
        lint_files = list(set(lint_files))

        if not lint_files:
            raise PluginExecutionFailed("No files")

        run_args = SafeRunScriptPlugin.Args(
            origin=str(args.reference_root),
            script=["python3", "run-clang-format.py",
                    "--color", "always", "-r", *lint_files],
            paths_blacklist=get_cpp_blacklist(args.reference_root),
        )
        output = SafeRunScriptPlugin()._run(run_args, verbose=verbose).output
        print_info(output)
        return PluginOutput(output="[No issues]")
