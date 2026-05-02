import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size

@pytest.mark.asyncio
async def test_hexdump_defaults_and_formatting():
    # Data includes printable 'A', non-printable '\x01', and high-bit '\xff'
    data = b"A" * 15 + b"\x01" + b"BC" + b"\xff"
    app = App()
    async with app.run_test() as pilot:
        widget = HexDump(data)
        await app.mount(widget)
        
        # 1. Verify Default property values
        assert widget.show_offset is True
        assert widget.show_ascii is True
        assert widget.bytes_per_line == 16
        assert widget.highlight_index is None

        render = widget.render()
        plain = render.plain
        
        # 2. Verify Uppercase formatting of offset (8 digits) and hex (2 digits)
        assert "00000000" in plain
        assert "41 41" in plain  # Uppercase hex for 'A'
        assert "FF" in plain     # Uppercase hex for '\xff'

        # 3. Verify ASCII mapping (non-printables to '.')
        assert "|AAAAAAAAAAAAAAA.|" in plain

        # 4. Verify vertical alignment (Padding)
        lines = plain.splitlines()
        # The pipes on line 1 and line 2 should be at the same character column
        assert lines[0].find("|") == lines[1].find("|"), "ASCII sections must be vertically aligned"

@pytest.mark.asyncio
async def test_hexdump_constructor_kwargs():
    data = b"test"
    class ConstApp(App):
        def compose(self):
            yield HexDump(data, show_offset=False, show_ascii=False, bytes_per_line=4, highlight_index=0)
    
    app = ConstApp()
    async with app.run_test() as pilot:
        widget = app.query_one(HexDump)
        assert widget.show_offset is False
        assert widget.show_ascii is False
        assert widget.bytes_per_line == 4
        assert widget.highlight_index == 0
        
        plain = widget.render().plain
        assert "00000000" not in plain
        assert "|" not in plain

@pytest.mark.asyncio
async def test_hexdump_highlighting_behavior():
    # Verify highlight index 1 ('B') appears in both hex and ascii sections
    # Uses behavioral content matching instead of implementation-specific indices
    data = b"ABC"
    app = App()
    async with app.run_test() as pilot:
        widget = HexDump(data, highlight_index=1)
        await app.mount(widget)
        
        render = widget.render()
        highlighted_contents = []
        for span in render.spans:
            # Spec requires 'reverse red'
            style_str = str(span.style).lower()
            if "reverse" in style_str and "red" in style_str:
                highlighted_contents.append(render.plain[span.start:span.end])
        
        assert "42" in highlighted_contents, "Hex representation of index 1 (42) should be highlighted"
        assert "B" in highlighted_contents, "ASCII representation of index 1 (B) should be highlighted"

@pytest.mark.asyncio
async def test_hexdump_runtime_mutability():
    data = b"mutations"
    app = App()
    async with app.run_test() as pilot:
        widget = HexDump(data)
        await app.mount(widget)
        
        # Test visual update for show_ascii
        widget.show_ascii = False
        assert "|" not in widget.render().plain
        
        # Test visual update for highlight_index
        widget.highlight_index = 0
        assert any("reverse" in str(s.style) for s in widget.render().spans)
        
        widget.highlight_index = None
        assert not any("reverse" in str(s.style) for s in widget.render().spans)

@pytest.mark.asyncio
async def test_hexdump_dimensions():
    data = b"X" * 20
    widget = HexDump(data)
    
    # 20 bytes @ 16 bpl = 2 lines. Width = 10(off) + 47(hex) + 20(ascii) = 77
    w = widget.get_content_width(Size(100, 100), Size(100, 100))
    h = widget.get_content_height(Size(100, 100), Size(100, 100), w)
    assert h == 2
    assert w == 77
    
    # Change bytes_per_line to 8
    widget.bytes_per_line = 8
    w8 = widget.get_content_width(Size(100, 100), Size(100, 100))
    h8 = widget.get_content_height(Size(100, 100), Size(100, 100), w8)
    # 20 / 8 = 3 lines. Width = 10(off) + 23(hex) + 12(ascii) = 45
    assert h8 == 3
    assert w8 == 45
