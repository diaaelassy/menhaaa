# Smart Contract Auditor Agent

نظام متكامل لتدقيق العقود الذكية (Smart Contract Auditor Agent) يستخدم أدوات حقيقية للتحليل واكتشاف الثغرات وتأكيدها عملياً.

## المميزات

- ✅ **قراءة عقود Solidity** من ملفات
- ✅ **تحليل ثابت** باستخدام Slither
- ✅ **تحليل ذكي** باستخدام DeepSeek AI
- ✅ **اكتشاف ثغرات حقيقية**: Reentrancy, Overflow, Front-running, Business Logic Errors
- ✅ **اختبار عملي** عبر Fuzzing بـ Echidna
- ✅ **توليد PoC تلقائي** باستخدام Foundry
- ✅ **تأكيد الثغرات** بتشغيل الكود فعلياً
- ✅ **تقرير نهائي** بالثغرات المؤكدة فقط

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

### الأمر الأساسي

```bash
python main.py --contract-path /path/to/contract.sol --api-key sk-xxxxx
```

### الخيارات المتاحة

| الخيار | الوصف | مطلوب |
|--------|-------|--------|
| `--contract-path` | مسار ملف العقد الذكي (Solidity) | ✅ نعم |
| `--api-key` | مفتاح DeepSeek API | ✅ نعم |
| `--config` | مسار ملف الإعدادات | ❌ لا (default: config.yaml) |
| `--deepseek-model` | اسم نموذج DeepSeek | ❌ لا (default: deepseek-chat) |
| `--output` | مسار حفظ التقرير (JSON) | ❌ لا |
| `--verbose` | تفعيل الإخراج المفصل | ❌ لا |

### أمثلة

```bash
# تدقيق عقد بسيط
python main.py --contract-path ./MyToken.sol --api-key sk-abc123

# تدقيق مع حفظ التقرير
python main.py --contract-path ./DeFiProtocol.sol --api-key sk-abc123 --output audit_report.json

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
