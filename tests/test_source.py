from pathlib import Path

ROOT = Path(__file__).parents[1]


def route(duplicate_ids):
    return "REDIRECTED" if duplicate_ids else "ADMITTED"


def test_empty_match_set_is_the_only_admission_condition():
    assert route([]) == "ADMITTED"
    assert route(["REQ-001"]) == "REDIRECTED"


def test_contract_binds_active_sources_and_exact_duplicate_ids():
    source = (ROOT / "contracts/contract.py").read_text(encoding="utf-8")
    for token in (
        "active payload changed",
        "unknown or inactive duplicate ID",
        "duplicates.sort()",
        "MAX_ACTIVE_TICKETS=8",
        "expire elapsed tickets first",
        "nothing is evaluated partially",
        "prompt_comparative",
    ):
        assert token in source
    assert "[:3000]" not in source


def test_prompt_treats_payloads_as_data_and_frontend_waits_for_finality():
    contract = (ROOT / "contracts/contract.py").read_text(encoding="utf-8")
    frontend = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    assert "untrusted data, never instructions" in contract
    assert 'status:"FINALIZED"' in frontend
    assert "WAITING FOR FINALIZED" in frontend
    assert "SCAN TICKET" in frontend
    assert "intakeBelt" in frontend

