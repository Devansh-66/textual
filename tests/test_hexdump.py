import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_comprehensive_behavior():
    # 20 bytes: Line 1 (16 bytes), Line 2 (4 bytes)
    data = b"Hello" + b"\x01" + b"World!" + b"12345678"
    
    class HexDumpApp(App):
        def compose(self):
            yield HexDump(data, highlight_index=0)

    app = HexDumpApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        
        # 1. Verify Hex Formatting & Spacing
        text_result = widget.render()
        plain = text_result.plain
        # Check first line: Offset(8) + 2 spaces + Hex(16*2 + 15 spaces)
        assert "00000000  48 65 6C 6C 6F 01 57 6F 72 6C 64 21 31 32 33 34" in plain
        # Check ASCII: 2 spaces + | + 16 chars + |
        assert "  |Hello.World!1234|" in plain

        # 2. Verify Colors (Rich Spans)
        styles = [str(span.style) for span in text_result.spans]
        assert any("cyan" in s for s in styles), "Offset should be cyan"
        assert any("green" in s for s in styles), "Hex data should be green"
        assert any("yellow" in s for s in styles), "ASCII should be yellow"
        assert any("reverse red" in s for s in styles), "Highlight should be reverse red"

        # 3. Verify bytes_per_line option
        widget.bytes_per_line = 8
        width = widget.get_content_width(Size(80, 24), Size(80, 24))
        height = widget.get_content_height(Size(80, 24), Size(80, 24), width)
        assert height == 3, "20 bytes with 8 per line should be 3 lines"

        # 4. Verify Toggling (Mutable properties)
        widget.show_offset = False
        widget.show_ascii = False
        toggled_plain = widget.render().plain
        assert "00000000" not in toggled_plain
        assert "|" not in toggled_plain
