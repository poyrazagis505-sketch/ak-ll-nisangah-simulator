# Akıllı Mühimmat Takip ve Gösterge Sistemi (Sandbox)

Bu proje, gerçek bir Raspberry Pi / mikrodenetleyici ve NFC tabanlı şarjör tanıma mantığını simüle eden güvenli bir laboratuvar prototipidir.

## Özellikler

- Şarjör ekleme / kaldırma
- NFC kimlik takibi
- Kalan fişek sayısı takibi
- Atış ve boş şarjör olayları
- Belirsiz olay kaydı
- Streamlit arayüzü
- JSON tabanlı kalıcı veri saklama

## Kurulum

```bash
pip install -r requirements.txt
``` 

## Çalıştırma

```bash
streamlit run app.py
```

## Dosya yapısı

- `app.py` : Streamlit arayüzü
- `magazine_manager.py` : Şarjör yönetimi ve veri saklama
- `data/magazines.json` : Kalıcı kayıtlar
- `requirements.txt` : Gerekli kütüphaneler

## Kullanım

1. Uygulamayı başlatın.
2. Sol menüden şarjör ekleyin.
3. Şarjörün NFC ID'sini girin.
4. Ateş simülasyonu yapın.
5. Olay geçmişini inceleyin.

Bu uygulama gerçek donanım yerine laboratuvar testi için tasarlanmıştır.
