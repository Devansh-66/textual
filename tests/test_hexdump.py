import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_comprehensive_behavior():
    data = b"Hello" + b"\x01" + b"World!"
    
    class HexDumpApp(App):
        def compose(self):
            yield HexDump(data, show_offset=True, show_ascii=True, highlight_index=0)

    app = HexDumpApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        
        width = widget.get_content_width(Size(80, 24), Size(80, 24))
        height = widget.get_content_height(Size(80, 24), Size(80, 24), width)
        assert width > 0
        assert height >= 1
        
        text_result = widget.render()
        plain_text = text_result.plain
        
        assert "00000000  " in plain_text
        assert "|Hello.World!|" in plain_text

        styles = [str(span.style) for span in text_result.spans]
        assert "cyan" in styles
        assert "green" in styles
        assert "yellow" in styles
        
        highlight_count = sum(1 for style in styles if "reverse red" in style)
        assert highlight_count == 2

        widget.highlight_index = None
        none_result = widget.render()
        none_styles = [str(span.style) for span in none_result.spans]
        assert "reverse red" not in none_styles
