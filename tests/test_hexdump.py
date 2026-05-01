import pytest
from textual.app import App
from textual.widgets import HexDump

async def test_hexdump_render():
    class HexDumpApp(App):
        def compose(self):
            # Highlight the 'W' in 'Hello World!'
            yield HexDump(b"Hello World!", show_offset=True, show_ascii=True, highlight_index=6)

    app = HexDumpApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        
        text_result = widget.render()
        plain_text = text_result.plain
        
        # Check that it renders the offset, hex, and ascii correctly
        assert "00000000" in plain_text
        assert "48 65 6C 6C 6F 20 57 6F 72 6C 64 21" in plain_text
        assert "Hello World!" in plain_text
