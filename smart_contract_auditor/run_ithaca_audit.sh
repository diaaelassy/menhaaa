#!/bin/bash
# تشغيل تدقيق Ithaca Protocol

CONTRACT_PATH="/workspace/ithaca-audit/ithaca-repo/contracts/access/AccessController.sol"
API_KEY="${DEEPSEEK_API_KEY:-YOUR_API_KEY_HERE}"

echo "🚀 Starting Ithaca Protocol Audit..."
echo "📄 Contract: $CONTRACT_PATH"
echo "🔑 API Key: ${API_KEY:0:10}..."

cd /workspace/smart_contract_auditor

python test_quick_audit.py --contract "$CONTRACT_PATH" --api-key "$API_KEY"
