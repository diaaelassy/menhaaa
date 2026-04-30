"""
DeepSeek Tool - Connect to DeepSeek API for deep analysis
أداة الاتصال بـ DeepSeek API للتحليل العميق للعقود الذكية
"""

import requests
from typing import Optional, Dict, Any


class DeepSeekTool:
    """الاتصال بـ DeepSeek API لتحليل العقود الذكية"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com/v1",
        model_name: str = "deepseek-chat",
        timeout_seconds: int = 60
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_contract(
        self,
        contract_code: str,
        vulnerability_types: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        تحليل عقد ذكي لاكتشاف الثغرات
        
        Args:
            contract_code: كود العقد الذكي (Solidity)
            vulnerability_types: أنواع الثغرات المطلوب البحث عنها
            
        Returns:
            dict: نتائج التحليل
        """
        if vulnerability_types is None:
            vulnerability_types = [
                "Reentrancy",
                "Overflow/Underflow",
                "Front-running",
                "Access Control",
                "Business Logic Errors",
                "Gas Optimization",
                "Timestamp Dependence",
                "Denial of Service"
            ]
        
        system_prompt = """You are an expert Smart Contract Security Auditor. 
Analyze the provided Solidity smart contract code for security vulnerabilities.
For each vulnerability found, provide:
1. Vulnerability type
2. Severity (Critical, High, Medium, Low)
3. Location (line number if possible)
4. Description
5. Proof of Concept suggestion
6. Recommended fix

Be precise and only report actual vulnerabilities, not potential issues."""

        user_prompt = f"""Please analyze this Solidity smart contract for the following vulnerability types: {', '.join(vulnerability_types)}

Contract Code:
```solidity
{contract_code}
```

Provide a detailed security analysis with specific vulnerabilities."""

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 4096
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout_seconds
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "analysis": result["choices"][0]["message"]["content"],
                "model": self.model_name,
                "usage": result.get("usage", {})
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Request timed out after {self.timeout_seconds} seconds"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def generate_poc_instructions(
        self,
        vulnerability_type: str,
        contract_code: str,
        vulnerability_description: str
    ) -> str:
        """
        توليد تعليمات لإنشاء Proof of Concept لثغرة محددة
        
        Args:
            vulnerability_type: نوع الثغرة
            contract_code: كود العقد
            vulnerability_description: وصف الثغرة
            
        Returns:
            str: تعليمات إنشاء PoC
        """
        system_prompt = """You are a Smart Contract Security Researcher.
Generate detailed instructions for creating a Foundry test that exploits a specific vulnerability.
The test should use forge-std/Test.sol and include setUp() and testExploit() functions.
Use vm.startPrank and vm.expectRevert when appropriate."""

        user_prompt = f"""Create a Foundry test PoC for this vulnerability:

Vulnerability Type: {vulnerability_type}
Description: {vulnerability_description}

Contract Code:
```solidity
{contract_code}
```

Provide complete Solidity test code that demonstrates the exploit."""

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 4096
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout_seconds
            )
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error generating PoC instructions: {str(e)}"
