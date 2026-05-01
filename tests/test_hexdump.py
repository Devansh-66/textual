import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_comprehensive_behavior():
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
        assert "00000000  48 65 6C 6C 6F 01 57 6F 72 6C 64 21 31 32 33 34" in plain
        assert "  |Hello.World!1234|" in plain

        # 2. Verify Highlighting logic
        styles = [str(span.style) for span in text_result.spans]
        highlight_count = sum(1 for s in styles if "reverse red" in s)
        assert highlight_count == 2, "Highlight index 0 should appear in hex and ascii"

        # 3. Verify Toggling Mutability (show_offset and show_ascii)
        widget.show_offset = False
        widget.show_ascii = False
        toggled_plain = widget.render().plain
        assert "00000000" not in toggled_plain
        assert "|" not in toggled_plain
