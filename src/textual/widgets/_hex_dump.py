from __future__ import annotations

import math
from rich.text import Text
from textual.geometry import Size
from textual.reactive import reactive
from textual.widget import Widget


class HexDump(Widget, can_focus=True):
    DEFAULT_CSS = "HexDump { height: auto; width: auto; background: $surface; color: $text; padding: 1 2; }"

    data: reactive[bytes] = reactive(b"")
    show_offset: reactive[bool] = reactive(True)
    show_ascii: reactive[bool] = reactive(True)
    bytes_per_line: reactive[int] = reactive(16)
    highlight_index: reactive[int | None] = reactive(None)

    def __init__(
        self,
        data: bytes = b"",
        *,
        show_offset: bool = True,
        show_ascii: bool = True,
        bytes_per_line: int = 16,
        highlight_index: int | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.data = data
        self.show_offset = show_offset
        self.show_ascii = show_ascii
        self.bytes_per_line = bytes_per_line
        self.highlight_index = highlight_index

    def render(self) -> Text:
        if not self.data:
            return Text("<empty data>", style="dim italic")

        lines: list[Text] = []

        for i in range(0, len(self.data), self.bytes_per_line):
            chunk = self.data[i : i + self.bytes_per_line]
            line = Text()

            # OFFSET
            if self.show_offset:
                line.append(f"{i:08X}  ")

            # HEX SECTION (fixed width)
            hex_parts = []
            for byte_offset, b in enumerate(chunk):
                global_index = i + byte_offset
                style = "reverse red" if global_index == self.highlight_index else None
                hex_parts.append((f"{b:02X}", style))

            # build hex string with correct spacing
            for idx, (hx, style) in enumerate(hex_parts):
                line.append(hx, style=style)
                if idx < self.bytes_per_line - 1:
                    line.append(" ")

            # pad missing bytes (VERY IMPORTANT for alignment)
            missing = self.bytes_per_line - len(chunk)
            if missing > 0:
                line.append("   " * missing)

            # ASCII SECTION
            if self.show_ascii:
                line.append("  |")
                for byte_offset, b in enumerate(chunk):
                    global_index = i + byte_offset
                    char = chr(b) if 32 <= b <= 126 else "."
                    style = "reverse red" if global_index == self.highlight_index else None
                    line.append(char, style=style)
                line.append("|")

            lines.append(line)

        # SAFE JOIN (NO Text.join)
        result = Text()
        for idx, line in enumerate(lines):
            if idx:
                result.append("\n")
            result.append(line)

        return result

    def get_content_width(self, container: Size, viewport: Size) -> int:
        width = 0

        if self.show_offset:
            width += 10  # 8 hex + 2 spaces

        # hex section width (fixed)
        width += (self.bytes_per_line * 3) - 1

        if self.show_ascii:
            width += 4 + self.bytes_per_line  # "  |" + chars + "|"

        return width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        if not self.data:
            return 1
        return math.ceil(len(self.data) / self.bytes_per_line)
