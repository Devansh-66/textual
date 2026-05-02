import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_constructor_and_dimensions():
    data = b"Hello World"
    class ConstApp(App):
        def compose(self):
            yield HexDump(
                data, 
                show_offset=False, 
                show_ascii=False, 
                bytes_per_line=8,
                highlight_index=0
            )
    app = ConstApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        assert widget.show_offset is False
        assert widget.show_ascii is False
        assert widget.bytes_per_line == 8
        # width = 0 + (8 * 3) - 1 = 23
        assert widget.get_content_width(Size(80, 24), Size(80, 24)) == 23

@pytest.mark.asyncio
async def test_hexdump_highlighting_and_layout():
    data = b"ABC" # 41 42 43
    class HighlightingApp(App):
        def compose(self):
            yield HexDump(data, highlight_index=1)
    app = HighlightingApp()
    async with app.run_test() as pilot:
        # FIXED: app is the app, so we query HexDump directly
        widget = app.query_one(HexDump)
        render = widget.render()
        
        hex_span_found = False
        ascii_span_found = False
        for span in render.spans:
            if str(span.style) == "reverse red":
                if span.start == 13 and span.end == 15: # Hex section
                    hex_span_found = True
                if span.start == 61 and span.end == 62: # ASCII section
                    ascii_span_found = True
        
        assert hex_span_found, "Highlight index 1 missing from Hex section"
        assert ascii_span_found, "Highlight index 1 missing from ASCII section"

@pytest.mark.asyncio
async def test_hexdump_mutability_toggling():
    data = b"X" * 20
    app = App()
    async with app.run_test() as pilot:
        widget = HexDump(data)
        await app.mount(widget)
        assert widget.get_content_height(Size(80, 24), Size(80, 24), 77) == 2
        widget.bytes_per_line = 5
        assert widget.get_content_height(Size(80, 24), Size(80, 24), 77) == 4
        widget.show_offset = False
        assert "00000000" not in widget.render().plain
