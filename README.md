# IT o‘quv markaz boshqaruv tizimi

Bu Django loyiha o‘quv markaz uchun: bosh admin, o‘qituvchi, yordamchi o‘qituvchi va o‘quvchi rollari bilan ishlaydi.

## Imkoniyatlar

- Bosh admin barcha foydalanuvchilarni yaratadi va tahrirlaydi.
- Admin kurs, guruh, o‘qituvchi, yordamchi o‘qituvchi va o‘quvchilarni bog‘laydi.
- O‘qituvchi va yordamchi o‘qituvchi guruhga uyga vazifa yoki imtihon beradi.
- Vazifa va javoblarda pdf, video, audio, rasm, arxiv va kod fayllari yuklanadi.
- Vazifa va imtihonga kun, soat, minutgacha deadline beriladi.
- O‘quvchi vazifani ko‘radi, faylni yuklab oladi va javob yuboradi.
- O‘qituvchi topshirilgan ishni baholaydi va izoh yozadi.
- Admin xodimlarga oylik chiqaradi.
- Har bir foydalanuvchida shaxsiy profil, telefon, passport raqami, manzil va rasm bor.
- Bosh sahifada reklama, markaz haqida ma’lumot, ustozlar, eng yaxshi talabalar va ariza formasi bor.
- Face ID demo: profilga rasm yuklangan foydalanuvchi kamera orqali kirishni sinab ko‘ra oladi.
- Admin foydalanuvchilarning oxirgi faolligi, online/offline holati va parol yoki Face ID orqali kirganini ko‘radi.

## App tuzilmasi

- `accounts` - admin, o‘qituvchi, yordamchi o‘qituvchi, student va profil ma’lumotlari.
- `courses` - kurslar, guruhlar, o‘qituvchi va o‘quvchini guruhga biriktirish.
- `assignments` - uyga vazifa, imtihon, fayl yuklash, student javobi va baholash.
- `finance` - oylik chiqarish va to‘lov holati.
- `admissions` - yangi o‘quvchi arizalari.
- `pages` - homepage, dashboard va umumiy sahifalar.
- `edu_center` - Django project sozlamalari.

## Ishga tushirish

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Brauzerda ochish:

```text
http://127.0.0.1:8000/
```

## Face ID ishlatish

1. Admin orqali foydalanuvchi yarating yoki profilga rasm yuklang.
2. Login sahifasida `Face ID bilan kirish` ni bosing.
3. Username yozing, kamerani yoqing va tekshiring.

Eslatma: Face ID xavfsiz ishlashi uchun `face_recognition` kutubxonasi kerak. Kutubxona o‘rnatilmagan bo‘lsa, tizim Face ID orqali kirishga ruxsat bermaydi, chunki oddiy rasm o‘xshashligini tekshirish xavfsiz emas.

## Faollik nazorati

- `LoginActivity` jadvali har bir kirishni saqlaydi.
- `method=password` bo‘lsa, foydalanuvchi parol bilan kirgan.
- `method=face_id` bo‘lsa, foydalanuvchi kamera orqali kirgan.
- `last_seen` foydalanuvchi oxirgi marta sayt ichida faol bo‘lgan vaqtni saqlaydi.
- 5 daqiqa ichida faol bo‘lgan foydalanuvchi dashboard va admin panelda `Online` ko‘rinadi.

## Jamoada bo‘lib olish

1. Sardor / menejer: GitHub repo, vazifalarni bo‘lish, pull request tekshirish, README va yakuniy himoya.
2. Backendchi: `accounts`, `courses`, `assignments`, `finance`, `admissions` app modellari va ruxsatlari.
3. Frontendchi: `pages/templates/academy/` va `static/academy/styles.css`, sahifalarni chiroyli va qulay qilish.

## Keyingi qo‘shimcha g‘oyalar

- Davomat jurnali.
- To‘lovlar va qarzdorlik.
- Guruh jadvali va xona bandligi.
- Telegram bildirishnoma.
- Sertifikat chiqarish.
- Excel hisobot eksporti.
