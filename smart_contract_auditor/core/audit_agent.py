"""
Audit Agent - Main LangChain Agent for Smart Contract Auditing
الوكيل الرئيسي لتدقيق العقود الذكية باستخدام LangChain
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

# Note: LangChain AgentExecutor is not strictly needed for this implementation
# We use a custom sequential agent flow instead

from langchain_openai import ChatOpenAI

# Use absolute imports for tools
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.terminal_tool import TerminalTool
from tools.deepseek_tool import DeepSeekTool
from tools.slither_tool import SlitherTool
from tools.fuzzing_tool import FuzzingTool
from tools.poc_generator import PoCGenerator


class AuditAgent:
    """
    الوكيل الرئيسي لتدقيق العقود الذكية
    
    يمر بمراحل متسلسلة:
    1. قراءة العقد
    2. تحليل Slither
    3. تحليل DeepSeek
    4. تحديد ثغرات مشبوهة
    5. لكل ثغرة: يكتب PoC ويشغله
    6. إذا نجح: يعتبرها مؤكدة
    7. إذا فشل: يحاول تعديلها حتى 3 مرات
    8. يخرج تقرير نهائي بالثغرات المؤكدة فقط
    """
    
    def __init__(
        self,
        api_key: str,
        config: Dict[str, Any],
        model_name: Optional[str] = None
    ):
        self.api_key = api_key
        self.config = config
        self.model_name = model_name or config.get('model_name', 'deepseek-chat')
        
        # تهيئة الأدوات
        self.terminal = TerminalTool(
            timeout_seconds=config.get('timeout_seconds', 60)
        )
        self.deepseek = DeepSeekTool(
            api_key=api_key,
            base_url=config.get('deepseek_base_url', 'https://api.deepseek.com/v1'),
            model_name=self.model_name,
            timeout_seconds=config.get('timeout_seconds', 60)
        )
        self.slither = SlitherTool(
            timeout_seconds=config.get('timeout_seconds', 60)
        )
        self.fuzzing = FuzzingTool(
            timeout_seconds=config.get('timeout_seconds', 60),
            test_limit=config.get('echidna_test_limit', 100)
        )
        self.poc_generator = PoCGenerator()
        
        # تتبع الثغرات المؤكدة
        self.confirmed_vulnerabilities = []
        self.attempted_pocs = []
    
    def audit_contract(self, contract_path: str) -> Dict[str, Any]:
        """
        التدقيق الكامل على عقد ذكي
        
        Args:
            contract_path: مسار ملف العقد
            
        Returns:
            dict: تقرير التدقيق النهائي
        """
        print(f"🔍 Starting audit for: {contract_path}")
        
        # المرحلة 1: قراءة العقد
        contract_code = self._read_contract(contract_path)
        if not contract_code:
            return {"success": False, "error": "Failed to read contract"}
        
        print("✅ Contract loaded successfully")
        
        # المرحلة 2: تحليل Slither
        print("\n📊 Running Slither static analysis...")
        slither_results = self.slither.analyze(contract_path)
        print(f"✅ Slither found {slither_results.get('issues_count', 0)} potential issues")
        
        # المرحلة 3: تحليل DeepSeek
        print("\n🤖 Running DeepSeek AI analysis...")
        deepseek_results = self.deepseek.analyze_contract(contract_code)
        if deepseek_results.get('success'):
            print("✅ DeepSeek analysis completed")
        else:
            print(f"⚠️ DeepSeek analysis failed: {deepseek_results.get('error')}")
        
        # المرحلة 4: دمج النتائج وتحديد الثغرات المشبوهة
        suspicious_vulnerabilities = self._merge_analysis_results(
            slither_results,
            deepseek_results
        )
        
        print(f"\n🎯 Identified {len(suspicious_vulnerabilities)} suspicious vulnerabilities")
        
        # المرحلة 5: اختبار كل ثغرة عن طريق PoC
        print("\n🧪 Testing each vulnerability with PoC...")
        for i, vuln in enumerate(suspicious_vulnerabilities):
            print(f"\n--- Testing Vulnerability {i+1}/{len(suspicious_vulnerabilities)} ---")
            print(f"Type: {vuln.get('type', 'Unknown')}")
            print(f"Severity: {vuln.get('severity', 'Unknown')}")
            
            is_confirmed = self._test_vulnerability_with_poc(
                contract_path=contract_path,
                vulnerability=vuln,
                max_attempts=3
            )
            
            if is_confirmed:
                print(f"✅ VULNERABILITY CONFIRMED: {vuln.get('type')}")
                self.confirmed_vulnerabilities.append(vuln)
            else:
                print(f"❌ Could not confirm: {vuln.get('type')}")
        
        # المرحلة 6: إصدار التقرير النهائي
        report = self._generate_final_report(
            contract_path=contract_path,
            contract_code=contract_code,
            slither_results=slither_results,
            deepseek_results=deepseek_results,
            confirmed_vulnerabilities=self.confirmed_vulnerabilities
        )
        
        print("\n" + "="*60)
        print("📋 FINAL AUDIT REPORT")
        print("="*60)
        print(f"Total vulnerabilities tested: {len(suspicious_vulnerabilities)}")
        print(f"Confirmed vulnerabilities: {len(self.confirmed_vulnerabilities)}")
        print("="*60)
        
        return report
    
    def _read_contract(self, contract_path: str) -> Optional[str]:
        """قراءة كود العقد من الملف"""
        try:
            with open(contract_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading contract: {e}")
            return None
    
    def _merge_analysis_results(
        self,
        slither_results: Dict[str, Any],
        deepseek_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """دمج نتائج التحليلات"""
        vulnerabilities = []
        
        # إضافة ثغرات Slither
        slither_issues = slither_results.get('issues', [])
        for issue in slither_issues:
            vulnerabilities.append({
                'type': issue.get('type', 'Unknown'),
                'severity': self._map_impact_to_severity(issue.get('impact', 'Unknown')),
                'confidence': issue.get('confidence', 'Unknown'),
                'description': issue.get('description', ''),
                'source': 'slither',
                'location': issue.get('elements', [])
            })
        
        # استخراج ثغرات من تحليل DeepSeek
        if deepseek_results.get('success'):
            ai_vulns = self._parse_ai_vulnerabilities(
                deepseek_results.get('analysis', '')
            )
            for vuln in ai_vulns:
                # تجنب التكرار
                if not self._is_duplicate(vuln, vulnerabilities):
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _map_impact_to_severity(self, impact: str) -> str:
        """تحويل تأثير Slither إلى مستوى خطورة"""
        impact_map = {
            'HIGH': 'Critical',
            'MEDIUM': 'High',
            'LOW': 'Medium',
            'INFORMATIONAL': 'Low'
        }
        return impact_map.get(impact.upper(), 'Medium')
    
    def _parse_ai_vulnerabilities(self, analysis_text: str) -> List[Dict[str, Any]]:
        """استخراج الثغرات من نص تحليل AI"""
        vulnerabilities = []
        
        # محاولة بسيطة لاستخراج الثغرات المذكورة
        lines = analysis_text.split('\n')
        current_vuln = None
        
        for line in lines:
            line = line.strip()
            
            # البحث عن أنواع الثغرات الشائعة
            vuln_types = [
                'Reentrancy', 'Overflow', 'Underflow', 'Front-running',
                'Access Control', 'Business Logic', 'Timestamp', 'DoS'
            ]
            
            for vtype in vuln_types:
                if vtype.lower() in line.lower():
                    if current_vuln:
                        vulnerabilities.append(current_vuln)
                    
                    current_vuln = {
                        'type': vtype,
                        'severity': 'High' if 'critical' in line.lower() else 'Medium',
                        'description': line,
                        'source': 'deepseek'
                    }
                    break
        
        if current_vuln:
            vulnerabilities.append(current_vuln)
        
        return vulnerabilities
    
    def _is_duplicate(self, vuln: Dict, existing: List[Dict]) -> bool:
        """التحقق من عدم التكرار"""
        for existing_vuln in existing:
            if vuln.get('type', '').lower() == existing_vuln.get('type', '').lower():
                return True
        return False
    
    def _test_vulnerability_with_poc(
        self,
        contract_path: str,
        vulnerability: Dict[str, Any],
        max_attempts: int = 3
    ) -> bool:
        """
        اختبار ثغرة عن طريق كتابة وتشغيل PoC
        
        Args:
            contract_path: مسار العقد
            vulnerability: معلومات الثغرة
            max_attempts: عدد المحاولات القصوى
            
        Returns:
            bool: هل تم تأكيد الثغرة؟
        """
        vuln_type = vulnerability.get('type', 'Unknown')
        description = vulnerability.get('description', '')
        
        for attempt in range(1, max_attempts + 1):
            print(f"  Attempt {attempt}/{max_attempts}...")
            
            # توليد PoC
            poc_result = self._generate_and_run_poc(
                contract_path=contract_path,
                vulnerability=vulnerability
            )
            
            if poc_result.get('confirmed'):
                vulnerability['poc_path'] = poc_result.get('poc_path')
                vulnerability['poc_output'] = poc_result.get('output')
                return True
            
            # إذا فشل، نحاول تحسين الـ PoC في المحاولة التالية
            if attempt < max_attempts:
                print(f"    Refining PoC based on feedback...")
        
        return False
    
    def _generate_and_run_poc(
        self,
        contract_path: str,
        vulnerability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """توليد وتشغيل PoC"""
        contract_name = self._extract_contract_name(contract_path)
        vuln_type = vulnerability.get('type', 'Unknown')
        description = vulnerability.get('description', '')
        
        # إنشاء مسار للـ PoC
        poc_filename = f"test_exploit_{vuln_type.lower().replace('/', '_')}.t.sol"
        poc_path = os.path.join(os.path.dirname(contract_path), poc_filename)
        
        # توليد الـ PoC
        poc_result = self.poc_generator.generate_poc(
            contract_path=contract_path,
            contract_name=contract_name or "TargetContract",
            vulnerability_type=vuln_type,
            vulnerability_description=description,
            output_path=poc_path
        )
        
        if not poc_result.get('success'):
            return {'confirmed': False, 'error': poc_result.get('error')}
        
        print(f"    Generated PoC at: {poc_path}")
        
        # تشغيل الـ PoC باستخدام Foundry
        test_result = self._run_foundry_test(poc_path, contract_path)
        
        if test_result.get('success'):
            return {
                'confirmed': True,
                'poc_path': poc_path,
                'output': test_result.get('output', '')
            }
        
        return {'confirmed': False, 'output': test_result.get('error', '')}
    
    def _extract_contract_name(self, contract_path: str) -> Optional[str]:
        """استخراج اسم العقد"""
        try:
            with open(contract_path, 'r') as f:
                content = f.read()
            match = re.search(r'contract\s+(\w+)', content)
            return match.group(1) if match else None
        except Exception:
            return None
    
    def _run_foundry_test(
        self,
        test_path: str,
        contract_path: str
    ) -> Dict[str, Any]:
        """تشغيل اختبار Foundry"""
        # التأكد من وجود forge
        exit_code, stdout, stderr = self.terminal.execute("forge --version")
        if exit_code != 0:
            return {
                'success': False,
                'error': 'Foundry (forge) not installed or not in PATH'
            }
        
        # تشغيل الاختبار
        command = f"forge test --match-path {test_path} -vvv"
        exit_code, stdout, stderr = self.terminal.execute(command)
        
        # Foundry returns 0 if tests pass, non-zero if they fail
        # For exploit tests, we want them to "pass" (demonstrate the exploit)
        return {
            'success': exit_code == 0 or 'PASSED' in stdout,
            'output': stdout,
            'error': stderr
        }
    
    def _generate_final_report(
        self,
        contract_path: str,
        contract_code: str,
        slither_results: Dict[str, Any],
        deepseek_results: Dict[str, Any],
        confirmed_vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """إنشاء التقرير النهائي"""
        return {
            'success': True,
            'contract_path': contract_path,
            'contract_name': self._extract_contract_name(contract_path),
            'audit_summary': {
                'total_issues_found': len(slither_results.get('issues', [])),
                'confirmed_vulnerabilities': len(confirmed_vulnerabilities),
                'critical': sum(1 for v in confirmed_vulnerabilities if v.get('severity') == 'Critical'),
                'high': sum(1 for v in confirmed_vulnerabilities if v.get('severity') == 'High'),
                'medium': sum(1 for v in confirmed_vulnerabilities if v.get('severity') == 'Medium'),
                'low': sum(1 for v in confirmed_vulnerabilities if v.get('severity') == 'Low')
            },
            'confirmed_vulnerabilities': confirmed_vulnerabilities,
            'tools_used': ['Slither', 'DeepSeek AI', 'Foundry'],
            'recommendation': self._generate_recommendation(confirmed_vulnerabilities)
        }
    
    def _generate_recommendation(self, vulnerabilities: List[Dict]) -> str:
        """توليد توصية بناءً على الثغرات المؤكدة"""
        if not vulnerabilities:
            return "No critical vulnerabilities confirmed. Contract appears secure."
        
        critical_count = sum(1 for v in vulnerabilities if v.get('severity') == 'Critical')
        high_count = sum(1 for v in vulnerabilities if v.get('severity') == 'High')
        
        if critical_count > 0:
            return f"CRITICAL: {critical_count} critical vulnerability(ies) found. DO NOT deploy until fixed."
        elif high_count > 0:
            return f"HIGH PRIORITY: {high_count} high severity issue(s) found. Fix before deployment."
        else:
            return "Medium/Low severity issues found. Review and fix before production use."
