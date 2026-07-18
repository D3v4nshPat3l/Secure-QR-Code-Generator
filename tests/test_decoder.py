from secure_qr.decoder import analyze_payload


def test_payment_report_highlights_recipient() -> None:
    report = analyze_payload("upi://pay?pa=person%40bank&am=100")
    assert report.kind == "payment"
    assert report.risk == "high"
    assert any("person@bank" in item for item in report.findings)


def test_dangerous_scheme_is_critical() -> None:
    report = analyze_payload("javascript:alert(1)")
    assert report.risk == "critical"
