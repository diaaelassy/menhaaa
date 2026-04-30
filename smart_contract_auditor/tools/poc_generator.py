"""
PoC Generator - Generate Foundry test exploit code
أداة توليد كود اختبار Foundry لاستغلال الثغرات
"""

import os
import re
from typing import Dict, Any, Optional, List


class PoCGenerator:
    """توليد اختبارات Foundry PoC للاستغلال"""
    
    def __init__(self):
        self.template = self._get_base_template()
    
    def _get_base_template(self) -> str:
        """
        الحصول على القالب الأساسي لاختبار Foundry
        
        Returns:
            str: قالب الاختبار
        """
        return '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import {TARGET_CONTRACT} from "{CONTRACT_PATH}";

contract ExploitTest is Test {{
    TARGET_CONTRACT public target;
    
    function setUp() public {{
        target = new TARGET_CONTRACT();
    }}
    
    function testExploit() public {{
        // TODO: Implement exploit logic here
        // Use vm.startPrank() to impersonate accounts
        // Use vm.expectRevert() to expect specific errors
        // Demonstrate the vulnerability
    }}
}}
'''
    
    def generate_poc(
        self,
        contract_path: str,
        contract_name: str,
        vulnerability_type: str,
        vulnerability_description: str,
        output_path: str
    ) -> Dict[str, Any]:
        """
        توليد PoC لثغرة محددة
        
        Args:
            contract_path: مسار العقد المستهدف
            contract_name: اسم العقد
            vulnerability_type: نوع الثغرة
            vulnerability_description: وصف الثغرة
            output_path: مسار ملف الإخراج
            
        Returns:
            dict: نتيجة التوليد
        """
        try:
            # قراءة كود العقد الأصلي
            with open(contract_path, 'r') as f:
                original_code = f.read()
            
            # استخراج imports من العقد الأصلي
            imports = self._extract_imports(original_code)
            
            # بناء كود الاختبار
            test_code = self._build_test_code(
                contract_name=contract_name,
                contract_path=contract_path,
                vulnerability_type=vulnerability_type,
                vulnerability_description=vulnerability_description,
                imports=imports
            )
            
            # كتابة الملف
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(test_code)
            
            return {
                "success": True,
                "output_path": output_path,
                "contract_name": contract_name,
                "vulnerability_type": vulnerability_type,
                "lines_of_code": len(test_code.split('\n'))
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate PoC: {str(e)}"
            }
    
    def _extract_imports(self, code: str) -> List[str]:
        """
        استخراج جملة import من الكود
        
        Args:
            code: كود العقد
            
        Returns:
            list: قائمة الـ imports
        """
        imports = []
        for line in code.split('\n'):
            if line.strip().startswith('import'):
                imports.append(line.strip())
        return imports
    
    def _build_test_code(
        self,
        contract_name: str,
        contract_path: str,
        vulnerability_type: str,
        vulnerability_description: str,
        imports: List[str]
    ) -> str:
        """
        بناء كود الاختبار الكامل
        
        Args:
            contract_name: اسم العقد
            contract_path: مسار العقد
            vulnerability_type: نوع الثغرة
            vulnerability_description: وصف الثغرة
            imports: قائمة الـ imports
            
        Returns:
            str: كود الاختبار
        """
        # تخصيص القالب حسب نوع الثغرة
        exploit_logic = self._get_exploit_logic(vulnerability_type, vulnerability_description)
        
        template = self.template.replace(
            "TARGET_CONTRACT", 
            contract_name
        ).replace(
            "{CONTRACT_PATH}",
            contract_path
        )
        
        # إضافة exploit logic مخصص
        template = template.replace(
            "// TODO: Implement exploit logic here\n        // Use vm.startPrank() to impersonate accounts\n        // Use vm.expectRevert() to expect specific errors\n        // Demonstrate the vulnerability",
            exploit_logic
        )
        
        return template
    
    def _get_exploit_logic(self, vulnerability_type: str, description: str) -> str:
        """
        الحصول على منطق الاستغلال حسب نوع الثغرة
        
        Args:
            vulnerability_type: نوع الثغرة
            description: وصف الثغرة
            
        Returns:
            str: كود الاستغلال
        """
        vuln_lower = vulnerability_type.lower()
        
        if 'reentrancy' in vuln_lower:
            return '''// Reentrancy Attack Example
        address attacker = address(this);
        
        // Start prank to impersonate attacker
        vm.startPrank(attacker);
        
        // Call vulnerable function that makes external call before state update
        // Example: target.withdraw(amount);
        
        // The attack happens in the fallback/receive function
        // which re-calls the withdraw function
        
        vm.stopPrank();
        
        // Verify the exploit succeeded
        assert(attacker.balance > 0);'''
        
        elif 'overflow' in vuln_lower or 'underflow' in vuln_lower:
            return '''// Overflow/Underflow Attack Example
        uint256 largeAmount = type(uint256).max;
        
        vm.startPrank(address(this));
        
        // Trigger overflow/underflow
        // Example: target.process(largeAmount);
        
        vm.stopPrank();
        
        // Verify unexpected behavior occurred'''
        
        elif 'front-run' in vuln_lower or 'frontrun' in vuln_lower:
            return '''// Front-running Attack Example
        // Observe pending transaction in mempool
        // Submit competing transaction with higher gas price
        
        vm.startPrank(address(this));
        
        // Example: If victim is buying tokens, buy first
        // target.buyTokens{gasPrice: highGasPrice}(amount);
        
        vm.stopPrank();
        
        // Verify profit from front-running'''
        
        elif 'access control' in vuln_lower or 'access_control' in vuln_lower:
            return '''// Access Control Bypass Example
        address unauthorized = address(0x1337);
        
        vm.startPrank(unauthorized);
        
        // Call admin-only function without proper checks
        // Example: target.adminFunction();
        
        vm.stopPrank();
        
        // Verify unauthorized access succeeded'''
        
        else:
            return f'''// Exploit for: {vulnerability_type}
        // Description: {description[:100]}...
        
        vm.startPrank(address(this));
        
        // TODO: Implement specific exploit logic based on vulnerability
        // Consult the analysis report for details
        
        vm.stopPrank();
        
        // Add assertions to verify exploit success'''
    
    def generate_from_analysis(
        self,
        contract_path: str,
        analysis_result: Dict[str, Any],
        output_dir: str
    ) -> List[Dict[str, Any]]:
        """
        توليد PoCs متعددة من نتائج التحليل
        
        Args:
            contract_path: مسار العقد
            analysis_result: نتائج التحليل
            output_dir: مجلد الإخراج
            
        Returns:
            list: قائمة نتائج التوليد
        """
        results = []
        
        issues = analysis_result.get('issues', [])
        contract_name = self._extract_contract_name(contract_path)
        
        for i, issue in enumerate(issues):
            vuln_type = issue.get('type', 'Unknown')
            description = issue.get('description', 'No description')
            
            output_path = os.path.join(
                output_dir,
                f"exploit_{i}_{vuln_type.lower().replace('/', '_')}.t.sol"
            )
            
            result = self.generate_poc(
                contract_path=contract_path,
                contract_name=contract_name or "TargetContract",
                vulnerability_type=vuln_type,
                vulnerability_description=description,
                output_path=output_path
            )
            
            results.append(result)
        
        return results
    
    def _extract_contract_name(self, contract_path: str) -> Optional[str]:
        """
        استخراج اسم العقد من الملف
        
        Args:
            contract_path: مسار الملف
            
        Returns:
            str or None: اسم العقد
        """
        try:
            with open(contract_path, 'r') as f:
                content = f.read()
            
            match = re.search(r'contract\s+(\w+)', content)
            if match:
                return match.group(1)
            
            return None
        except Exception:
            return None
