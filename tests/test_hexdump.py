import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_comprehensive():
    # 20 bytes to test multi-line wrapping (16 per line)
    data = b"Hello" + b"\x01" + b"World!" + b"12345678"
    
    class HexDumpApp(App):
        def compose(self):
            yield HexDump(data, show_offset=True, show_ascii=True, highlight_index=0)

    app = HexDumpApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        
        # 1. Verify exact 8-digit offset and 2-space gap
        text_result = widget.render()
        plain = text_result.plain
        assert "00000000  " in plain
        assert "00000010  " in plain
        
        # 2. Verify ASCII wrapping and 2-space leading gap
        assert "  |Hello.World!123|" in plain
        
        # 3. Verify Highlighting in both columns (index 0 is 'H')
        styles = [str(span.style) for span in text_result.spans]
        highlight_count = sum(1 for s in styles if "reverse red" in s)
        assert highlight_count == 2
        
        # 4. Verify Multi-line dimensions
        width = widget.get_content_width(Size(80, 24), Size(80, 24))
        height = widget.get_content_height(Size(80, 24), Size(80, 24), width)
        assert height == 2
        
        # 5. Verify Toggling show_offset and show_ascii
        widget.show_offset = False
        widget.show_ascii = False
        toggled_plain = widget.render().plain
        assert "00000000" not in toggled_plain
        assert "|" not in toggled_plain
