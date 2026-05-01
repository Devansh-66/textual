import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_comprehensive_behavior():
    # 20 bytes: Line 1 (0-15), Line 2 (16-19)
    data = b"Hello" + b"\x01" + b"World!" + b"12345678"
    
    class HexDumpApp(App):
        def compose(self):
            yield HexDump(data, highlight_index=5)

    app = HexDumpApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        
        # 1. Verify Layout & Multi-line offsets
        render = widget.render()
        plain = render.plain
        assert plain.startswith("00000000  48 65 6C 6C 6F 01 57 6F 72 6C 64 21 31 32 33 34")
        assert "  |Hello.World!1234|" in plain
        assert "00000010  35 36 37 38" in plain

        # 2. Verify Highlighting (Checking Rich spans for 'reverse red')
        styles = [str(span.style) for span in render.spans]
        assert any("reverse red" in s for s in styles)

        # 3. Verify Reactive Toggling
        widget.show_offset = False
        assert "00000000" not in widget.render().plain
        
        widget.show_ascii = False
        assert "|" not in widget.render().plain

        # 4. Verify Dimension Recomputation (Satisfies Sanity Check)
        widget.show_offset = True
        widget.show_ascii = True
        widget.bytes_per_line = 8
        
        # Recompute width before checking height
        new_width = widget.get_content_width(Size(80, 24), Size(80, 24))
        new_height = widget.get_content_height(Size(80, 24), Size(80, 24), new_width)
        
        # 20 bytes / 8 per line = 3 lines
        assert new_height == 3
        assert "00000008  " in widget.render().plain
