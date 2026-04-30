// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Vulnerable contract for testing purposes
contract VulnerableVault {
    mapping(address => uint256) public balances;
    
    // Deposit function
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    
    // Withdraw function - VULNERABLE TO REENTRANCY
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // External call before state update (reentrancy vulnerability)
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        // State update after external call
        balances[msg.sender] -= amount;
    }
    
    // Get contract balance
    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
