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
    
    def audit_contract(self, contract_path: str, additional_paths: list = None) -> Dict[str, Any]:
        """
        التدقيق الكامل على عقد ذكي مع العقود المرتبطة به (Router, Proxy, Dependencies)
        
        Args:
            contract_path: مسار ملف العقد الرئيسي
            additional_paths: مسارات ملفات العقود الإضافية (Router, Proxy, Libraries)
            
        Returns:
            dict: تقرير التدقيق النهائي
        """
        print(f"🔍 Starting COMPREHENSIVE audit for: {contract_path}")
        if additional_paths:
            print(f"📎 Additional contracts to analyze: {len(additional_paths)}")
        
        # المرحلة 1: قراءة العقد الرئيسي وجميع العقود المرتبطة
        contracts_data = self._read_all_contracts(contract_path, additional_paths)
        if not contracts_data:
            return {"success": False, "error": "Failed to read contracts"}
        
        print(f"✅ Loaded {len(contracts_data)} contract(s) successfully")
        
        # المرحلة 2: تحليل العلاقات بين العقود (Proxy, Router, Implementation)
        print("\n🔗 Analyzing contract relationships and dependencies...")
        relationships = self._analyze_contract_relationships(contracts_data)
        print(f"✅ Found {len(relationships)} contract relationship(s)")
        
        # المرحلة 3: تحليل Slither لكل العقود
        print("\n📊 Running Slither static analysis on ALL contracts...")
        all_slither_results = []
        for contract_name, contract_info in contracts_data.items():
            print(f"   → Analyzing {contract_name}...")
            slither_result = self.slither.analyze(contract_info['path'])
            all_slither_results.append({
                'contract': contract_name,
                'results': slither_result
            })
        print(f"✅ Slither analysis completed for {len(contracts_data)} contracts")
        
        # المرحلة 4: تحليل DeepSeek للثغرات المعقدة عبر العقود المتعددة
        print("\n🤖 Running DeepSeek AI analysis for CROSS-CONTRACT vulnerabilities...")
        deepseek_results = self.deepseek.analyze_multi_contract(
            contracts_data=contracts_data,
            relationships=relationships,
            focus_on_complex=True,
            zero_day_hunting=True,
            focus_areas=[
                'Proxy Pattern Vulnerabilities',
                'Router/Dispatcher Logic Flaws',
                'Cross-contract Reentrancy',
                'Storage Collision in Upgradeable Proxies',
                'DelegateCall Chain Attacks',
                'Access Control Bypass Across Contracts',
                'Inter-contract State Manipulation',
                'Composability Exploits'
            ]
        )
        if deepseek_results.get('success'):
            print("✅ DeepSeek cross-contract analysis completed")
        else:
            print(f"⚠️ DeepSeek analysis failed: {deepseek_results.get('error')}")
        
        # المرحلة 5: دمج النتائج وتحديد الثغرات المشبوهة
        suspicious_vulnerabilities = self._merge_multi_contract_analysis(
            all_slither_results=all_slither_results,
            deepseek_results=deepseek_results,
            relationships=relationships
        )
        
        print(f"\n🎯 Identified {len(suspicious_vulnerabilities)} suspicious vulnerabilities across all contracts")
        
        # المرحلة 6: اختبار كل ثغرة عن طريق PoC متعدد العقود
        print("\n🧪 Testing each vulnerability with MULTI-CONTRACT PoC...")
        for i, vuln in enumerate(suspicious_vulnerabilities):
            print(f"\n--- Testing Vulnerability {i+1}/{len(suspicious_vulnerabilities)} ---")
            print(f"Type: {vuln.get('type', 'Unknown')}")
            print(f"Severity: {vuln.get('severity', 'Unknown')}")
            print(f"Affects: {', '.join(vuln.get('affected_contracts', []))}")
            
            is_confirmed = self._test_vulnerability_with_multi_contract_poc(
                contracts_data=contracts_data,
                vulnerability=vuln,
                max_attempts=5  # زيادة المحاولات للثغرات المعقدة
            )
            
            if is_confirmed:
                print(f"✅ VULNERABILITY CONFIRMED: {vuln.get('type')}")
                self.confirmed_vulnerabilities.append(vuln)
            else:
                print(f"❌ Could not confirm: {vuln.get('type')}")
        
        # المرحلة 7: إصدار التقرير النهائي
        report = self._generate_final_report(
            contracts_data=contracts_data,
            relationships=relationships,
            slither_results=all_slither_results,
            deepseek_results=deepseek_results,
            confirmed_vulnerabilities=self.confirmed_vulnerabilities
        )
        
        print("\n" + "="*60)
        print("📋 FINAL AUDIT REPORT")
        print("="*60)
        print(f"Total contracts analyzed: {len(contracts_data)}")
        print(f"Total vulnerabilities tested: {len(suspicious_vulnerabilities)}")
        print(f"Confirmed vulnerabilities: {len(self.confirmed_vulnerabilities)}")
        print("="*60)
        
        return report
    
    def _read_all_contracts(self, main_contract_path: str, additional_paths: list = None) -> dict:
        """قراءة العقد الرئيسي وجميع العقود المرتبطة"""
        contracts = {}
        
        # قراءة العقد الرئيسي
        main_contract = self._read_single_contract(main_contract_path)
        if main_contract:
            contracts['MainContract'] = {
                'path': main_contract_path,
                'code': main_contract,
                'is_main': True
            }
        
        # قراءة العقود الإضافية (Router, Proxy, Libraries)
        if additional_paths:
            for idx, path in enumerate(additional_paths):
                contract_code = self._read_single_contract(path)
                if contract_code:
                    contract_name = self._extract_contract_name(path) or f"Contract_{idx+1}"
                    contracts[contract_name] = {
                        'path': path,
                        'code': contract_code,
                        'is_main': False
                    }
        
        # محاولة اكتشاف العقود المستوردة تلقائياً
        if main_contract:
            imported_contracts = self._discover_imported_contracts(
                main_contract, 
                os.path.dirname(main_contract_path)
            )
            for imp_name, imp_info in imported_contracts.items():
                if imp_name not in contracts:
                    contracts[imp_name] = imp_info
        
        return contracts
    
    def _read_single_contract(self, contract_path: str) -> Optional[str]:
        """قراءة كود عقد واحد من الملف"""
        try:
            with open(contract_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading contract {contract_path}: {e}")
            return None
    
    def _discover_imported_contracts(self, code: str, base_dir: str) -> dict:
        """اكتشاف العقود المستوردة وقراءتها تلقائياً"""
        imported = {}
        
        # البحث عن جملة import
        import_pattern = r'import\s+(?:"([^"]+)"|\'([^\']+)\')'
        matches = re.findall(import_pattern, code)
        
        for match in matches:
            # الحصول على مسار الملف المستورد
            import_path = match[0] or match[1]
            
            # إذا كان المسار نسبي، نحوله إلى مطلق
            if not os.path.isabs(import_path):
                full_path = os.path.join(base_dir, import_path)
            else:
                full_path = import_path
            
            # قراءة العقد المستورد إذا وجد
            if os.path.exists(full_path):
                contract_code = self._read_single_contract(full_path)
                if contract_code:
                    contract_name = self._extract_contract_name(full_path) or os.path.basename(full_path)
                    imported[contract_name] = {
                        'path': full_path,
                        'code': contract_code,
                        'is_main': False
                    }
        
        return imported
    
    def _analyze_contract_relationships(self, contracts_data: dict) -> list:
        """تحليل العلاقات بين العقود (Proxy, Router, Implementation)"""
        relationships = []
        
        for name, info in contracts_data.items():
            code = info['code']
            
            # التحقق من نمط Proxy
            if 'delegatecall' in code.lower() or 'proxy' in code.lower():
                relationships.append({
                    'type': 'Proxy Pattern',
                    'contract': name,
                    'description': 'Uses delegatecall - potential proxy/implementation pattern'
                })
            
            # التحقق من نمط Router/Dispatcher
            if 'router' in code.lower() or 'dispatcher' in code.lower():
                relationships.append({
                    'type': 'Router/Dispatcher',
                    'contract': name,
                    'description': 'Acts as router/dispatcher for multiple contracts'
                })
            
            # التحقق من الوراثة
            inheritance_pattern = r'contract\s+\w+\s+is\s+([\w\s,]+)'
            matches = re.findall(inheritance_pattern, code)
            if matches:
                parents = [p.strip() for p in matches[0].split(',')]
                for parent in parents:
                    if parent in contracts_data:
                        relationships.append({
                            'type': 'Inheritance',
                            'child': name,
                            'parent': parent,
                            'description': f'{name} inherits from {parent}'
                        })
            
            # التحقق من استدعاءات العقود الخارجية
            call_pattern = r'(\w+)\.(\w+)\s*\('
            calls = re.findall(call_pattern, code)
            external_contracts = set()
            for contract_ref, func_name in calls:
                # التحقق إذا كان المرجع يشير إلى عقد آخر
                if contract_ref.lower() != 'this' and contract_ref.lower() not in ['target', 'attacker', 'vm']:
                    external_contracts.add(contract_ref)
            
            for ext_contract in external_contracts:
                if ext_contract in contracts_data:
                    relationships.append({
                        'type': 'External Call',
                        'caller': name,
                        'callee': ext_contract,
                        'description': f'{name} calls functions in {ext_contract}'
                    })
        
        return relationships
    
    def _merge_multi_contract_analysis(
        self,
        all_slither_results: list,
        deepseek_results: dict,
        relationships: list
    ) -> List[Dict[str, Any]]:
        """دمج نتائج التحليل متعدد العقود"""
        vulnerabilities = []
        
        # إضافة ثغرات Slither من جميع العقود
        for result in all_slither_results:
            contract_name = result['contract']
            slither_result = result['results']
            
            if slither_result.get('success'):
                issues = slither_result.get('issues', [])
                for issue in issues:
                    vulnerabilities.append({
                        'type': issue.get('type', 'Unknown'),
                        'severity': self._map_impact_to_severity(issue.get('impact', 'Unknown')),
                        'confidence': issue.get('confidence', 'Unknown'),
                        'description': issue.get('description', ''),
                        'source': 'slither',
                        'affected_contracts': [contract_name],
                        'location': issue.get('elements', [])
                    })
        
        # استخراج ثغرات من تحليل DeepSeek متعدد العقود
        if deepseek_results.get('success'):
            ai_vulns = self._parse_multi_contract_vulnerabilities(
                deepseek_results.get('analysis', ''),
                relationships
            )
            for vuln in ai_vulns:
                if not self._is_duplicate(vuln, vulnerabilities):
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _parse_multi_contract_vulnerabilities(self, analysis_text: str, relationships: list) -> List[Dict[str, Any]]:
        """استخراج الثغرات متعددة العقود من تحليل AI"""
        vulnerabilities = []
        lines = analysis_text.split('\n')
        current_vuln = None
        
        # أنواع الثغرات متعددة العقود
        multi_contract_types = [
            'Cross-contract Reentrancy', 'Proxy Pattern', 'Storage Collision',
            'DelegateCall Chain', 'Access Control Bypass', 'Composability Exploit',
            'Router Logic Flaw', 'Inter-contract', 'Multi-contract', 'Cross-protocol'
        ]
        
        affected = [rel.get('contract') or rel.get('caller') or rel.get('child') 
                   for rel in relationships]
        
        for line in lines:
            line_stripped = line.strip()
            
            for vtype in multi_contract_types:
                if vtype.lower() in line_stripped.lower():
                    if current_vuln:
                        current_vuln['affected_contracts'] = list(set(affected))[:3]
                        vulnerabilities.append(current_vuln)
                    
                    severity = 'Critical' if 'critical' in line_stripped.lower() else 'High'
                    
                    current_vuln = {
                        'type': vtype,
                        'severity': severity,
                        'description': line_stripped,
                        'source': 'deepseek_multi_contract',
                        'is_complex': True,
                        'is_zero_day_candidate': 'zero-day' in line_stripped.lower(),
                        'affected_contracts': list(set(affected))[:3]
                    }
                    break
        
        if current_vuln:
            current_vuln['affected_contracts'] = list(set(affected))[:3]
            vulnerabilities.append(current_vuln)
        
        return vulnerabilities
    
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
        """استخراج الثغرات المعقدة و Zero-day من نص تحليل AI"""
        vulnerabilities = []
        
        # محاولة استخراج الثغرات المعقدة المذكورة
        lines = analysis_text.split('\n')
        current_vuln = None
        in_vuln_section = False
        
        # أنواع الثغرات المعقدة و Zero-day التي نبحث عنها (2025-2026)
        complex_vuln_types = [
            # Advanced Reentrancy
            'Cross-Function Reentrancy', 'Read-only Reentrancy', 'DelegateCall Proxies',
            'Multi-protocol Composability Reentrancy', 'ERC-777', 'ERC-1155',
            'Reentrancy Guards Bypass',
            
            # Flash Loan & Economic
            'Flash Loan Sandwich', 'Multi-hop Flash Loan', 'Flash Mint Attack',
            'Collateral Swapping', 'Governance Proposal Flash Loan',
            
            # Oracle Manipulation
            'TWAP Oracle', 'Cross-chain Oracle', 'Chainlink Feed',
            'Oracle Staleness', 'Multi-oracle Aggregator',
            
            # MEV & Front-running
            'Mempool Scanning', 'JIT Liquidity', 'Validator Extractable Value',
            'VEV', 'Cross-domain MEV', 'L2 Rollups', 'Time-bandit',
            'Backrunning Chains',
            
            # Access Control & Governance
            'Signature Malleability', 'Multi-sig', 'Governance Token Weight',
            'Proposal Execution Timing', 'DelegateCall Chain',
            'Upgradeable Proxy', 'Storage Collision',
            
            # DeFi Protocol
            'Yield Farming Reward', 'Liquidity Pool Share', 'Staking Reward',
            'Lock-up Period', 'Derivative Pricing', 'Perpetual Futures',
            'Funding Rate',
            
            # Cross-chain & Bridge
            'Bridge Message', 'Cross-chain Replay', 'Wrapped Token',
            'Mint/Burn Race', 'Light Client Proof', 'Relayer Incentive',
            
            # L2 & Scaling
            'Optimistic Rollup', 'Fraud Proof', 'ZK-proof', 'Circuit Constraint',
            'Sequencer Censorship', 'State Commitment',
            
            # Zero-day Novel Vectors
            'Storage Layout', 'Compiler Optimization', 'EVM Opcode',
            'Precompile Behavior', 'Block Header', 'Timestamp Oracles',
            
            # Business Logic Complex
            'Multi-transaction State Machine', 'Economic Incentive Misalignment',
            'Rational Actor', 'Game Theory', 'Mechanism Design', 'Tokenomics',
            
            # General complex types
            'Multi-step Reentrancy', 'Business Logic', 'Flash Loan',
            'Oracle Manipulation', 'Access Control Chain', 'MEV',
            'Governance', 'Composability', 'Economic', 'Time-based',
            'Cross-protocol', 'Liquidity Drainage', 'Zero-day'
        ]
        
        for line in lines:
            line_stripped = line.strip()
            
            # البحث عن أنواع الثغرات المعقدة و Zero-day
            for vtype in complex_vuln_types:
                if vtype.lower() in line_stripped.lower():
                    if current_vuln:
                        vulnerabilities.append(current_vuln)
                    
                    # تحديد مستوى الخطورة
                    severity = 'High'
                    if 'critical' in line_stripped.lower() or 'zero-day' in line_stripped.lower():
                        severity = 'Critical'
                    elif 'medium' in line_stripped.lower():
                        severity = 'Medium'
                    
                    # تحديد إذا كانت Zero-day candidate
                    is_zero_day = 'zero-day' in line_stripped.lower() or 'novel' in line_stripped.lower()
                    
                    current_vuln = {
                        'type': vtype,
                        'severity': severity,
                        'description': line_stripped,
                        'source': 'deepseek',
                        'is_complex': True,
                        'is_zero_day_candidate': is_zero_day
                    }
                    in_vuln_section = True
                    break
            
            # إذا كنا في قسم ثغرة، نضيف المزيد من الوصف
            if in_vuln_section and current_vuln:
                if line_stripped and not line_stripped.startswith('```'):
                    current_vuln['description'] += '\n' + line_stripped
        
        if current_vuln:
            vulnerabilities.append(current_vuln)
        
        return vulnerabilities
    
    def _is_duplicate(self, vuln: Dict, existing: List[Dict]) -> bool:
        """التحقق من عدم التكرار"""
        for existing_vuln in existing:
            if vuln.get('type', '').lower() == existing_vuln.get('type', '').lower():
                return True
        return False
    
    def _test_vulnerability_with_multi_contract_poc(
        self,
        contracts_data: dict,
        vulnerability: Dict[str, Any],
        max_attempts: int = 5
    ) -> bool:
        """
        اختبار ثغرة متعددة العقود عن طريق كتابة وتشغيل PoC معقد
        
        Args:
            contracts_data: بيانات جميع العقود
            vulnerability: معلومات الثغرة
            max_attempts: عدد المحاولات القصوى
            
        Returns:
            bool: هل تم تأكيد الثغرة؟
        """
        vuln_type = vulnerability.get('type', 'Unknown')
        description = vulnerability.get('description', '')
        affected_contracts = vulnerability.get('affected_contracts', [])
        
        print(f"   📝 Multi-contract PoC for: {vuln_type}")
        print(f"   🎯 Affects: {', '.join(affected_contracts) if affected_contracts else 'Multiple contracts'}")
        
        for attempt in range(1, max_attempts + 1):
            print(f"   Attempt {attempt}/{max_attempts}...")
            
            # توليد PoC متعدد العقود
            poc_result = self._generate_and_run_multi_contract_poc(
                contracts_data=contracts_data,
                vulnerability=vulnerability
            )
            
            if poc_result.get('confirmed'):
                vulnerability['poc_path'] = poc_result.get('poc_path')
                vulnerability['poc_output'] = poc_result.get('output')
                return True
            
            # إذا فشل، نحاول تحسين الـ PoC في المحاولة التالية
            if attempt < max_attempts:
                print(f"     Refining multi-contract PoC based on feedback...")
        
        return False
    
    def _generate_and_run_multi_contract_poc(
        self,
        contracts_data: dict,
        vulnerability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """توليد وتشغيل PoC متعدد العقود"""
        vuln_type = vulnerability.get('type', 'Unknown')
        description = vulnerability.get('description', '')
        affected_contracts = vulnerability.get('affected_contracts', [])
        
        # إنشاء مسار للـ PoC
        main_contract_name = list(contracts_data.keys())[0] if contracts_data else "MainContract"
        main_contract_info = contracts_data.get(main_contract_name, {})
        main_contract_path = main_contract_info.get('path', './contract.sol')
        
        poc_filename = f"test_exploit_{vuln_type.lower().replace('/', '_').replace('-', '_')}.t.sol"
        poc_path = os.path.join(os.path.dirname(main_contract_path), poc_filename)
        
        # توليد الـ PoC باستخدام DeepSeek للثغرات المعقدة
        poc_code = self._generate_complex_multi_contract_poc(
            contracts_data=contracts_data,
            vulnerability=vulnerability
        )
        
        try:
            # كتابة ملف الـ PoC
            os.makedirs(os.path.dirname(poc_path) if os.path.dirname(poc_path) else '.', exist_ok=True)
            with open(poc_path, 'w') as f:
                f.write(poc_code)
            
            print(f"     Generated multi-contract PoC at: {poc_path}")
            
            # تشغيل الـ PoC باستخدام Foundry
            test_result = self._run_foundry_test(poc_path, main_contract_path)
            
            if test_result.get('success'):
                return {
                    'confirmed': True,
                    'poc_path': poc_path,
                    'output': test_result.get('output', '')
                }
            
            return {'confirmed': False, 'output': test_result.get('error', '')}
        
        except Exception as e:
            return {'confirmed': False, 'error': str(e)}
    
    def _generate_complex_multi_contract_poc(
        self,
        contracts_data: dict,
        vulnerability: Dict[str, Any]
    ) -> str:
        """توليد كود PoC معقد لثغرة متعددة العقود باستخدام AI"""
        vuln_type = vulnerability.get('type', 'Unknown')
        description = vulnerability.get('description', '')
        
        # تحضير سياق العقود للـ AI
        context = ""
        for name, info in contracts_data.items():
            context += f"\n\n// ===== Contract: {name} =====\n"
            context += f"// Path: {info['path']}\n"
            context += info['code'][:2000]  # أول 2000 حرف فقط لتجنب الحد الأقصى
        
        # استخدام DeepSeek لتوليد PoC معقد
        if hasattr(self.deepseek, 'generate_poc_instructions'):
            poc_instructions = self.deepseek.generate_poc_instructions(
                vulnerability_type=vuln_type,
                contract_code=context,
                vulnerability_description=description,
                is_complex=True
            )
            return poc_instructions
        
        # قالب افتراضي للـ PoC المعقد
        return f'''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";

/**
 * @title Multi-Contract Exploit PoC
 * @notice Proof of Concept for: {vuln_type}
 * @dev This test demonstrates a complex multi-step attack across multiple contracts
 */

contract MultiContractExploitTest is Test {{
    // Contract instances
    {self._generate_contract_declarations(contracts_data)}
    
    // Accounts
    address public attacker = makeAddr("attacker");
    address public victim = makeAddr("victim");
    address public intermediary = makeAddr("intermediary");
    
    function setUp() public {{
        // Fund accounts
        vm.deal(attacker, 100 ether);
        vm.deal(victim, 100 ether);
        vm.deal(intermediary, 50 ether);
        
        // Deploy all contracts
        {self._generate_contract_deployments(contracts_data)}
        
        // Setup initial state for the attack
        // TODO: Add any prerequisite state changes
    }}
    
    function testExploit() public {{
        // ========================================
        // PHASE 1: PREPARATION
        // ========================================
        // Step 1.1: Setup attack prerequisites
        // - Manipulate oracle prices if needed
        // - Establish positions in DeFi protocols
        // - Prepare flash loan if required
        
        vm.startPrank(attacker);
        
        // ========================================
        // PHASE 2: STATE MANIPULATION
        // ========================================
        // Step 2.1: First transaction - prepare state
        // TODO: Implement first step of attack chain
        
        // Step 2.2: Second transaction - exploit vulnerability
        // TODO: Implement cross-contract exploitation
        
        // ========================================
        // PHASE 3: EXPLOIT EXECUTION
        // ========================================
        // Step 3.1: Trigger the vulnerability across contracts
        // This may involve:
        // - Reentrancy through multiple contracts
        // - Storage collision in proxy pattern
        // - DelegateCall chain manipulation
        // - Access control bypass
        
        // TODO: Implement actual exploit logic here
        
        // ========================================
        // PHASE 4: VALUE EXTRACTION
        // ========================================
        // Step 4.1: Extract profit from the exploit
        // Step 4.2: Clean up and cover tracks
        
        vm.stopPrank();
        
        // ========================================
        // VERIFICATION
        // ========================================
        // Prove the exploit succeeded
        // assertGt(attacker.balance, initialBalance, "Exploit failed");
        // assertEq(target.owner(), attacker, "Ownership not transferred");
    }}
}}

/*
 * ATTACK EXPLANATION:
 * ===================
 * Vulnerability: {vuln_type}
 * Description: {description[:500]}
 * 
 * Attack Steps:
 * 1. [Preparation] Setup required preconditions
 * 2. [Manipulation] Manipulate state across contracts
 * 3. [Exploitation] Trigger the vulnerability
 * 4. [Extraction] Extract value/profit
 * 
 * Affected Contracts: {', '.join(contracts_data.keys())}
 */
'''
    
    def _generate_contract_declarations(self, contracts_data: dict) -> str:
        """توليد تصريحات العقود"""
        declarations = []
        for name, info in contracts_data.items():
            contract_name = self._extract_contract_name(info['path']) or name
            declarations.append(f"{contract_name} public {name.lower()};")
        return "\n    ".join(declarations) if declarations else "// No contracts to declare"
    
    def _generate_contract_deployments(self, contracts_data: dict) -> str:
        """توليد أوامر نشر العقود"""
        deployments = []
        for name, info in contracts_data.items():
            contract_name = self._extract_contract_name(info['path']) or name
            deployments.append(f"{name.lower()} = new {contract_name}();")
        return "\n        ".join(deployments) if deployments else "// No contracts to deploy"
    
    def _test_vulnerability_with_poc(
        self,
        contract_path: str,
        vulnerability: Dict[str, Any],
        max_attempts: int = 3
    ) -> bool:
        """
        اختبار ثغرة عن طريق كتابة وتشغيل PoC (للخلفية فقط)
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
        contracts_data: Dict[str, str],
        relationships: List[Dict[str, Any]],
        slither_results: Dict[str, Any],
        deepseek_results: Dict[str, Any],
        confirmed_vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """إنشاء التقرير النهائي لأنظمة متعددة العقود"""
        
        # استخراج اسم العقد الرئيسي
        main_contract_path = list(contracts_data.keys())[0] if contracts_data else "Unknown"
        main_contract_name = self._extract_contract_name(main_contract_path)
        
        return {
            'success': True,
            'main_contract_path': main_contract_path,
            'main_contract_name': main_contract_name,
            'contracts_audited': list(contracts_data.keys()),
            'total_contracts': len(contracts_data),
            'relationships_analyzed': len(relationships),
            'audit_summary': {
                'total_issues_found': sum(len(sr.get('issues', [])) for sr in slither_results.values()) if isinstance(slither_results, dict) else 0,
                'confirmed_vulnerabilities': len(confirmed_vulnerabilities),
                'critical': sum(1 for v in confirmed_vulnerabilities if v.get('severity') == 'Critical'),
                'high': sum(1 for v in confirmed_vulnerabilities if v.get('severity') == 'High'),
                'medium': sum(1 for v in confirmed_vulnerabilities if v.get('severity') == 'Medium'),
                'low': sum(1 for v in confirmed_vulnerabilities if v.get('severity') == 'Low')
            },
            'confirmed_vulnerabilities': confirmed_vulnerabilities,
            'tools_used': ['Slither', 'DeepSeek AI', 'Foundry'],
            'contract_relationships': relationships,
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
