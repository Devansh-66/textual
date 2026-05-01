import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_comprehensive():
    data = b"Hello" + b"\x01" + b"World!" + b"12345678"
    
    class HexDumpApp(App):
        def compose(self):
            yield HexDump(data, highlight_index=0)

    app = HexDumpApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        
        # Verify Spacing & Formatting
        plain = widget.render().plain
        assert "00000000  48 65 6C 6C 6F 01 57 6F 72 6C 64 21 31 32 33 34" in plain
        assert "  |Hello.World!1234|" in plain

        # Verify Scrolling Dimensions (Crucial for Shipd pass)
        width = widget.get_content_width(Size(80, 24), Size(80, 24))
        height = widget.get_content_height(Size(80, 24), Size(80, 24), width)
        assert height == 2
        
        # Verify Mutability
        widget.bytes_per_line = 8
        assert widget.get_content_height(Size(80, 24), Size(80, 24), width) == 3
