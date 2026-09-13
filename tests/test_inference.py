from backend.app.inference import HuggingFaceImageDetector


def test_model_label_mapping_is_explicit():
    detector = HuggingFaceImageDetector()
    fake, real = detector._scores([
        {"label": "REAL", "score": 0.92},
        {"label": "FAKE", "score": 0.08},
    ])
    assert round(fake, 2) == 0.08
    assert round(real, 2) == 0.92


def test_verdict_thresholds():
    detector = HuggingFaceImageDetector()
    assert detector._verdict(0.90)[0] == "AI_GENERATED"
    assert detector._verdict(0.65)[0] == "POTENTIALLY_MANIPULATED"
    assert detector._verdict(0.20)[0] == "AUTHENTIC"
