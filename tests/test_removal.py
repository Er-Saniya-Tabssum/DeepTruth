from PIL import Image

from backend.app.services.removal import make_text_mask


def test_text_mask_is_binary_and_scaled(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (100, 80), "white").save(source)
    regions = [{
        "region_id": "text-1",
        "polygon": [[10, 10], [40, 10], [40, 30], [10, 30]],
        "bbox": {"x": 10, "y": 10, "width": 30, "height": 20},
        "confidence": 0.99,
    }]
    mask = make_text_mask(str(source), regions, 1.0)
    assert mask.size == (100, 80)
    assert mask.getbbox() is not None
    assert mask.getpixel((20, 20)) == 255
    assert mask.getpixel((90, 70)) == 0
