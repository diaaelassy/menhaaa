"""
Terminal Tool - Execute real commands with timeout
أداة تنفيذ الأوامر في الطرفية مع مهلة زمنية
"""

import subprocess
import shlex
from typing import Optional, Tuple


class TerminalTool:
    """تنفيذ أوامر النظام مع دعم المهلة الزمنية"""
    
    def __init__(self, timeout_seconds: int = 60):
        self.timeout_seconds = timeout_seconds
    
    def execute(
        self, 
        command: str, 
        cwd: Optional[str] = None,
        capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """
        تنفيذ أمر في الطرفية
        
        Args:
            command: الأمر المراد تنفيذه
            cwd: مجلد العمل (اختياري)
            capture_output: التقاط المخرجات
            
        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        try:
            args = shlex.split(command)
            result = subprocess.run(
                args,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout_seconds
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {self.timeout_seconds} seconds"
        except FileNotFoundError:
            return -2, "", f"Command not found: {command}"
        except Exception as e:
            return -3, "", f"Error executing command: {str(e)}"
    
    def execute_with_retry(
        self,
        command: str,
        max_retries: int = 3,
        cwd: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """
        تنفيذ أمر مع إعادة المحاولة
        
        Args:
            command: الأمر المراد تنفيذه
            max_retries: عدد المحاولات القصوى
            cwd: مجلد العمل
            
        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        last_error = None
        for attempt in range(max_retries):
            exit_code, stdout, stderr = self.execute(command, cwd)
            if exit_code == 0:
                return exit_code, stdout, stderr
            last_error = (exit_code, stdout, stderr)
        
        return last_error if last_error else (-1, "", "Unknown error")
