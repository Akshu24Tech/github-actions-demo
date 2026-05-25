"""Tests for the canonical map and normalize function."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from financial_agent import normalize, BASE_CANONICAL

def test_exact_synonyms():
    assert normalize('Total Assets') == 'total_assets'
    assert normalize('Net Revenue') == 'revenue'
    assert normalize('PAT') == 'profit_after_tax'

def test_fuzzy_match():
    assert normalize('Net Worth') == 'total_equity'
    assert normalize('D&A') == 'depreciation'
    assert normalize('Interest Expense') == 'finance_cost'

def test_base_canonical_completeness():
    required = ['revenue', 'profit_after_tax', 'total_assets', 'total_equity',
                'operating_cash_flow', 'capex', 'depreciation', 'finance_cost']
    for key in required:
        assert key in BASE_CANONICAL, f'{key} missing from BASE_CANONICAL'
