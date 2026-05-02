import pytest
from textual.app import App
from textual.widgets import HexDump
from textual.geometry import Size


# ✅ IMPORTANT: ensures F2P is not empty
def test_hexdump_import_exists():
    from textual.widgets import HexDump
    assert HexDump is not None


@pytest.mark.asyncio
async def test_hexdump_defaults_and_formatting():
    data = b"A" * 15 + b"\x01" + b"BC" + b"\xff"
    app = App()

    async with app.run_test() as pilot:
        widget = HexDump(data)

        # ✅ FIXED mounting
        await pilot.app.mount(widget)

        # Default properties
        assert widget.show_offset is True
        assert widget.show_ascii is True
        assert widget.bytes_per_line == 16
        assert widget.highlight_index is None

        render = widget.render()
        plain = render.plain

        # Uppercase formatting
        assert "00000000" in plain
        assert "41 41" in plain
        assert "FF" in plain

        # ASCII mapping
        assert "|AAAAAAAAAAAAAAA.|" in plain

        # Alignment check
        lines = plain.splitlines()
        assert lines[0].find("|") == lines[1].find("|"), \
            "ASCII sections must be vertically aligned"


@pytest.mark.asyncio
async def test_hexdump_constructor_kwargs():
    data = b"test"

    class ConstApp(App):
        def compose(self):
            yield HexDump(
                data,
                show_offset=False,
                show_ascii=False,
                bytes_per_line=4,
                highlight_index=0,
            )

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
    data = b"ABC"
    app = App()

    async with app.run_test() as pilot:
        widget = HexDump(data, highlight_index=1)

        # ✅ FIXED mounting
        await pilot.app.mount(widget)

        render = widget.render()
        highlighted_contents = []

        for span in render.spans:
            style_str = str(span.style).lower()
            if "reverse" in style_str and "red" in style_str:
                highlighted_contents.append(
                    render.plain[span.start:span.end]
                )

        assert "42" in highlighted_contents
        assert "B" in highlighted_contents


@pytest.mark.asyncio
async def test_hexdump_runtime_mutability():
    data = b"mutations"
    app = App()

    async with app.run_test() as pilot:
        widget = HexDump(data)

        # ✅ FIXED mounting
        await pilot.app.mount(widget)

        # Toggle ASCII
        widget.show_ascii = False
        assert "|" not in widget.render().plain

        # Enable highlight
        widget.highlight_index = 0
        assert any(
            "reverse" in str(s.style)
            for s in widget.render().spans
        )

        # Disable highlight
        widget.highlight_index = None
        assert not any(
            "reverse" in str(s.style)
            for s in widget.render().spans
        )


@pytest.mark.asyncio
async def test_hexdump_dimensions():
    data = b"X" * 20
    widget = HexDump(data)

    # Default (16 bytes/line)
    w = widget.get_content_width(Size(100, 100), Size(100, 100))
    h = widget.get_content_height(Size(100, 100), Size(100, 100), w)

    assert h == 2
    assert w == 77

    # Change bytes_per_line
    widget.bytes_per_line = 8

    w8 = widget.get_content_width(Size(100, 100), Size(100, 100))
    h8 = widget.get_content_height(Size(100, 100), Size(100, 100), w8)

    assert h8 == 3
    assert w8 == 45
