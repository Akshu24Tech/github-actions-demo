"""Tests for the ratio derivation engine and consensus/verify logic."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from financial_agent import do_derive, do_consensus, do_verify, _var

def _fact(metric, value, year='FY2024', conf=0.98):
    return {'metric': metric, 'value': value, 'year': year, 'confidence': conf, 'unit': 'INR crore'}

def test_total_liabilities_derived():
    facts = {
        'total_assets__FY2024': _fact('total_assets', 114950),
        'total_equity__FY2024': _fact('total_equity', 81176),
    }
    result = do_derive(facts)
    assert abs(result['total_liabilities__FY2024']['value'] - 33774) < 1

def test_net_profit_margin_derived():
    facts = {
        'profit_after_tax__FY2024': _fact('profit_after_tax', 27234),
        'revenue__FY2024': _fact('revenue', 128933),
    }
    result = do_derive(facts)
    assert abs(result['net_profit_margin__FY2024']['value'] - 21.12) < 0.1

def test_ebitda_derived():
    facts = {
        'profit_before_tax__FY2024': _fact('profit_before_tax', 30000),
        'finance_cost__FY2024': _fact('finance_cost', 5000),
        'depreciation__FY2024': _fact('depreciation', 8000),
    }
    result = do_derive(facts)
    assert result['ebitda__FY2024']['value'] == 43000

def test_consensus_agree():
    ra = {'extractions': [{'metric': 'total_assets', 'value': 114950, 'year': 'FY2024', 'unit': 'INR crore', 'page': 190, 'entity': 'standalone', 'confidence': 0.95}]}
    rb = {'extractions': [{'metric': 'total_assets', 'value': 114950, 'year': 'FY2024', 'unit': 'INR crore', 'page': 190, 'entity': 'standalone', 'confidence': 0.97}]}
    result = do_consensus(ra, rb)
    assert result['total_assets__FY2024']['flag'] == 'OK'
    assert result['total_assets__FY2024']['confidence'] == 0.98

def test_consensus_disagree():
    ra = {'extractions': [{'metric': 'total_assets', 'value': 114950, 'year': 'FY2024', 'unit': 'INR crore', 'page': 190, 'entity': 'standalone', 'confidence': 0.95}]}
    rb = {'extractions': [{'metric': 'total_assets', 'value': 99999,  'year': 'FY2024', 'unit': 'INR crore', 'page': 190, 'entity': 'standalone', 'confidence': 0.90}]}
    result = do_consensus(ra, rb)
    assert result['total_assets__FY2024']['flag'] == 'DISAGREE'
    assert result['total_assets__FY2024']['value'] is None

def test_verify_found():
    tc = {'190': 'Total assets 1,14,950 1,01,337'}
    f = do_verify({'metric': 'total_assets', 'value': 114950, 'page': 190, 'confidence': 0.98}, tc)
    assert f['confidence'] == 0.98

def test_verify_hallucination():
    tc = {'190': 'Total assets 1,14,950 1,01,337'}
    f = do_verify({'metric': 'total_assets', 'value': 999999, 'page': 190, 'confidence': 0.98}, tc)
    assert f['flag'] == 'UNVERIFIED'
    assert f['confidence'] == 0.45
    assert f['value'] == 999999  # value preserved, just flagged

def test_var_formats():
    variants = _var(114950)
    assert '1,14,950' in variants
    variants_neg = _var(-268)
    assert '(268)' in variants_neg
