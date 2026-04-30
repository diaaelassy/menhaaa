#!/usr/bin/env python3
"""
Smart Contract Auditor - Main CLI Interface
واجهة سطر الأوامر الرئيسية لنظام تدقيق العقود الذكية

Usage:
    python main.py --contract-path /path/to/contract.sol --api-key sk-xxxxx [--deepseek-model deepseek-chat]
"""

import argparse
import sys
import os
import yaml
from pathlib import Path

# إضافة المسار الحالي للـ Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.audit_agent import AuditAgent


def load_config(config_path: str) -> dict:
    """تحميل ملف الإعدادات"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}, using defaults")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing config file: {e}")
        return {}


def validate_contract_path(contract_path: str) -> bool:
    """التحقق من وجود ملف العقد"""
    if not os.path.exists(contract_path):
        print(f"Error: Contract file not found at {contract_path}")
        return False
    
    if not contract_path.endswith('.sol'):
        print("Warning: File does not have .sol extension")
    
    return True


def save_report(report: dict, output_path: str) -> bool:
    """حفظ التقرير في ملف"""
    try:
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False


def print_report_summary(report: dict):
    """طباعة ملخص التقرير"""
    print("\n" + "="*70)
    print("📊 SMART CONTRACT AUDIT REPORT".center(70))
    print("="*70)
    
    if not report.get('success'):
        print(f"❌ Audit failed: {report.get('error', 'Unknown error')}")
        return
    
    # معلومات العقد
    print(f"\n📄 Contract: {report.get('contract_name', 'Unknown')}")
    print(f"📁 Path: {report.get('contract_path', 'Unknown')}")
    
    # ملخص التدقيق
    summary = report.get('audit_summary', {})
    print("\n📈 AUDIT SUMMARY:")
    print("-"*70)
    print(f"  Total Issues Found:     {summary.get('total_issues_found', 0)}")
    print(f"  Confirmed Vulnerabilities: {summary.get('confirmed_vulnerabilities', 0)}")
    print()
    print(f"  🔴 Critical: {summary.get('critical', 0)}")
    print(f"  🟠 High:     {summary.get('high', 0)}")
    print(f"  🟡 Medium:   {summary.get('medium', 0)}")
    print(f"  🟢 Low:      {summary.get('low', 0)}")
    
    # الثغرات المؤكدة
    confirmed = report.get('confirmed_vulnerabilities', [])
    if confirmed:
        print("\n✅ CONFIRMED VULNERABILITIES:")
        print("-"*70)
        for i, vuln in enumerate(confirmed, 1):
            severity_icon = {
                'Critical': '🔴',
                'High': '🟠',
                'Medium': '🟡',
                'Low': '🟢'
            }.get(vuln.get('severity', 'Medium'), '⚪')
            
            print(f"\n  {i}. {severity_icon} {vuln.get('type', 'Unknown')}")
            print(f"     Severity: {vuln.get('severity', 'Unknown')}")
            print(f"     Source: {vuln.get('source', 'Unknown')}")
            if vuln.get('poc_path'):
                print(f"     PoC: {vuln.get('poc_path')}")
    
    # التوصية النهائية
    print("\n" + "-"*70)
    print(f"💡 RECOMMENDATION:")
    print(f"   {report.get('recommendation', 'No recommendation available')}")
    
    # الأدوات المستخدمة
    tools = report.get('tools_used', [])
    if tools:
        print(f"\n🛠️  Tools Used: {', '.join(tools)}")
    
    print("\n" + "="*70)
    print("⚠️  DISCLAIMER: This is an automated audit. Manual review recommended.")
    print("="*70 + "\n")


def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(
        description='Smart Contract Auditor - Automated Security Analysis for Multi-Contract Systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # تدقيق عقد واحد
  python main.py --contract-path ./MyContract.sol --api-key sk-xxxxx
  
  # تدقيق نظام متعدد العقود (Router + Proxy + Implementation)
  python main.py --contract-path ./Router.sol --additional-paths ./Proxy.sol ./Impl.sol --api-key sk-xxxxx
  
  # تدقيق مع حفظ التقرير
  python main.py --contract-path ./DeFi.sol --api-key sk-xxxxx --output report.json
  
  # تحديد موديل مختلف
  python main.py --contract-path ./Token.sol --api-key sk-xxxxx --model deepseek-coder
        """
    )
    
    parser.add_argument(
        '--contract-path',
        type=str,
        required=True,
        help='Path to the main Solidity smart contract file'
    )
    
    parser.add_argument(
        '--additional-paths',
        type=str,
        nargs='+',
        default=None,
        help='Paths to additional contract files (Router, Proxy, Libraries, etc.). Use space-separated paths or comma-separated.'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        required=True,
        help='DeepSeek API key for AI analysis'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--deepseek-model',
        type=str,
        default=None,
        help='DeepSeek model name (default: from config or deepseek-chat)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output path for the audit report (JSON format)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # معالجة المسارات الإضافية (دعم الفواصل والمسافات)
    additional_paths = None
    if args.additional_paths:
        additional_paths = []
        for path_item in args.additional_paths:
            # إذا كان يحتوي على فواصل، نقسمه
            if ',' in path_item:
                additional_paths.extend([p.strip() for p in path_item.split(',') if p.strip()])
            else:
                additional_paths.append(path_item.strip())
    
    # التحقق من ملف العقد
    if not validate_contract_path(args.contract_path):
        sys.exit(1)
    
    # تحميل الإعدادات
    config_path = args.config if os.path.isabs(args.config) else os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        args.config
    )
    config = load_config(config_path)
    
    # تحديث الإعدادات من argumentos
    if args.api_key:
        config['deepseek_api_key'] = args.api_key
    
    model_name = args.deepseek_model or config.get('model_name', 'deepseek-chat')
    
    # التحقق من وجود مفتاح API
    api_key = config.get('deepseek_api_key', '')
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("Error: DeepSeek API key is required")
        print("Provide it via --api-key or set it in config.yaml")
        sys.exit(1)
    
    print("="*70)
    print("🔍 SMART CONTRACT AUDITOR AGENT".center(70))
    print("="*70)
    print(f"\n📋 Configuration:")
    print(f"   Model: {model_name}")
    print(f"   Contract: {args.contract_path}")
    print(f"   Config: {config_path}")
    print()
    
    try:
        # إنشاء الوكيل
        agent = AuditAgent(
            api_key=api_key,
            config=config,
            model_name=model_name
        )
        
        # بدء التدقيق متعدد العقود
        report = agent.audit_contract(
            contract_path=args.contract_path,
            additional_paths=additional_paths
        )
        
        # طباعة التقرير
        print_report_summary(report)
        
        # حفظ التقرير إذا طُلب
        if args.output:
            if save_report(report, args.output):
                print(f"💾 Report saved to: {args.output}")
        
        # تحديد حالة الخروج بناءً على النتائج
        confirmed_count = len(report.get('confirmed_vulnerabilities', []))
        critical_count = sum(
            1 for v in report.get('confirmed_vulnerabilities', [])
            if v.get('severity') == 'Critical'
        )
        
        if critical_count > 0:
            print("\n🚨 CRITICAL VULNERABILITIES FOUND - DO NOT DEPLOY!")
            sys.exit(2)
        elif confirmed_count > 0:
            print("\n⚠️  VULNERABILITIES FOUND - REVIEW BEFORE DEPLOYMENT")
            sys.exit(1)
        else:
            print("\n✅ NO CRITICAL VULNERABILITIES CONFIRMED")
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Audit interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
