"""
Slither Tool - Run Slither static analyzer and extract results
أداة تشغيل Slither لاستخراج نتائج التحليل الثابت
"""

import json
import os
from typing import Dict, Any, List, Optional
from .terminal_tool import TerminalTool


class SlitherTool:
    """تشغيل Slither لتحليل العقود الذكية"""
    
    def __init__(self, timeout_seconds: int = 60):
        self.timeout_seconds = timeout_seconds
        self.terminal = TerminalTool(timeout_seconds=timeout_seconds)
    
    def analyze(
        self,
        contract_path: str,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        تحليل عقد باستخدام Slither
        
        Args:
            contract_path: مسار ملف العقد
            output_format: صيغة المخرجات (json أو stdout)
            
        Returns:
            dict: نتائج التحليل
        """
        if not os.path.exists(contract_path):
            return {
                "success": False,
                "error": f"Contract file not found: {contract_path}"
            }
        
        # تشغيل Slither مع مخرجات JSON
        command = f"slither {contract_path} --json /tmp/slither_output.json 2>&1"
        exit_code, stdout, stderr = self.terminal.execute(command)
        
        # Slither قد يعود بـ exit code مختلف عن 0 حتى عند نجاح التحليل
        # المهم أن ملف JSON تم إنشاؤه
        
        # قراءة ملف JSON
        try:
            with open("/tmp/slither_output.json", "r") as f:
                slither_results = json.load(f)
            
            # استخراج النتائج من البنية الجديدة لـ Slither
            results_data = slither_results.get('results', {})
            detectors = results_data.get('detectors', [])
            
            return {
                "success": True,
                "results": slither_results,
                "issues_count": len(detectors),
                "issues": self._parse_issues(slither_results),
                "raw_output": stdout
            }
        except FileNotFoundError:
            # محاولة بدون JSON إذا فشل
            command_simple = f"slither {contract_path} 2>&1"
            exit_code, stdout, stderr = self.terminal.execute(command_simple)
            
            return {
                "success": True,  # Slither يعمل حتى لو وجد مشاكل
                "output": stdout,
                "error": stderr,
                "issues_found": len(stdout.strip()) > 0,
                "issues_count": 0,
                "issues": []
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse Slither JSON: {str(e)}"
            }
    
    def _parse_issues(self, results: Dict) -> List[Dict[str, Any]]:
        """
        استخراج وتحليل الثغرات من نتائج Slither
        
        Args:
            results: نتائج Slither الخام
            
        Returns:
            list: قائمة الثغرات المُحللة
        """
        issues = []
        
        # البنية الجديدة لـ Slither تستخدم results.detectors
        results_data = results.get('results', {})
        raw_issues = results_data.get('detectors', [])
        
        # إذا لم نجد البنية الجديدة، نجرب القديمة
        if not raw_issues:
            raw_issues = results.get('issues', [])
        
        for issue in raw_issues:
            # استخراج معلومات الثغرة
            check_name = issue.get('check', issue.get('name', 'Unknown'))
            impact = issue.get('impact', 'Unknown')
            confidence = issue.get('confidence', 'Unknown')
            
            # استخراج الوصف
            description = ""
            elements_data = issue.get('elements', [])
            if elements_data:
                first_elem = elements_data[0] if elements_data else {}
                description = first_elem.get('description', {}).get('text', '')
                
                # أو من source mapping
                if not description:
                    source_mapping = first_elem.get('source_mapping', {})
                    filename = source_mapping.get('filename_short', '')
                    lines = source_mapping.get('lines', [])
                    if filename and lines:
                        description = f"Found in {filename} at lines {lines}"
            
            parsed_issue = {
                "type": check_name,
                "impact": impact,
                "confidence": confidence,
                "description": description,
                "elements": []
            }
            
            # استخراج العناصر المتأثرة
            for element in elements_data:
                elem_info = {
                    "type": element.get("type", "unknown"),
                    "name": element.get("name", "unknown"),
                    "source_mapping": element.get("source_mapping", {})
                }
                parsed_issue["elements"].append(elem_info)
            
            issues.append(parsed_issue)
        
        return issues
    
    def run_detector(
        self,
        contract_path: str,
        detector_name: str
    ) -> Dict[str, Any]:
        """
        تشغيل كاشف محدد في Slither
        
        Args:
            contract_path: مسار العقد
            detector_name: اسم الكاشف
            
        Returns:
            dict: نتائج الكاشف
        """
        command = f"slither {contract_path} --detect {detector_name}"
        exit_code, stdout, stderr = self.terminal.execute(command)
        
        return {
            "success": exit_code == 0 or exit_code == 1,
            "output": stdout,
            "error": stderr,
            "issues_found": exit_code == 1
        }
    
    def get_supported_detectors(self) -> List[str]:
        """
        الحصول على قائمة الكواشف المدعومة
        
        Returns:
            list: أسماء الكواشف
        """
        command = "slither --list-detectors"
        exit_code, stdout, stderr = self.terminal.execute(command)
        
        if exit_code == 0:
            # تحليل المخرجات لاستخراج أسماء الكواشف
            detectors = []
            for line in stdout.split('\n'):
                if line.strip() and not line.startswith('-'):
                    parts = line.split()
                    if parts:
                        detectors.append(parts[0])
            return detectors
        
        return []
