# 🚀 كيفية تدقيق عقود Ithaca Protocol

## المتطلبات الأساسية:

### 1. تثبيت Foundry (لاختبار PoC)
```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### 2. تثبيت Slither
```bash
pip3 install slither-analyzer
```

### 3. الحصول على مفتاح DeepSeek API
- احصل على المفتاح من: https://platform.deepseek.com/
- أو استخدم أي مفتاح OpenAI-compatible آخر

## تشغيل التدقيق على Ithaca Protocol:

### الطريقة 1: تدقيق العقد الرئيسي فقط
```bash
cd /workspace/smart_contract_auditor
python main.py \
  --contract-path /workspace/ithaca-audit/ithaca-repo/contracts/ledger/Ledger.sol \
  --api-key YOUR_DEEPSEEK_API_KEY_HERE
```

### الطريقة 2: تدقيق متعدد العقود (⭐ موصى به)
```bash
cd /workspace/smart_contract_auditor
python main.py \
  --contract-path /workspace/ithaca-audit/ithaca-repo/contracts/ledger/Ledger.sol \
  --additional-paths \
    /workspace/ithaca-audit/ithaca-repo/contracts/fundlock/Fundlock.sol \
    /workspace/ithaca-audit/ithaca-repo/contracts/registry/Registry.sol \
    /workspace/ithaca-audit/ithaca-repo/contracts/strategies/AaveV3Strategy.sol \
    /workspace/ithaca-audit/ithaca-repo/contracts/access/AccessRestricted.sol \
    /workspace/ithaca-audit/ithaca-repo/contracts/ledger/proxy/LedgerBeaconProxy.sol \
  --api-key YOUR_DEEPSEEK_API_KEY_HERE \
  --output ithaca_audit_report.json
```

## الثغرات المعقدة التي يبحث فيها النظام:

### 🔴 ثغرات متعددة العقود (Multi-Contract):
1. **Cross-contract Reentrancy** - إعادة الدخول عبر عقود متعددة
2. **Storage Collision** في Upgradeable Proxies
3. **DelegateCall Chain Attacks** - هجمات سلسلة التفويض
4. **Access Control Bypass** عبر contracts chain

### 💰 ثغرات DeFi الاقتصادية:
5. **Flash Loan Attacks** - هجمات القروض السريعة
6. **Oracle Manipulation** - التلاعب بأسعار Oracle
7. **Yield Farming Exploits** - استغلال العوائد
8. **MEV Extraction** - استخراج MEV

### 🏛️ أخطاء منطق الأعمال:
9. **Balance Manipulation** عبر updateBalances
10. **Withdrawal Queue Exploits** - استغلال طابور السحب
11. **Strategy Fund Mismanagement** - سوء إدارة أموال الاستراتيجية

## مثال على التقرير المتوقع:

```json
{
  "success": true,
  "contract_name": "Ledger",
  "confirmed_vulnerabilities": [
    {
      "type": "Cross-contract Reentrancy",
      "severity": "Critical",
      "affected_contracts": ["Ledger", "Fundlock"],
      "description": "...",
      "poc_path": "/path/to/test_exploit.t.sol"
    }
  ],
  "recommendation": "DO NOT DEPLOY - Critical vulnerabilities found"
}
```

## ملاحظات مهمة:

⚠️ **النظام لا يؤكد ثغرة إلا إذا:**
- تم توليد PoC قابل للتنفيذ
- نجح اختبار PoC باستخدام Foundry (forge test)
- أثبت الاستغلال الفعلي للثغرة

✅ **الميزات الفريدة:**
- يحاول تعديل PoC حتى 5 مرات قبل التخلي عن الثغرة
- يركز على الثغرات المعقدة متعددة الخطوات
- يكتشف Zero-day المحتملة
- يحلل العلاقات بين Router/Proxy/Implementation

