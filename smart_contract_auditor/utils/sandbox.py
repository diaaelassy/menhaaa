"""
Sandbox - Optional Docker-based execution environment
بيئة اختيارية لتشغيل الأوامر في Docker للعزل الأمني
"""

import subprocess
import shlex
from typing import Optional, Tuple


class Sandbox:
    """تشغيل الأوامر في بيئة معزولة باستخدام Docker"""
    
    def __init__(self, use_docker: bool = False):
        self.use_docker = use_docker
        self.container_name = "smart_contract_auditor_sandbox"
    
    def execute(
        self,
        command: str,
        timeout_seconds: int = 60
    ) -> Tuple[int, str, str]:
        """
        تنفيذ أمر في البيئة المعزولة
        
        Args:
            command: الأمر المراد تنفيذه
            timeout_seconds: مهلة التنفيذ
            
        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        if self.use_docker:
            return self._execute_in_docker(command, timeout_seconds)
        else:
            return self._execute_local(command, timeout_seconds)
    
    def _execute_in_docker(
        self,
        command: str,
        timeout_seconds: int
    ) -> Tuple[int, str, str]:
        """تنفيذ أمر في Docker container"""
        try:
            # تشغيل container جديد للأمر
            docker_command = f"docker run --rm -t {self._get_image()} bash -c {shlex.quote(command)}"
            
            result = subprocess.run(
                shlex.split(docker_command),
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            return result.returncode, result.stdout, result.stderr
        
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout_seconds} seconds"
        except Exception as e:
            return -2, "", f"Docker execution failed: {str(e)}"
    
    def _execute_local(
        self,
        command: str,
        timeout_seconds: int
    ) -> Tuple[int, str, str]:
        """تنفيذ أمر محلياً (بدون Docker)"""
        try:
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            return result.returncode, result.stdout, result.stderr
        
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout_seconds} seconds"
        except Exception as e:
            return -2, "", f"Local execution failed: {str(e)}"
    
    def _get_image(self) -> str:
        """الحصول على صورة Docker المناسبة"""
        # يمكن تخصيص الصورة حسب الحاجة
        return "python:3.10-slim"
    
    def setup_environment(self) -> bool:
        """
        إعداد البيئة المعزولة
        
        Returns:
            bool: نجاح الإعداد
        """
        if not self.use_docker:
            return True
        
        try:
            # التحقق من وجود Docker
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("Docker is not installed or not running")
                self.use_docker = False
                return False
            
            # سحب الصورة إذا لزم الأمر
            image = self._get_image()
            print(f"Ensuring Docker image {image} is available...")
            
            return True
        
        except Exception as e:
            print(f"Failed to setup sandbox: {e}")
            self.use_docker = False
            return False
