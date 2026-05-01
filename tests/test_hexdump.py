import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

async def test_hexdump_comprehensive_behavior():
    class HexDumpApp(App):
        def compose(self):
            # 20 bytes of data to test multiple lines with bytes_per_line=16
            yield HexDump(b"A" * 20, highlight_index=17)

    app = HexDumpApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        
        # (g) Proper scrolling via get_content_width/get_content_height
        width = widget.get_content_width(Size(80, 24), Size(80, 24))
        height = widget.get_content_height(Size(80, 24), Size(80, 24), width)
        assert height == 2, "Data length 20 with 16 bytes_per_line should be 2 lines"
        assert width == 77, "Expected width for full features: 10(offset) + 47(hex) + 20(ascii)"

        text_result = widget.render()
        plain_text = text_result.plain
        
        # (d) bytes_per_line layout and multi-line rendering
        # (f) Exact 8-digit offset format and spacing
        assert "00000000  " in plain_text
        assert "00000010  " in plain_text
        
        # (b) ASCII representation wrapped in | |
        assert "|AAAAAAAAAAAAAAAA|" in plain_text
        assert "|AAAA|" in plain_text

        # (c) required colors (cyan, green, yellow)
        # (a) Highlighting behavior styled as reverse red
        styles = [str(span.style) for span in text_result.spans]
        assert "cyan" in styles
        assert "green" in styles
        assert "yellow" in styles
        assert "reverse red" in styles
        
        # Count the highlights to ensure it hit both columns
        highlight_count = sum(1 for style in styles if style == "reverse red")
        assert highlight_count == 2, "Highlight should apply to both Hex and ASCII sections"

        # (e) default property values and toggling show_offset/show_ascii
        widget.show_offset = False
        widget.show_ascii = False
        toggled_result = widget.render()
        toggled_plain = toggled_result.plain
        
        assert "00000000  " not in toggled_plain
        assert "|AAAA|" not in toggled_plain
        assert "41 41 41" in toggled_plain  # hex should still be there
        
        # Dimension width should shrink after toggling
        shrunk_width = widget.get_content_width(Size(80, 24), Size(80, 24))
        assert shrunk_width == 47, "Width should just be hex data now"
        
        # Change bytes_per_line to test dynamic height updates
        widget.bytes_per_line = 10
        new_height = widget.get_content_height(Size(80, 24), Size(80, 24), shrunk_width)
        assert new_height == 2, "Data length 20 with 10 bytes_per_line should be 2 lines"
