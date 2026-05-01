from __future__ import annotations

import math
from rich.text import Text
from textual.geometry import Size
from textual.reactive import reactive
from textual.widget import Widget

class HexDump(Widget, can_focus=True):
    """A widget to display binary data in a hex dump format."""

    DEFAULT_CSS = """
    HexDump {
        height: auto;
        width: auto;
        background: $surface;
        color: $text;
        padding: 1 2;
    }
    """

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

        lines = []
        for i in range(0, len(self.data), self.bytes_per_line):
            chunk = self.data[i : i + self.bytes_per_line]
            line_text = Text()

            # 1. Offset: 8-digit cyan hex + exactly two spaces
            if self.show_offset:
                line_text.append(f"{i:08X}  ", style="cyan")

            # 2. Hex Data: Two-digit green strings + single space
            for byte_offset, b in enumerate(chunk):
                global_index = i + byte_offset
                hex_str = f"{b:02X}"
                style = "reverse red" if global_index == self.highlight_index else "green"
                line_text.append(hex_str, style=style)
                
                # Single space between hex pairs, but not after the last byte of the chunk
                if byte_offset < len(chunk) - 1:
                    line_text.append(" ")

            # 3. Padding and ASCII Section
            if self.show_ascii:
                # Pad the hex section if the line is incomplete to keep ASCII aligned
                missing_bytes = self.bytes_per_line - len(chunk)
                if missing_bytes > 0:
                    # 3 spaces per missing byte (2 for hex digits + 1 for separator)
                    line_text.append("   " * missing_bytes)
                
                # Exactly two spaces before the pipe
                line_text.append("  |", style="dim")
                for byte_offset, b in enumerate(chunk):
                    global_index = i + byte_offset
                    # Printable characters (32-126), others are dots
                    char = chr(b) if 32 <= b <= 126 else "."
                    style = "reverse red" if global_index == self.highlight_index else "yellow"
                    line_text.append(char, style=style)
                line_text.append("|", style="dim")

            lines.append(line_text)

        return Text("\n").join(lines)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        width = 0
        if self.show_offset:
            width += 10 # 8 digits + 2 spaces
        
        # Hex portion width
        width += (self.bytes_per_line * 3) - 1
        
        if self.show_ascii:
            width += 4 + self.bytes_per_line # 2 spaces + 2 pipes + chars
        return width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        if not self.data:
            return 1
        return math.ceil(len(self.data) / self.bytes_per_line)
