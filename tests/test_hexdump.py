import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_comprehensive_behavior():
    # 20 bytes of data (Line 1: 16 bytes, Line 2: 4 bytes by default)
    data = b"Hello" + b"\x01" + b"World!" + b"12345678"
    
    class HexDumpApp(App):
        def compose(self):
            yield HexDump(data, highlight_index=0)

    app = HexDumpApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        
        # 1. Verify Hex Formatting & Exact Spacing
        text_result = widget.render()
        plain = text_result.plain
        # Check first line: Offset(8) + 2 spaces + Hex values + 2 spaces + |16 chars|
        assert "00000000  48 65 6C 6C 6F 01 57 6F 72 6C 64 21 31 32 33 34" in plain
        assert "  |Hello.World!1234|" in plain

        # 2. Verify Dimensions (Required for scrolling)
        # Default is 16 bytes/line. 20 bytes should span 2 lines.
        width = widget.get_content_width(Size(80, 24), Size(80, 24))
        height = widget.get_content_height(Size(80, 24), Size(80, 24), width)
        assert height == 2, "20 bytes should span 2 lines at 16 bytes/line"
        assert width > 0

        # 3. Verify bytes_per_line Reactive & Multi-line Rendering
        widget.bytes_per_line = 8
        # 20 bytes at 8 bytes/line should now span 3 lines (8+8+4)
        new_height = widget.get_content_height(Size(80, 24), Size(80, 24), width)
        assert new_height == 3, "20 bytes should span 3 lines at 8 bytes/line"
        
        # Verify the second line offset exists in the new render
        new_render = widget.render().plain
        assert "00000008  " in new_render

        # 4. Verify Highlighting logic (Rich Spans)
        styles = [str(span.style) for span in text_result.spans]
        highlight_count = sum(1 for s in styles if "reverse red" in s)
        assert highlight_count == 2, "Highlight index 0 should appear in hex and ascii"

        # 5. Verify Toggling Mutability (show_offset)
        widget.show_offset = False
        assert "00000000" not in widget.render().plain
