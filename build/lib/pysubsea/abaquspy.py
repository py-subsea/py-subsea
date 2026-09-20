"""
This module provides functionality to create Abaqus sensitivity files by replacing
parameter fields in an Abaqus template file and executing embedded Python blocks.

Features
--------
 - The `AbaqusSensitivity` class orchestrates the full process end-to-end.
 - Designed to generate sensitivity inputs from a master Abaqus template.
 - Designed for finite element sensitivity studies and parameter sweeps with
   Abaqus .inp files.

.. raw:: html

     <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

"""

from __future__ import annotations

import builtins
import re
import textwrap

class AbaqusSensitivity:
    """
    Class to create sensitivity files by replacing parameter fields in a master template file.

    Parameters
    ----------
    template_filename : str
        The base name of the Abaqus template file (without .inp extension).
    sensitivity_filename : str
        The base name for the output sensitivity files.
    param_dict : dict
        Dictionary mapping parameter names to lists of values.
    isens : int
        Index of the sensitivity case to use from param_dict values.
    """

    def __init__(self, *, template_filename: str, sensitivity_filename: str, param_dict: dict, isens: int):
        self.template_filename = template_filename
        self.sensitivity_filename = sensitivity_filename
        self.param_dict = param_dict
        self.isens = isens
        self.lines: list[str] = []
        self.replaced_lines: list[str] | None = None

    @staticmethod
    def _compile_inline_expression(pattern: re.Pattern[str], namespace: dict, line: str) -> str:
        def replacer(match: re.Match[str]) -> str:
            expression = match.group(1)
            evaluator = getattr(builtins, "eval")
            return str(evaluator(expression, namespace, namespace))

        return pattern.sub(replacer, line)

    @staticmethod
    def _is_python_start(line: str) -> bool:
        stripped = line.strip()
        return (
            stripped.startswith("<py")
            or stripped == r"**\start_python"
            or stripped == r"**\start_python_global"
        )

    @staticmethod
    def _is_python_end(line: str) -> bool:
        stripped = line.strip()
        return stripped in {"py>", r"**\end_python", r"**\end_python_global"}

    @staticmethod
    def _translate_block_line(line: str) -> str:
        stripped = line.lstrip()
        indentation = line[: len(line) - len(stripped)]

        if not stripped:
            return ""

        if stripped.startswith("$"):
            content = stripped[1:]
            if not content:
                return ""
            leading_space = " " if content[:1].isspace() else ""
            escaped_content = content.lstrip().replace("\\", "\\\\").replace('"', '\\"')
            return f'{indentation}write(f"{leading_space}{escaped_content}\\n")'

        if stripped.startswith("writeLine +="):
            rhs = stripped.split("+=", 1)[1].strip()
            return f"{indentation}write({rhs})"

        return line.rstrip("\n")

    def _render_text_line(self, line: str, namespace: dict) -> str:
        inline_pattern = re.compile(r"\$\s*\{([^{}]+)\}")

        stripped = line.lstrip()
        if stripped.startswith("$"):
            content = stripped[1:]
            leading_space = " " if content[:1].isspace() else ""
            content = content.lstrip()

            def brace_replacer(match: re.Match[str]) -> str:
                expression = match.group(1)
                evaluator = getattr(builtins, "eval")
                return str(evaluator(expression, namespace, namespace))

            rendered = re.sub(r"\{([^{}]+)\}", brace_replacer, content)
            return leading_space + rendered

        return self._compile_inline_expression(inline_pattern, namespace, line)

    def _extract_python_block(self, start_index: int) -> tuple[list[str], int]:
        start_line = self.replaced_lines[start_index]
        stripped = start_line.strip()

        if stripped.startswith("<py"):
            single_line_match = re.match(r"^\s*<py(?:\s+(.*?))?\s*py>\s*$", start_line)
            if single_line_match:
                body = (single_line_match.group(1) or "").strip()
                return ([body] if body else []), start_index + 1

            body_lines: list[str] = []
            remainder = start_line[start_line.find("<py") + 3 :]
            if remainder.strip():
                body_lines.append(remainder.rstrip("\n"))

            current = start_index + 1
            while current < len(self.replaced_lines):
                candidate = self.replaced_lines[current]
                if candidate.strip() == "py>":
                    return body_lines, current + 1
                body_lines.append(candidate.rstrip("\n"))
                current += 1

            raise ValueError("Missing 'py>' terminator for '<py' block.")

        if stripped == r"**\start_python_global":
            end_marker = r"**\end_python_global"
        elif stripped == r"**\start_python":
            end_marker = r"**\end_python"
        else:
            raise ValueError(f"Unrecognized Python block start: {start_line!r}")

        body_lines = []
        current = start_index + 1
        while current < len(self.replaced_lines):
            candidate = self.replaced_lines[current]
            if candidate.strip() == end_marker:
                return body_lines, current + 1
            body_lines.append(candidate.rstrip("\n"))
            current += 1

        raise ValueError(f"Missing {end_marker!r} terminator for Python block.")

    def _build_execution_namespace(self) -> tuple[dict, list[str]]:
        output_lines: list[str] = []

        def write(*parts: object) -> None:
            text = "".join(str(part) for part in parts)
            output_lines.append(text)

        namespace = {
            "__builtins__": __builtins__,
            "write": write,
            "emit": write,
            "pysubsea_write": write,
            "abaqus_write": write,
        }
        return namespace, output_lines

    def _render_template(self) -> list[str]:
        namespace, output_lines = self._build_execution_namespace()
        current = 0

        while current < len(self.replaced_lines):
            line = self.replaced_lines[current]

            if self._is_python_start(line):
                block_lines, current = self._extract_python_block(current)
                translated_lines = [self._translate_block_line(block_line) for block_line in block_lines]
                code = "\n".join(translated_lines)
                code = textwrap.dedent(code).strip("\n")
                if code.strip():
                    executor = getattr(builtins, "exec")
                    executor(compile(code, f"{self.template_filename}.inp", "exec"), namespace, namespace)
                continue

            if self._is_python_end(line):
                raise ValueError(f"Unexpected Python block terminator: {line!r}")

            output_lines.append(self._render_text_line(line, namespace))
            current += 1

        return output_lines

    def _read_template(self) -> None:
        with open(f"{self.template_filename}.inp", "r", encoding="utf-8") as file_old:
            self.lines = file_old.readlines()

    def _replace_parameters(self) -> None:
        if not self.param_dict:
            self.replaced_lines = list(self.lines)
            return

        def replacer(match: re.Match[str]) -> str:
            return str(self.param_dict[match.group(0)][self.isens])

        pattern = re.compile("|".join(re.escape(k) for k in self.param_dict.keys()))
        self.replaced_lines = [pattern.sub(replacer, line) for line in self.lines]

    def run(self) -> None:
        """Run the full process and write the final sensitivity file."""
        self._read_template()
        self._replace_parameters()
        rendered_lines = self._render_template()
        with open(f"{self.sensitivity_filename}.inp", "w", encoding="utf-8") as sens_file:
            sens_file.writelines(rendered_lines)
