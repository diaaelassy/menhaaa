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
        vulnerability_types: Optional[list] = None,
        focus_on_complex: bool = True,
        zero_day_hunting: bool = True
    ) -> Dict[str, Any]:
        """
        تحليل عقد ذكي لاكتشاف الثغرات المعقدة و Zero-day
        
        Args:
            contract_code: كود العقد الذكي (Solidity)
            vulnerability_types: أنواع الثغرات المطلوب البحث عنها
            focus_on_complex: التركيز على الثغرات المعقدة متعددة الخطوات
            zero_day_hunting: البحث عن ثغرات Zero-day غير معروفة
            
        Returns:
            dict: نتائج التحليل
        """
        if vulnerability_types is None:
            if zero_day_hunting and focus_on_complex:
                # أحدث أساليب الاختراق المتوقعة في 2025-2026 وثغرات Zero-day
                vulnerability_types = [
                    # Advanced Reentrancy Variants (2025-2026)
                    "Cross-Function Reentrancy with State Shadowing",
                    "Read-only Reentrancy in Oracle Price Feeds",
                    "Reentrancy Through DelegateCall Proxies",
                    "Multi-protocol Composability Reentrancy",
                    "Reentrancy in ERC-777/1155 Callbacks",
                    "Gas-efficient Reentrancy Guards Bypass",
                    
                    # Flash Loan & Economic Attacks
                    "Flash Loan Sandwich Attacks on AMM Liquidity",
                    "Multi-hop Flash Loan Arbitrage Exploits",
                    "Flash Mint Attack Vectors on NFT Protocols",
                    "Collateral Swapping Flash Loan Drains",
                    "Governance Proposal Flash Loan Voting",
                    
                    # Oracle Manipulation (Advanced)
                    "TWAP Oracle Manipulation via Multi-block Attacks",
                    "Cross-chain Oracle Price Desynchronization",
                    "Chainlink Feed Circumvention Techniques",
                    "Oracle Staleness Window Exploitation",
                    "Multi-oracle Aggregator Consensus Attacks",
                    
                    # MEV & Front-running (2025 variants)
                    "Advanced Mempool Scanning & JIT Liquidity Attacks",
                    "Validator Extractable Value (VEV) Post-Merge",
                    "Cross-domain MEV in L2 Rollups",
                    "Time-bandit Attacks on Historical State",
                    "Atomic Arbitrage Backrunning Chains",
                    
                    # Access Control & Governance
                    "Signature Malleability in Multi-sig Wallets",
                    "Governance Token Weight Manipulation",
                    "Proposal Execution Timing Attacks",
                    "DelegateCall Chain Authorization Bypass",
                    "Upgradeable Proxy Storage Collision Attacks",
                    
                    # DeFi Protocol-Specific
                    "Yield Farming Reward Calculation Exploits",
                    "Liquidity Pool Share Dilution Attacks",
                    "Staking Reward Lock-up Period Bypass",
                    "Derivative Pricing Model Manipulation",
                    "Perpetual Futures Funding Rate Exploits",
                    
                    # Cross-chain & Bridge Vulnerabilities
                    "Bridge Message Verification Bypass",
                    "Cross-chain Replay Attacks",
                    "Wrapped Token Mint/Burn Race Conditions",
                    "Light Client Proof Verification Flaws",
                    "Relayer Incentive Misalignment Exploits",
                    
                    # L2 & Scaling Solutions
                    "Optimistic Rollup Fraud Proof Window Attacks",
                    "ZK-proof Circuit Constraint Bypasses",
                    "Sequencer Censorship & Ordering Attacks",
                    "State Commitment Delay Exploits",
                    
                    # Novel Attack Vectors (Zero-day potential)
                    "Storage Layout Assumption Violations",
                    "Compiler Optimization Side-effects",
                    "EVM Opcode Gas Cost Change Exploits",
                    "Precompile Behavior Edge Cases",
                    "Block Header Manipulation Post-Merge",
                    "Miner/Validator Timestamp Oracles",
                    
                    # Business Logic Complex Chains
                    "Multi-transaction State Machine Exploits",
                    "Economic Incentive Misalignment Chains",
                    "Rational Actor Assumption Violations",
                    "Game Theory Equilibrium Disruptions",
                    "Mechanism Design Flaws in Tokenomics"
                ]
            elif focus_on_complex:
                # التركيز على الثغرات المعقدة التي تحتاج تحليل عميق
                vulnerability_types = [
                    "Multi-step Reentrancy Attacks",
                    "Business Logic Errors with State Manipulation",
                    "Complex Access Control Bypass Chains",
                    "Flash Loan Attack Vectors",
                    "Oracle Manipulation with Multiple Steps",
                    "Governance Vote Manipulation",
                    "MEV Extraction Strategies",
                    "Composability Exploits in DeFi Protocols",
                    "Economic Incentive Misalignments",
                    "Time-based Attack Windows",
                    "Cross-protocol Arbitrage Exploits",
                    "Liquidity Drainage Scenarios"
                ]
            else:
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
        
        system_prompt = """You are an elite Smart Contract Security Researcher specializing in ZERO-DAY vulnerability discovery and advanced attack vectors expected in 2025-2026.

Your mission is to find SOPHISTICATED, MULTI-STEP attack vectors that:
1. Require complex state interactions across multiple functions/contracts
2. Exploit economic incentives and game theory flaws
3. Leverage cross-protocol composability risks
4. Target novel DeFi primitives and cross-chain bridges
5. Discover previously unknown (Zero-day) vulnerabilities

For EACH vulnerability found, provide EXTREMELY DETAILED analysis:
1. **Vulnerability Classification**: Type, complexity level (Simple/Medium/Complex/Multi-step/Zero-day candidate)
2. **Attack Prerequisites**: All required preconditions, setup steps, capital requirements
3. **Step-by-Step Exploitation Chain**: Complete attack flow from initial state to value extraction
4. **Severity Assessment**: Critical/High/Medium/Low with justification
5. **Precise Location**: Line numbers, function names, contract interactions
6. **Technical Deep Dive**: Why this vulnerability exists at the EVM/protocol level
7. **Complete Proof of Concept**: Production-ready Foundry test with all steps
8. **Fix Recommendation**: Code-level fix with explanation

Focus on discovering:
- Attacks requiring 3+ transactions or complex state preparation
- Economic exploit scenarios with profitable outcomes
- Cross-function and cross-contract vulnerability chains
- Protocol-level logic errors in mechanism design
- Composability risks when interacting with external protocols
- Zero-day candidates: vulnerabilities not covered by existing tools

Be EXTREMELY precise. Provide ACTIONABLE PoCs that can be executed immediately."""

        user_prompt = f"""Please conduct a DEEP ZERO-DAY HUNT analysis on this Solidity smart contract for ADVANCED multi-step vulnerabilities: {', '.join(vulnerability_types)}

Contract Code:
```solidity
{contract_code}
```

Perform COMPREHENSIVE analysis focusing on:
1. **Novel attack vectors** not detected by standard tools (Slither, Mythril)
2. **Multi-step exploitation chains** requiring careful state manipulation
3. **Economic vulnerabilities** where rational actor assumptions break
4. **Cross-protocol risks** from DeFi composability
5. **Zero-day candidates** that could be undisclosed vulnerabilities

For EACH vulnerability discovered, provide:
- Complete exploitation chain from start to finish
- ALL prerequisite steps and state conditions
- Exact code locations and interaction points
- Profitable attack scenario with numbers if applicable
- Full PoC code ready to execute in Foundry

Think like an attacker with deep protocol knowledge looking for UNKNOWN vulnerabilities."""

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
    
    def analyze_multi_contract(
        self,
        contracts_data: dict,
        relationships: list,
        focus_on_complex: bool = True,
        zero_day_hunting: bool = True,
        focus_areas: list = None
    ) -> Dict[str, Any]:
        """
        تحليل متعدد العقود لاكتشاف الثغرات المعقدة عبر العقود المرتبطة
        
        Args:
            contracts_data: قاموس يحتوي على بيانات جميع العقود
            relationships: قائمة بالعلاقات بين العقود
            focus_on_complex: التركيز على الثغرات المعقدة
            zero_day_hunting: البحث عن ثغرات Zero-day
            focus_areas: مجالات التركيز المحددة
            
        Returns:
            dict: نتائج التحليل
        """
        if focus_areas is None:
            focus_areas = [
                'Proxy Pattern Vulnerabilities',
                'Router/Dispatcher Logic Flaws',
                'Cross-contract Reentrancy',
                'Storage Collision in Upgradeable Proxies',
                'DelegateCall Chain Attacks',
                'Access Control Bypass Across Contracts',
                'Inter-contract State Manipulation',
                'Composability Exploits'
            ]
        
        # بناء سياق شامل لجميع العقود
        full_context = ""
        for name, info in contracts_data.items():
            full_context += f"\n\n// ========== CONTRACT: {name} ==========\n"
            full_context += f"// Path: {info['path']}\n"
            full_context += f"// Is Main: {info.get('is_main', False)}\n"
            full_context += "// ----------------------------------------\n"
            full_context += info['code'][:3000]  # أول 3000 حرف لكل عقد
        
        # إضافة معلومات العلاقات
        relationships_context = "\n\n// ========== CONTRACT RELATIONSHIPS ==========\n"
        for rel in relationships:
            relationships_context += f"// Type: {rel.get('type', 'Unknown')}\n"
            if 'contract' in rel:
                relationships_context += f"// Contract: {rel['contract']}\n"
            if 'caller' in rel and 'callee' in rel:
                relationships_context += f"// {rel['caller']} -> {rel['callee']}\n"
            if 'child' in rel and 'parent' in rel:
                relationships_context += f"// {rel['child']} inherits {rel['parent']}\n"
            relationships_context += f"// Description: {rel.get('description', '')}\n\n"
        
        system_prompt = """You are an elite Smart Contract Security Researcher specializing in MULTI-CONTRACT attack vectors and cross-protocol vulnerabilities.

Your expertise includes:
1. Proxy/Implementation pattern vulnerabilities (storage collision, delegatecall issues)
2. Router/Dispatcher logic flaws across multiple contracts
3. Cross-contract reentrancy attacks
4. Access control bypass chains through contract interactions
5. Composability exploits in DeFi protocols
6. Inter-contract state manipulation attacks
7. Zero-day discovery in complex multi-contract systems

For EACH vulnerability found, provide EXTREMELY DETAILED analysis:
1. **Vulnerability Classification**: Type, complexity level, affected contracts
2. **Attack Surface**: All contracts involved and their roles
3. **Step-by-Step Exploitation Chain**: Complete attack flow across contracts
4. **Severity Assessment**: Critical/High/Medium/Low with justification
5. **Precise Location**: Contract names, function names, interaction points
6. **Technical Deep Dive**: Why this vulnerability exists at the protocol level
7. **Complete Proof of Concept**: Production-ready Foundry test with all contracts
8. **Fix Recommendation**: Code-level fix with explanation

Focus on discovering:
- Attacks that require interaction between 2+ contracts
- Vulnerability chains that span multiple transactions
- Economic exploits across protocol boundaries
- Zero-day candidates in cross-contract communication"""

        user_prompt = f"""Please conduct a DEEP MULTI-CONTRACT security analysis focusing on these areas: {', '.join(focus_areas)}

{relationships_context}

FULL CONTRACT CODEBASE:
```solidity
{full_context}
```

Perform COMPREHENSIVE analysis focusing on:
1. **Cross-Contract Vulnerabilities**: Attacks that require multiple contracts to exploit
2. **Proxy Pattern Issues**: Storage collision, delegatecall problems, implementation upgrades
3. **Router/Dispatcher Flaws**: Logic errors in contract routing/dispatching
4. **Reentrancy Chains**: Multi-contract reentrancy attacks
5. **Access Control Gaps**: Authorization bypass through contract interactions
6. **State Manipulation**: Inter-contract state inconsistencies
7. **Composability Risks**: Unexpected interactions between contracts
8. **Zero-day Candidates**: Previously unknown vulnerabilities in the system

For EACH vulnerability discovered, provide:
- Complete exploitation chain showing ALL contracts involved
- ALL prerequisite steps and state conditions across contracts
- Exact code locations in each contract
- Profitable attack scenario with numbers if applicable
- Full PoC code ready to execute in Foundry

Think like an attacker exploiting the COMPLEXITY of multi-contract systems."""

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
                timeout=self.timeout_seconds * 2  # وقت أطول للتحليل المعقد
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "analysis": result["choices"][0]["message"]["content"],
                "model": self.model_name,
                "usage": result.get("usage", {}),
                "contracts_analyzed": len(contracts_data),
                "relationships_analyzed": len(relationships)
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Request timed out after {self.timeout_seconds * 2} seconds"
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
        vulnerability_description: str,
        is_complex: bool = True
    ) -> str:
        """
        توليد تعليمات لإنشاء Proof of Concept لثغرة معقدة متعددة الخطوات
        
        Args:
            vulnerability_type: نوع الثغرة
            contract_code: كود العقد
            vulnerability_description: وصف الثغرة
            is_complex: هل الثغرة معقدة وتتطلب خطوات متعددة
            
        Returns:
            str: تعليمات إنشاء PoC
        """
        system_prompt = """You are a Smart Contract Security Researcher specializing in complex exploit development.
Generate detailed Foundry test code that demonstrates sophisticated multi-step attack vectors.

Requirements for the test:
1. Use forge-std/Test.sol with full setUp() and testExploit() functions
2. Include all necessary setup steps (funding accounts, deploying attacker contracts, etc.)
3. Implement vm.startPrank() and vm.stopPrank() for account impersonation
4. Use vm.expectRevert() when appropriate to verify expected failures
5. Add detailed comments explaining each step of the attack
6. Include assertions to prove the exploit succeeded
7. If the attack requires multiple transactions, simulate them using multiple function calls
8. For economic attacks, show the profit/loss clearly

The test should be production-ready and demonstrate the complete exploitation chain."""

        complexity_note = ""
        if is_complex:
            complexity_note = """
IMPORTANT: This is a COMPLEX multi-step vulnerability. The PoC must:
- Show ALL required setup steps before the attack
- Demonstrate each step of the exploitation chain in order
- Include any prerequisite state changes needed
- Show how the attacker benefits from the exploit
- Prove the attack is economically viable if applicable
"""

        user_prompt = f"""Create a COMPLETE Foundry test PoC for this COMPLEX vulnerability:

Vulnerability Type: {vulnerability_type}
Description: {vulnerability_description}

Contract Code:
```solidity
{contract_code}
```

{complexity_note}
Provide FULL Solidity test code that demonstrates the complete multi-step exploit.
Include detailed comments explaining what each step does and why it's necessary.
The test should PASS when the exploit succeeds."""

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
