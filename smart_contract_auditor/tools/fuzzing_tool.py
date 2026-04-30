"""
Fuzzing Tool - Run Echidna and analyze results
أداة تشغيل Echidna للفازينج واختبار العقود الذكية
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from .terminal_tool import TerminalTool


class FuzzingTool:
    """تشغيل Echidna للفازينج واكتشاف الثغرات"""
    
    def __init__(self, timeout_seconds: int = 60, test_limit: int = 100):
        self.timeout_seconds = timeout_seconds
        self.test_limit = test_limit
        self.terminal = TerminalTool(timeout_seconds=timeout_seconds)
    
    def run_echidna(
        self,
        contract_path: str,
        contract_name: Optional[str] = None,
        config_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        تشغيل Echidna على عقد ذكي
        
        Args:
            contract_path: مسار ملف العقد
            contract_name: اسم العقد (اختياري)
            config_path: مسار ملف الإعدادات (اختياري)
            
        Returns:
            dict: نتائج الفازينج
        """
        if not os.path.exists(contract_path):
            return {
                "success": False,
                "error": f"Contract file not found: {contract_path}"
            }
        
        # تحديد اسم العقد من الملف إذا لم يُحدد
        if contract_name is None:
            contract_name = self._extract_contract_name(contract_path)
        
        if contract_name is None:
            return {
                "success": False,
                "error": "Could not determine contract name. Please specify it explicitly."
            }
        
        # بناء أمر Echidna
        command = f"echidna-test {contract_path} --contract {contract_name}"
        
        if config_path and os.path.exists(config_path):
            command += f" --config {config_path}"
        
        command += f" --test-limit {self.test_limit}"
        
        # تنفيذ الأمر
        exit_code, stdout, stderr = self.terminal.execute(
            command,
            timeout=self.timeout_seconds
        )
        
        # تحليل النتائج
        properties_failed = self._parse_failed_properties(stdout)
        
        return {
            "success": exit_code == 0,
            "output": stdout,
            "error": stderr,
            "properties_tested": self._count_properties(stdout),
            "properties_failed": len(properties_failed),
            "failed_properties": properties_failed,
            "exit_code": exit_code
        }
    
    def _extract_contract_name(self, contract_path: str) -> Optional[str]:
        """
        استخراج اسم العقد الأول من الملف
        
        Args:
            contract_path: مسار ملف العقد
            
        Returns:
            str or None: اسم العقد
        """
        try:
            with open(contract_path, 'r') as f:
                content = f.read()
            
            # البحث عن تعريف العقد
            import re
            match = re.search(r'contract\s+(\w+)', content)
            if match:
                return match.group(1)
            
            return None
        except Exception:
            return None
    
    def _parse_failed_properties(self, output: str) -> List[Dict[str, Any]]:
        """
        تحليل الخصائص التي فشلت في الاختبار
        
        Args:
            output: مخرجات Echidna
            
        Returns:
            list: قائمة الخصائص الفاشلة
        """
        failed = []
        lines = output.split('\n')
        
        for line in lines:
            if 'failed' in line.lower() or 'assertion failed' in line.lower():
                failed.append({
                    "property": line.strip(),
                    "description": "Property violated during fuzzing"
                })
        
        return failed
    
    def _count_properties(self, output: str) -> int:
        """
        عد عدد الخصائص التي تم اختبارها
        
        Args:
            output: مخرجات Echidna
            
        Returns:
            int: عدد الخصائص
        """
        count = 0
        lines = output.split('\n')
        
        for line in lines:
            if 'echidna' in line.lower() and 'test' in line.lower():
                count += 1
        
        return max(count, 1)
    
    def create_echidna_config(
        self,
        output_path: str,
        contract_name: Optional[str] = None,
        test_limit: Optional[int] = None
    ) -> bool:
        """
        إنشاء ملف إعدادات لـ Echidna
        
        Args:
            output_path: مسار ملف الإعدادات
            contract_name: اسم العقد
            test_limit: حد الاختبارات
            
        Returns:
            bool: نجاح الإنشاء
        """
        config = {
            "testLimit": test_limit or self.test_limit,
            "seqLen": 100,
            "shrinkLimit": 5000,
            "coverage": True,
            "printLogs": True
        }
        
        if contract_name:
            config["contract"] = contract_name
        
        try:
            with open(output_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception:
            return False
    
    def run_property_test(
        self,
        contract_path: str,
        property_name: str,
        contract_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        اختبار خاصية محددة
        
        Args:
            contract_path: مسار العقد
            property_name: اسم الخاصية
            contract_name: اسم العقد
            
        Returns:
            dict: نتيجة الاختبار
        """
        if contract_name is None:
            contract_name = self._extract_contract_name(contract_path)
        
        command = f"echidna-test {contract_path} --contract {contract_name} --property {property_name}"
        exit_code, stdout, stderr = self.terminal.execute(command)
        
        return {
            "success": exit_code == 0,
            "property": property_name,
            "output": stdout,
            "error": stderr,
            "passed": exit_code == 0
        }
