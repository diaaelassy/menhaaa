"""
PoC Generator - Generate Foundry test exploit code
أداة توليد كود اختبار Foundry لاستغلال الثغرات
"""

import os
import re
from typing import Dict, Any, Optional, List


class PoCGenerator:
    """توليد اختبارات Foundry PoC للاستغلال المعقد"""
    
    def __init__(self, deepseek_api_key: Optional[str] = None):
        self.template = self._get_base_template()
        self.deepseek_api_key = deepseek_api_key
    
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
    address public attacker;
    address public victim;
    
    // Additional attacker contracts for complex attacks
    // Add your custom attacker contract here if needed
    
    function setUp() public {{
        // Setup accounts
        attacker = makeAddr("attacker");
        victim = makeAddr("victim");
        
        // Fund attacker with ETH
        vm.deal(attacker, 100 ether);
        vm.deal(victim, 100 ether);
        
        // Deploy target contract
        target = new TARGET_CONTRACT();
        
        // TODO: Add any additional setup required for the attack
        // Such as:
        // - Setting up initial state
        // - Deploying helper contracts
        // - Configuring oracle prices
        // - Setting up liquidity pools
    }}
    
    function testExploit() public {{
        // ========================================
        // STEP 1: PREPARATION
        // ========================================
        // Add any preparation steps here
        // Example: attacker deposits funds, sets up positions, etc.
        
        vm.startPrank(attacker);
        
        // ========================================
        // STEP 2: ATTACK EXECUTION
        // ========================================
        // Implement the multi-step attack logic here
        // Use detailed comments to explain each step
        
        // Example attack pattern:
        // 1. Manipulate state in function A
        // 2. Call vulnerable function B
        // 3. Extract profit in function C
        
        // TODO: Replace with actual exploit logic
        
        vm.stopPrank();
        
        // ========================================
        // STEP 3: VERIFICATION
        // ========================================
        // Prove the exploit succeeded
        // Add assertions to verify the attack worked
        
        // Example: assert(attacker.balance > initialBalance);
        // Example: assert(target.totalSupply() < expectedValue);
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
        الحصول على منطق الاستغلال حسب نوع الثغرة المعقدة
        
        Args:
            vulnerability_type: نوع الثغرة
            description: وصف الثغرة
            
        Returns:
            str: كود الاستغلال المعقد
        """
        vuln_lower = vulnerability_type.lower()
        
        # Complex multi-step reentrancy attack (2025-2026 variants)
        if 'reentrancy' in vuln_lower and ('cross-function' in vuln_lower or 'multi' in vuln_lower or 'complex' in vuln_lower):
            return '''// ============================================
// COMPLEX MULTI-STEP REENTRANCY ATTACK (2025-2026)
// Cross-Function Reentrancy with State Shadowing
// ============================================

// Step 1: Deploy attacker contract with malicious fallback/receive
AttackerContract attackerContract = new AttackerContract(target);

// Step 2: Fund attacker contract for the attack
vm.deal(address(attackerContract), 10 ether);

// Step 3: Initial deposit to establish position in function A
vm.startPrank(address(attackerContract));
target.deposit{value: 5 ether}();

// Step 4: Trigger reentrancy through vulnerable function B
// The fallback will call function C before state is updated
attackerContract.attack{value: 1 ether}();

vm.stopPrank();

// Step 5: Verify drain succeeded - attacker has more than deposited
uint256 attackerBalance = address(attackerContract).balance;
assertGt(attackerBalance, 10 ether, "Reentrancy attack failed");'''
        
        # Read-only reentrancy in oracle price feeds
        elif 'read-only' in vuln_lower and 'reentrancy' in vuln_lower:
            return '''// ============================================
// READ-ONLY REENTRANCY IN ORACLE PRICE FEEDS
// ============================================

// Step 1: Setup - deploy malicious contract that calls view functions
OracleAttacker attacker = new OracleAttacker(target);

// Step 2: Manipulate state that affects price calculation
vm.startPrank(attacker);
target.swap{value: 100 ether}(tokenA, tokenB);

// Step 3: During swap, getPrice() is called and reenters
// The view function reads inconsistent state
attacker.exploitWithReadOnlyReentrancy();

vm.stopPrank();

// Step 4: Verify price was manipulated
uint256 manipulatedPrice = target.getPrice();
assertLt(manipulatedPrice, fairPrice, "Read-only reentrancy failed");'''
        
        # Flash loan sandwich attacks
        elif 'flash' in vuln_lower and 'sandwich' in vuln_lower:
            return '''// ============================================
// FLASH LOAN SANDWICH ATTACK ON AMM LIQUIDITY
// ============================================

uint256 initialAttackerBalance = attacker.balance;

vm.startPrank(attacker);

// Step 1: Take flash loan from lending protocol
// IFlashLender(lendingProtocol).flashLoan(token, borrowAmount, callbackData);

// Step 2: Front-run victim's large trade by buying first
target.swap{value: borrowedAmount}(tokenA, tokenB);

// Step 3: Victim's transaction executes at worse price
// (simulated - in real scenario this would be mempool)

// Step 4: Back-run by selling at inflated price
target.swap(boughtTokens, tokenA);

// Step 5: Repay flash loan + fee
// IFlashLender(lendingProtocol).repay(token, borrowAmount + fee);

vm.stopPrank();

assertGt(attacker.balance, initialAttackerBalance, "Sandwich attack failed");'''
        
        # Multi-hop flash loan arbitrage
        elif 'multi-hop' in vuln_lower and 'flash' in vuln_lower:
            return '''// ============================================
// MULTI-HOP FLASH LOAN ARBITRAGE EXPLOIT
// ============================================

uint256 initialBalance = attacker.balance;

vm.startPrank(attacker);

// Hop 1: Borrow from Protocol A
// protocolA.flashLoan(tokenX, 1000 ether, data);

// Hop 2: Swap on DEX 1 (price discrepancy)
// dex1.swap(tokenX, tokenY);

// Hop 3: Swap on DEX 2 (exploit price difference)
// dex2.swap(tokenY, tokenZ);

// Hop 4: Swap back on DEX 3
// dex3.swap(tokenZ, tokenX);

// Hop 5: Repay all flash loans
// protocolA.repay(tokenX, 1000 ether + fee);

vm.stopPrank();

assertGt(attacker.balance, initialBalance, "Multi-hop arbitrage failed");'''
        
        # TWAP Oracle manipulation via multi-block attacks
        elif 'twap' in vuln_lower or ('oracle' in vuln_lower and 'multi-block' in vuln_lower):
            return '''// ============================================
// TWAP ORACLE MANIPULATION VIA MULTI-BLOCK ATTACKS
// ============================================

vm.startPrank(attacker);

// Step 1: Manipulate price over multiple blocks
for (uint256 i = 0; i < 10; i++) {
    vm.roll(block.number + 1);
    target.swap{value: 50 ether}(tokenA, tokenB);
}

// Step 2: TWAP now reflects manipulated price
uint256 manipulatedTwap = target.getTwapPrice();

// Step 3: Exploit by borrowing against inflated collateral
target.borrowAgainstCollateral{value: 100 ether}();

vm.stopPrank();

// Step 4: Verify profit from manipulation
assertGt(attacker.balance, initialBalance, "TWAP manipulation failed");'''
        
        # Cross-chain oracle price desynchronization
        elif 'cross-chain' in vuln_lower and 'oracle' in vuln_lower:
            return '''// ============================================
// CROSS-CHAIN ORACLE PRICE DESYNCHRONIZATION
// ============================================

vm.startPrank(attacker);

// Step 1: Create price discrepancy between chains
// Bridge tokens to L2 where price is stale
target.bridgeToL2(token, amount);

// Step 2: Exploit stale price on L2
// L2 price hasn't updated yet
target.l2Swap{value: amount}(tokenA, tokenB);

// Step 3: Bridge back at profit
target.bridgeFromL2(receivedTokens);

vm.stopPrank();

assertGt(finalTokenBalance, initialTokenBalance, "Cross-chain exploit failed");'''
        
        # MEV extraction strategies
        elif 'mev' in vuln_lower or 'extraction' in vuln_lower:
            return '''// ============================================
// ADVANCED MEV EXTRACTION STRATEGY (2025)
// Validator Extractable Value Post-Merge
// ============================================

vm.startPrank(attacker);

// Step 1: Monitor mempool for profitable transactions
// (simulated - actual implementation requires off-chain component)

// Step 2: Front-run with higher gas price
// target.largeTrade{gasPrice: highGasPrice}();

// Step 3: Back-run for arbitrage
// target.arbitrageOpportunity();

// Step 4: Extract value through ordering manipulation
// In post-merge, validators can reorder within block

vm.stopPrank();

assertGt(attacker.balance, initialBalance, "MEV extraction failed");'''
        
        # Governance manipulation attacks
        elif 'governance' in vuln_lower:
            return '''// ============================================
// GOVERNANCE TOKEN WEIGHT MANIPULATION
// ============================================

vm.startPrank(attacker);

// Step 1: Borrow governance tokens via flash loan
// governanceToken.flashLoan(1000000 tokens);

// Step 2: Create proposal with malicious intent
uint256 proposalId = target.propose(newProposal);

// Step 3: Vote with borrowed tokens
target.vote(proposalId, true);

// Step 4: Execute before returning tokens
target.execute(proposalId);

// Step 5: Return flash loan
// governanceToken.repay(1000000 tokens + fee);

vm.stopPrank();

assertEq(target.currentOwner(), attacker, "Governance attack failed");'''
        
        # Bridge message verification bypass
        elif 'bridge' in vuln_lower and 'message' in vuln_lower:
            return '''// ============================================
// BRIDGE MESSAGE VERIFICATION BYPASS
// ============================================

vm.startPrank(attacker);

// Step 1: Intercept bridge message
bytes memory originalMessage = abi.encode(from, to, amount);

// Step 2: Modify message without invalidating signature
// Exploit missing domain separator or replay protection
bytes memory modifiedMessage = modifyMessage(originalMessage);

// Step 3: Submit modified message to bridge
target.bridgeRelay(modifiedMessage, signature);

// Step 4: Tokens minted to attacker instead of intended recipient
vm.stopPrank();

assertGt(attackerTokenBalance, expectedBalance, "Bridge bypass failed");'''
        
        # Storage layout assumption violations (Zero-day)
        elif 'storage' in vuln_lower and 'layout' in vuln_lower:
            return '''// ============================================
// STORAGE LAYOUT ASSUMPTION VIOLATION (ZERO-DAY)
// ============================================

vm.startPrank(attacker);

// Step 1: Deploy contract with colliding storage slots
StorageAttacker attacker_contract = new StorageAttacker();

// Step 2: Interact with upgradeable proxy
// Proxy storage slot 0 collides with implementation slot
attacker_contract.collideWithTarget(address(target));

// Step 3: Overwrite critical storage variable
// e.g., owner, balance, etc.
attacker_contract.overwriteStorage(maliciousValue);

vm.stopPrank();

// Step 4: Verify storage corruption succeeded
assertEq(target.owner(), attacker, "Storage collision failed");'''
        
        # Compiler optimization side-effects (Zero-day)
        elif 'compiler' in vuln_lower and 'optimization' in vuln_lower:
            return '''// ============================================
// COMPILER OPTIMIZATION SIDE-EFFECTS (ZERO-DAY)
// ============================================

vm.startPrank(attacker);

// Step 1: Trigger specific code path that causes optimizer bug
// This exploits how Solidity optimizer handles certain patterns
target.triggerOptimizerBug{value: 1 ether}();

// Step 2: The optimizer incorrectly removes a security check
// or miscalculates a value due to overflow in optimization

// Step 3: Exploit the incorrect optimized behavior
target.exploitOptimizedPath();

vm.stopPrank();

// Verify the exploit worked due to compiler bug
assertGt(attacker.balance, expectedBalance, "Compiler optimization exploit failed");'''
        
        # Business logic complex chain exploitation
        elif 'business' in vuln_lower or 'logic' in vuln_lower or 'mechanism' in vuln_lower:
            return '''// ============================================
// COMPLEX BUSINESS LOGIC EXPLOITATION CHAIN
// Multi-transaction State Machine Attack
// ============================================

// === TRANSACTION 1: SETUP ===
vm.startPrank(attacker);

// Initialize position with specific parameters
target.initializePosition{value: 10 ether}(param1, param2);

// Set up preconditions without triggering alerts
target.configureSettings(setting1, setting2);

vm.stopPrank();

// === TRANSACTION 2: STATE MANIPULATION ===
vm.roll(block.number + 1);
vm.startPrank(attacker);

// Exploit race condition or timing window
// Call functions in unexpected order
target.functionB(); // Should be called after functionC
target.functionA(); // Creates inconsistent state

vm.stopPrank();

// === TRANSACTION 3: EXPLOIT EXECUTION ===
vm.roll(block.number + 1);
vm.startPrank(attacker);

// Extract value from inconsistent state
target.withdrawMoreThanDeposited();

vm.stopPrank();

// Verify exploit succeeded
assertGt(attacker.balance, totalDeposited, "Business logic exploit failed");'''
        
        # Economic incentive misalignment (Game theory)
        elif 'economic' in vuln_lower or 'game' in vuln_lower or 'incentive' in vuln_lower:
            return '''// ============================================
// ECONOMIC INCENTIVE MISALIGNMENT EXPLOIT
// Game Theory Equilibrium Disruption
// ============================================

vm.startPrank(attacker);

// Step 1: Analyze mechanism design flaw
// Rational actors should behave one way, but...

// Step 2: Exploit misaligned incentives
// target.stake{value: 100 ether}();

// Step 3: Trigger scenario where honest behavior is unprofitable
// Other participants are incentivized to act against protocol

// Step 4: Extract value from broken equilibrium
target.exploitBrokenIncentives();

vm.stopPrank();

// Verify economic exploit profitability
assertGt(attacker.balance, honestBehaviorProfit, "Economic exploit failed");'''
        
        # Access control bypass chain
        elif 'access' in vuln_lower and ('chain' in vuln_lower or 'bypass' in vuln_lower):
            return '''// ============================================
// COMPLEX ACCESS CONTROL BYPASS CHAIN
// DelegateCall Chain Authorization Bypass
// ============================================

vm.startPrank(attacker);

// Step 1: Gain initial low-privilege access
target.registerUser();

// Step 2: Escalate through delegatecall chain
// Contract A delegates to B, which delegates to C
// Each hop loses track of msg.sender vs tx.origin
target.delegateCallChain(hop1, hop2, hop3);

// Step 3: Final hop calls admin function
// But thinks it's being called by owner
target.adminWithdraw();

vm.stopPrank();

assertEq(target.owner(), attacker, "Access bypass chain failed");'''
        
        # Default complex exploit template for unknown types
        else:
            return f'''// ============================================
// COMPLEX ZERO-DAY EXPLOIT FOR: {vulnerability_type}
// Advanced Multi-Step Attack Vector (2025-2026)
// ============================================
// Description: {description[:300]}...

// === PHASE 1: PREPARATION ===
vm.startPrank(attacker);

// Setup required preconditions
// - Fund accounts
// - Deploy helper contracts  
// - Configure initial state
// - Establish positions

// TODO: Add specific preparation steps

vm.stopPrank();

// === PHASE 2: STATE MANIPULATION ===
vm.roll(block.number + 1);
vm.startPrank(attacker);

// Manipulate contract state across multiple functions
// Create inconsistent or exploitable state
// May require multiple transactions

// TODO: Add specific manipulation steps

vm.stopPrank();

// === PHASE 3: EXPLOIT EXECUTION ===
vm.roll(block.number + 1);
vm.startPrank(attacker);

// Execute the core exploit
// Trigger vulnerable code path
// Extract value from protocol

// TODO: Add specific exploit steps

vm.stopPrank();

// === PHASE 4: VALUE EXTRACTION ===
// Convert exploited position to profit
// Clean up any remaining state

// === VERIFICATION ===
// Add assertions proving exploit succeeded
// assertGt(attacker.balance, initialBalance, "Exploit failed");
// assertEq(target.totalSupply(), 0, "Protocol drained");'''
    
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
