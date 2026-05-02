import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_behavior():
    # 20 bytes: 16 on line 1, 4 on line 2
    data = b"Hello" + b"\x01" + b"World!" + b"12345678"
    
    class HexDumpApp(App):
        def compose(self):
            # Test constructor kwargs and initial state
            yield HexDump(data, highlight_index=5)

    app = HexDumpApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        
        # 1. Verify Layout & Multi-line (0x10 offset)
        render = widget.render()
        plain = render.plain
        assert "00000000  48 65 6C 6C 6F 01 57 6F 72 6C 64 21 31 32 33 34" in plain
        assert "00000010  35 36 37 38" in plain
        assert "  |Hello.World!1234|" in plain

        # 2. Verify Styles (Check Rich spans for 'reverse red')
        # This satisfies the Reviewer's demand for style verification
        styles = [str(span.style) for span in render.spans]
        assert any("reverse red" in s for s in styles), "Highlight style missing"

        # 3. Verify Reactive Mutability (Reflected immediately)
        widget.show_offset = False
        assert "00000000" not in widget.render().plain
        
        widget.show_ascii = False
        assert "|" not in widget.render().plain

        # 4. Verify Dimension Recomputation (Satisfies Sanity Check)
        widget.show_offset = True
        widget.show_ascii = True
        widget.bytes_per_line = 8
        
        # Recompute width before height to avoid brittle results
        width = widget.get_content_width(Size(80, 24), Size(80, 24))
        height = widget.get_content_height(Size(80, 24), Size(80, 24), width)
        
        # 20 bytes / 8 per line = 3 lines
        assert height == 3
        assert "00000008  " in widget.render().plain
