# YALDA Motion Skills — نسخهٔ عمومی ۰٫۵٫۰

این مخزن شامل **دو Agent Skill مستقل** است: `yalda-motion-designer` برای طراحی سناریوهای سینمایی مبتنی بر اسکرول و `yalda-motion-auditor` برای ممیزی مستقل و **فقط‌خواندنی** حرکت، تصاویر و کارایی مرورگر.

ساختار هر پوشه مطابق استاندارد [Agent Skills](https://agentskills.io/specification) است: فایل الزامی `SKILL.md` و پوشه‌های اختیاری `scripts/`، `references/`، `assets/` و `agents/`.

## وب‌سایت رسمی پروژه

**YALDA Motion Skills**

وب‌سایت رسمی مهندسی یلدا:
https://www.yaldaeng.ir

مخزن رسمی سورس:
https://github.com/Mostafaair/yalda-motion-skills

YALDA Motion Skills شامل دو ابزار مستقل
Designer و Auditor برای طراحی و ارزیابی
انیمیشن‌های اسکرولی وب است.

## روش نصب

پوشهٔ یکی از دو Skill را با همان نام و تمام زیرپوشه‌ها در مسیر Skills مورد پشتیبانی عامل خود کپی کنید. برای استفادهٔ مستقل از Designer و Auditor باید هر دو پوشه نصب شوند. راهنمای محصول Agent را برای مسیر نصب بررسی کنید. **صرف آپلود ZIP به معنی خوانده‌شدن یا اجرای Skill نیست.**

## مهم‌ترین ویژگی‌ها

- حفظ تصاویر اصلی و انتخاب پروفایل `IMAGE-FIRST-HYBRID` یا 3D-source با مجوز صریح.
- YALDA Visual Timeline v1 با Keyframe، مختصات مستقل و کنترل پیشرفت محلی هر فصل.
- ریل مشترک برای حرکت هم‌زمان پنجره‌های SAFE و YALDA.
- تحویل پیوستهٔ کپشن، کنترل برخورد و خوانایی واقعی.
- اینرسی محدود، اسکرول برگشتی و `prefers-reduced-motion`.
- کنترل بودجهٔ رسانه و ذخیرهٔ مرحله‌ای قابل راستی‌آزمایی.
- ممیزی مستقل شواهد مرورگر، HAR، Trace، Alt و ادعاهای علمی.

## استفاده و آزمون

```bash
python skills/yalda-motion-auditor/scripts/validate_visual_timeline.py --help
python skills/yalda-motion-auditor/scripts/audit_caption_coverage.py --help
python -m unittest discover -s tests -q
```

نمونه‌های داخل `assets` مصنوعی یا تأییدنشده‌اند و هیچ‌یک از نتایج آن‌ها شاهد عملکرد واقعی سایت محسوب نمی‌شوند. این Skill محاسبات SSI یا انتقال عملیاتی به CSI SAFE انجام نمی‌دهد.

**وضعیت مجوز:** هنوز مجوز استفاده و بازتوزیع عمومی از سوی مالک انتخاب نشده است. قبل از معرفی مخزن به‌عنوان «متن‌باز»، `LICENSE` مناسب اضافه شود و منشأ همهٔ کدها و مثال‌ها بررسی گردد. ابزارهای YALDA بدون GO صریح مالک حق تغییر سورس یا Deploy نمی‌دهند.

[مقالهٔ معرفی فنی](docs/article-fa.md) · [خروجی HTML مقاله](docs/article-fa.html) · [گزارش پاکسازی](docs/PUBLIC_RELEASE_AUDIT_FA.md)
