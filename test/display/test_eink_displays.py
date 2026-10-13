import pytest

def test_epd2in9_V3_waveshare_display_image():
    from components.display.epd2in9b_V3_image_factory import Epd2in9bV3ImageFactory

    factory = Epd2in9bV3ImageFactory()
    image = factory.create(
        epd_height=296,
        epd_width=128,
        title="Remmi Demmi",
        artist="Deichkind",
        album="Aufstand im Schlaraffenland",
        paused=True,
        repeat_info="repeat_one"
    )
    image.save("epd_waveshare_2in9_V3.bmp")
    assert image.size == (296, 128)

def test_epd2in9_V4_waveshare_display_image():
    from components.display.epd2in9b_V4_image_factory import Epd2in9bV4ImageFactory

    factory = Epd2in9bV4ImageFactory()
    image = factory.create(
        epd_height=296,
        epd_width=128,
        title="Remmi Demmi",
        artist="Deichkind",
        album="Aufstand im Schlaraffenland",
        paused=True,
        repeat_info="repeat_one"
    )
    image.save("epd_waveshare_2in9_V4.bmp")
    assert image.size == (296, 128)