"""
Unit tests for the deterministic financial engine. These do not require a
database connection - compute_emi and build_repayment_schedule are pure
functions.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.financial.engine import (
    FinancialValidationError,
    build_repayment_schedule,
    compute_emi,
)


def test_emi_basic():
    emi = compute_emi(900000, 8.5, 7)
    assert emi > 0
    # sanity: total repayment should exceed principal
    assert emi * 7 * 12 > 900000


def test_emi_zero_principal():
    assert compute_emi(0, 8.5, 7) == 0.0


def test_emi_zero_interest():
    emi = compute_emi(120000, 0, 10)
    assert emi == round(120000 / 120, 2)


def test_emi_invalid_tenure():
    with pytest.raises(FinancialValidationError):
        compute_emi(100000, 8.5, 0)


def test_repayment_schedule_length_matches_tenure():
    result = build_repayment_schedule(900000, 8.5, 7, moratorium_months=6)
    # tenure_years*12 repayment installments + moratorium_months
    assert len(result["schedule"]) <= (7 * 12) + 6
    assert result["schedule"][-1]["remaining_balance"] == 0.0


def test_repayment_schedule_moratorium_defers_principal():
    result = build_repayment_schedule(500000, 9.0, 5, moratorium_months=3)
    moratorium_entries = [e for e in result["schedule"] if e["phase"] == "MORATORIUM"]
    assert len(moratorium_entries) == 3
    for e in moratorium_entries:
        assert e["principal_component"] == 0.0


def test_worked_example_from_spec():
    """Spec section 27 worked example:
    Available Margin = 1,00,000 -> Project Cost = 10,00,000, Loan = 9,00,000
    at 10% beneficiary contribution."""
    from app.financial.engine import compute_project_cost_and_loan

    result = compute_project_cost_and_loan(available_margin=100000, beneficiary_contribution_pct=0.10)
    assert result["project_cost"] == 1000000.0
    assert result["loan_amount"] == 900000.0
