# Smart Contract Auditor Agent - Multi-Contract Security Analysis

نظام متكامل لتدقيق العقود الذكية (Smart Contract Auditor Agent) يستخدم أدوات حقيقية للتحليل واكتشاف الثغرات وتأكيدها عملياً.

## المميزات

- ✅ **قراءة عقود Solidity** من ملفات متعددة (Router, Proxy, Implementation, Libraries)
- ✅ **تحليل العلاقات بين العقود**: Proxy Patterns, DelegateCall Chains, Cross-contract Calls
- ✅ **تحليل ثابت** باستخدام Slither لكل العقود
- ✅ **تحليل ذكي متقدم** باستخدام DeepSeek AI للثغرات المعقدة عبر العقود المتعددة
- ✅ **اكتشاف ثغرات معقدة متعددة الخطوات**: Cross-contract Reentrancy, Storage Collision, Access Control Bypass Chains
- ✅ **اختبار عملي** عبر Fuzzing بـ Echidna
- ✅ **توليد PoC تلقائي** باستخدام Foundry للاستغلال المعقد متعدد العقود
- ✅ **تأكيد الثغرات** بتشغيل الكود فعلياً
- ✅ **تقرير نهائي** بالثغرات المؤكدة فقط

## التركيز على الثغرات المعقدة و Zero-day (2025-2026)

هذا النظام مصمم خصيصاً لاكتشاف **أحدث الثغرات المعقدة متعددة الخطوات** و **ثغرات Zero-day** المتوقعة في 2025-2026، مع تركيز خاص على:

### 🎯 فئات الثغرات المتقدمة

#### 1. Multi-Contract Attack Vectors ⭐ NEW
- **Cross-contract Reentrancy**: هجمات تعبر عدة عقود في سلسلة واحدة
- **Proxy Pattern Vulnerabilities**: Storage collision, delegatecall issues
- **Router/Dispatcher Logic Flaws**: أخطاء في توجيه الاستدعاءات بين العقود
- **Storage Collision in Upgradeable Proxies**: تصادم التخزين في البروكسي القابل للترقية
- **DelegateCall Chain Attacks**: سلاسل DelegateCall عبر عقود متعددة
- **Access Control Bypass Across Contracts**: تجاوز الصلاحيات عبر التفاعلات
- **Inter-contract State Manipulation**: التلاعب بالحالة عبر العقود
- **Composability Exploits**: استغلال التركيبات غير المتوقعة بين العقود

#### 2. Advanced Reentrancy Variants (2025-2026)
- Cross-Function Reentrancy with State Shadowing
- Read-only Reentrancy in Oracle Price Feeds
- Reentrancy Through DelegateCall Proxies
- Multi-protocol Composability Reentrancy
- Reentrancy in ERC-777/1155 Callbacks
- Gas-efficient Reentrancy Guards Bypass

#### 2. Flash Loan & Economic Attacks
- Flash Loan Sandwich Attacks on AMM Liquidity
- Multi-hop Flash Loan Arbitrage Exploits
- Flash Mint Attack Vectors on NFT Protocols
- Collateral Swapping Flash Loan Drains
- Governance Proposal Flash Loan Voting

#### 3. Oracle Manipulation (Advanced)
- TWAP Oracle Manipulation via Multi-block Attacks
- Cross-chain Oracle Price Desynchronization
- Chainlink Feed Circumvention Techniques
- Oracle Staleness Window Exploitation
- Multi-oracle Aggregator Consensus Attacks

#### 4. MEV & Front-running (2025 variants)
- Advanced Mempool Scanning & JIT Liquidity Attacks
- Validator Extractable Value (VEV) Post-Merge
- Cross-domain MEV in L2 Rollups
- Time-bandit Attacks on Historical State
- Atomic Arbitrage Backrunning Chains

#### 5. Access Control & Governance
- Signature Malleability in Multi-sig Wallets
- Governance Token Weight Manipulation
- Proposal Execution Timing Attacks
- DelegateCall Chain Authorization Bypass
- Upgradeable Proxy Storage Collision Attacks

#### 6. DeFi Protocol-Specific
- Yield Farming Reward Calculation Exploits
- Liquidity Pool Share Dilution Attacks
- Staking Reward Lock-up Period Bypass
- Derivative Pricing Model Manipulation
- Perpetual Futures Funding Rate Exploits

#### 7. Cross-chain & Bridge Vulnerabilities
- Bridge Message Verification Bypass
- Cross-chain Replay Attacks
- Wrapped Token Mint/Burn Race Conditions
- Light Client Proof Verification Flaws
- Relayer Incentive Misalignment Exploits

#### 8. L2 & Scaling Solutions
- Optimistic Rollup Fraud Proof Window Attacks
- ZK-proof Circuit Constraint Bypasses
- Sequencer Censorship & Ordering Attacks
- State Commitment Delay Exploits

#### 9. Zero-day Novel Attack Vectors
- Storage Layout Assumption Violations
- Compiler Optimization Side-effects
- EVM Opcode Gas Cost Change Exploits
- Precompile Behavior Edge Cases
- Block Header Manipulation Post-Merge
- Miner/Validator Timestamp Oracles

#### 10. Business Logic Complex Chains
- Multi-transaction State Machine Exploits
- Economic Incentive Misalignment Chains
- Rational Actor Assumption Violations
- Game Theory Equilibrium Disruptions
- Mechanism Design Flaws in Tokenomics

### 🔍 منهجية اكتشاف Zero-day

النظام يستخدم AI متقدم للبحث عن:
- ثغرات غير مكتشفة سابقاً (Zero-day candidates)
- هجمات تتطلب 3+ معاملات أو إعداد حالة معقد
- سيناريوهات استغلال اقتصادي مربحة
- سلاسل ثغرات عبر وظائف وعقود متعددة
- أخطاء منطقية في تصميم الآليات
- مخاطر التركيب عند التفاعل مع بروتوكولات خارجية

## المتطلبات

### البرمجيات الأساسية

- Python 3.10+
- pip (Python package manager)

### الأدوات الخارجية (يتم تثبيتها يدوياً)

```bash
# تثبيت Foundry (forge, cast, anvil)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# تثبيت Slither
pip3 install slither-analyzer

# تثبيت Echidna (اختياري للفازينج)
# راجع: https://github.com/crytic/echidna#installation
```

## التثبيت

```bash
# استنساخ المشروع
cd smart_contract_auditor

# تثبيت المكتبات Python
pip install -r requirements.txt
```

## الاستخدام

### الأمر الأساسي لعقد واحد

```bash
python main.py --contract-path /path/to/contract.sol --api-key sk-xxxxx
```

### تدقيق نظام متعدد العقود (Router + Proxy + Implementation)

```bash
python main.py --contract-path ./Router.sol \
               --additional-paths ./Proxy.sol ./Implementation.sol ./Library.sol \
               --api-key sk-xxxxx
```

### الخيارات المتاحة

| الخيار | الوصف | مطلوب |
|--------|-------|--------|
| `--contract-path` | مسار ملف العقد الذكي الرئيسي | ✅ نعم |
| `--additional-paths` | مسارات ملفات العقود الإضافية (Router, Proxy, Libraries) | ❌ لا |
| `--api-key` | مفتاح DeepSeek API | ✅ نعم |
| `--config` | مسار ملف الإعدادات | ❌ لا (default: config.yaml) |
| `--deepseek-model` | اسم نموذج DeepSeek | ❌ لا (default: deepseek-chat) |
| `--output` | مسار حفظ التقرير (JSON) | ❌ لا |
| `--verbose` | تفعيل الإخراج المفصل | ❌ لا |

### أمثلة

```bash
# تدقيق عقد بسيط
python main.py --contract-path ./MyToken.sol --api-key sk-abc123

# تدقيق نظام متعدد العقود (⭐ NEW)
python main.py --contract-path ./DeFiRouter.sol \
               --additional-paths ./Proxy.sol ./Implementation.sol \
               --api-key sk-abc123

# تدقيق مع حفظ التقرير
python main.py --contract-path ./Protocol.sol --api-key sk-abc123 --output audit_report.json

# استخدام نموذج مختلف
python main.py --contract-path ./NFT.sol --api-key sk-abc123 --deepseek-model deepseek-coder
```

## هيكل المشروع

```
smart_contract_auditor/
├── requirements.txt          # مكتبات Python
├── config.yaml              # ملف الإعدادات
├── main.py                  # واجهة سطر الأوامر
├── tools/                   # أدوات التحليل
│   ├── __init__.py
│   ├── terminal_tool.py     # تنفيذ الأوامر
│   ├── deepseek_tool.py     # اتصال DeepSeek API
│   ├── slither_tool.py      # تحليل Slither
│   ├── fuzzing_tool.py      # فحص Echidna
│   └── poc_generator.py     # توليد PoC
├── core/                    # النواة الرئيسية
│   ├── __init__.py
│   └── audit_agent.py       # الوكيل الرئيسي
└── utils/                   # أدوات مساعدة
    ├── __init__.py
    └── sandbox.py           # بيئة معزولة (Docker)
```

## سير العمل

1. **قراءة العقد** ← تحميل كود Solidity من الملف
2. **تحليل Slither** ← فحص ثابت لاكتشاف الثغرات المعروفة
3. **تحليل DeepSeek** ← تحليل ذكي باستخدام AI
4. **دمج النتائج** ← تحديد الثغرات المشبوهة
5. **توليد PoC** ← كتابة اختبار Foundry لكل ثغرة
6. **تشغيل PoC** ← تنفيذ الاختبار للتأكد
7. **التكرار** ← محاولة تحسين PoC حتى 3 مرات إذا فشل
8. **التقرير النهائي** ← ثغرات مؤكدة فقط

## ملف الإعدادات (config.yaml)

```yaml
deepseek_api_key: "YOUR_API_KEY_HERE"
deepseek_base_url: "https://api.deepseek.com/v1"
model_name: "deepseek-chat"
timeout_seconds: 60
echidna_test_limit: 100
foundry_test_pattern: "test/*.t.sol"
```

## مثال على التقرير

```json
{
  "success": true,
  "contract_name": "VulnerableContract",
  "audit_summary": {
    "total_issues_found": 5,
    "confirmed_vulnerabilities": 2,
    "critical": 1,
    "high": 1,
    "medium": 0,
    "low": 0
  },
  "confirmed_vulnerabilities": [
    {
      "type": "Reentrancy",
      "severity": "Critical",
      "description": "...",
      "poc_path": "./test_exploit_reentrancy.t.sol"
    }
  ],
  "recommendation": "CRITICAL: 1 critical vulnerability found. DO NOT deploy until fixed."
}
```

## الحصول على مفتاح DeepSeek API

1. قم بزيارة [DeepSeek Platform](https://platform.deepseek.com/)
2. سجل حساباً جديداً
3. أنشئ مفتاح API جديد
4. استخدم المفتاح في الأمر أو في `config.yaml`

## ملاحظات هامة

⚠️ **تنبيهات:**

- هذا النظام يُستخدم لأغراض تعليمية وأمنية فقط
- التدقيق التلقائي لا يغني عن المراجعة اليدوية من قبل خبراء
- لا تتحمل المسؤولية عن أي خسائر ناتجة عن استخدام هذا النظام
- بعض الثغرات قد لا يتم اكتشافها (False Negatives)
- بعض التقارير قد تكون إيجابية كاذبة ويتم استبعادها بعد اختبار PoC

## المساهمة

المساهمات مرحب بها! يرجى فتح Issue أو Pull Request.

## الترخيص

MIT License

---

**تم التطوير بواسطة:** Smart Contract Auditor Team  
**الإصدار:** 1.0.0
