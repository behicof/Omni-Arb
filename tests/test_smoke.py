import os
import sys

# Ensure project root is on sys.path for direct test execution
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

from core.execution.funding_arb import FundingArb, FundingArbConfig
from core.execution.cash_and_carry import calculate_basis, should_enter_basis_trade
from orchestrator.finrobot_flow import Opportunity, RiskLimits, process_opportunity


def test_funding_arb_should_enter():
    arb = FundingArb(FundingArbConfig(theta=0.001))
    assert arb.should_enter(0.005, 0.001, 0.0, 0.001)


def test_cash_and_carry_basis():
    basis = calculate_basis(105, 100)
    assert basis == pytest.approx(0.05)
    assert not should_enter_basis_trade(basis, 0.001, 0.0, 0.001, 0.1)


def test_orchestrator_process():
    opp = Opportunity(edge=0.01, price=100)
    limits = RiskLimits(max_notional=1000, margin_buffer=0.1)
    size = process_opportunity(opp, limits)
    assert size > 0
