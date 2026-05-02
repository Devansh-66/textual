import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_constructor_and_dimensions():
    data = b"Hello World"
    # Test constructor with non-default optional kwargs
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
        
        # Verify constructor values were respected
        assert widget.show_offset is False
        assert widget.show_ascii is False
        assert widget.bytes_per_line == 8
        
        # Validate Width computation (show_offset=F, show_ascii=F, bpl=8)
        # width = 0 + (8 * 3) - 1 = 23
        expected_width = (8 * 3) - 1
        assert widget.get_content_width(Size(80, 24), Size(80, 24)) == expected_width

@pytest.mark.asyncio
async def test_hexdump_highlighting_and_layout():
    data = b"ABC" # 41 42 43
    
    class HighlightingApp(App):
        def compose(self):
            # Default: show_offset=T, show_ascii=T, bpl=16
            yield HexDump(data, highlight_index=1) # Highlight 'B' (index 1)

    app = HighlightingApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HighlightingApp).query_one(HexDump)
        render = widget.render()
        plain = render.plain
        
        # Verify Layout/Formatting
        # 00000000  41 42 43 ... |ABC|
        assert plain.startswith("00000000  41 42 43")
        assert "|ABC|" in plain

        # Verify Highlighting in BOTH sections
        # Hex '42' for index 1: 
        # Offset(10) + Byte0(2) + Space(1) = start at index 13
        # ASCII 'B' for index 1:
        # Offset(10) + HexPart(16*3-1=47) + Spaces(2) + Pipe(1) + Char0(1) = index 61
        
        hex_span_found = False
        ascii_span_found = False
        
        for span in render.spans:
            if str(span.style) == "reverse red":
                # Check if this span covers the Hex section (index 13-15)
                if span.start == 13 and span.end == 15:
                    hex_span_found = True
                # Check if this span covers the ASCII section (index 61-62)
                if span.start == 61 and span.end == 62:
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
        
        # Default height for 20 bytes (bpl=16) is 2 lines
        assert widget.get_content_height(Size(80, 24), Size(80, 24), 77) == 2
        
        # Toggle reactive properties
        widget.bytes_per_line = 5
        # 20 bytes / 5 bpl = 4 lines
        assert widget.get_content_height(Size(80, 24), Size(80, 24), 77) == 4
        
        widget.show_offset = False
        assert "00000000" not in widget.render().plain
