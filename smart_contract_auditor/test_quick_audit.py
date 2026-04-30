#!/usr/bin/env python3
"""
Quick Audit Test - اختبار سريع للنظام
"""

import sys
import os
import json
from pathlib import Path

# إضافة المسار الرئيسي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.audit_agent import AuditAgent
import yaml

def quick_audit(contract_path: str, api_key: str):
    """إجراء تدقيق سريع لعقد واحد"""
    
    # تحميل الإعدادات
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print("="*60)
    print("🔍 SMART CONTRACT QUICK AUDIT")
    print("="*60)
    print(f"📄 Contract: {contract_path}")
    print(f"🤖 Model: {config.get('model_name', 'deepseek-chat')}")
    print(f"⏱️  Timeout: {config.get('timeout_seconds', 300)}s")
    print("="*60)
    
    # إنشاء الوكيل
    agent = AuditAgent(
        api_key=api_key,
        config=config
    )
    
    # إجراء التدقيق
    try:
        result = agent.audit_contract(contract_path)
        
        print("\n" + "="*60)
        print("📊 AUDIT RESULTS")
        print("="*60)
        
        if result.get('success'):
            print(f"✅ Audit completed successfully")
            print(f"📋 Contracts audited: {result.get('total_contracts', 1)}")
            
            summary = result.get('audit_summary', {})
            print(f"🔴 Critical: {summary.get('critical', 0)}")
            print(f"🟠 High: {summary.get('high', 0)}")
            print(f"🟡 Medium: {summary.get('medium', 0)}")
            print(f"🟢 Low: {summary.get('low', 0)}")
            
            confirmed = result.get('confirmed_vulnerabilities', [])
            if confirmed:
                print(f"\n⚠️  CONFIRMED VULNERABILITIES: {len(confirmed)}")
                for i, vuln in enumerate(confirmed, 1):
                    print(f"\n{i}. {vuln.get('type', 'Unknown')}")
                    print(f"   Severity: {vuln.get('severity', 'Unknown')}")
                    print(f"   Description: {vuln.get('description', 'N/A')[:200]}...")
            else:
                print(f"\n✅ No confirmed vulnerabilities found")
            
            print(f"\n💡 Recommendation: {result.get('recommendation', 'N/A')}")
            
            # حفظ التقرير
            report_path = Path(__file__).parent / "audit_report.json"
            with open(report_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n💾 Report saved to: {report_path}")
            
        else:
            print(f"❌ Audit failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error during audit: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick Smart Contract Audit")
    parser.add_argument("--contract", required=True, help="Path to contract file")
    parser.add_argument("--api-key", required=True, help="DeepSeek API Key")
    
    args = parser.parse_args()
    
    success = quick_audit(args.contract, args.api_key)
    sys.exit(0 if success else 1)
