#!/usr/bin/env python3
"""اختبار سريع لعقد واحد"""
import sys
sys.path.insert(0, '.')
from core.audit_agent import AuditAgent

agent = AuditAgent(
    api_key="sk-test",
    config={'model_name': 'deepseek-chat'}
)

report = agent.audit_contract(
    contract_path="../ithaca-audit/ithaca-repo/contracts/access/AccessController.sol",
    additional_paths=None
)

print("\n" + "="*70)
print("REPORT SUMMARY")
print("="*70)
print(f"Success: {report.get('success')}")
print(f"Vulnerabilities Found: {len(report.get('confirmed_vulnerabilities', []))}")
if report.get('confirmed_vulnerabilities'):
    for v in report['confirmed_vulnerabilities']:
        print(f"  - {v.get('type')}: {v.get('severity')}")
