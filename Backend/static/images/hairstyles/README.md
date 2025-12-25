# Saç Modeli Fotoğrafları

Bu klasöre 25 saç modeli fotoğrafı eklemeniz gerekiyor.

## 🚀 Hızlı Başlangıç

### Seçenek 1: Placeholder Kullan (Test İçin)
```bash
cd backend
python use_placeholder_images.py
```
Bu, tüm fotoğrafları placeholder URL'lere çevirir ve hemen test edebilirsiniz.

### Seçenek 2: Gerçek Fotoğraflar Ekle

1. **Fotoğrafları İndir:**
   - Unsplash: https://unsplash.com/s/photos/hairstyle
   - Pexels: https://www.pexels.com/search/hairstyle/
   - Pixabay: https://pixabay.com/images/search/hairstyle/

2. **Dosya İsimlerini Kontrol Et:**
   `REQUIRED_IMAGES.txt` dosyasında tam liste var.

3. **Fotoğrafları Bu Klasöre Kopyala:**
   ```
   backend/static/images/hairstyles/
   ├── long-layers.jpg
   ├── textured-bob.jpg
   ├── side-swept-bangs.jpg
   └── ... (22 tane daha)
   ```

4. **JSON'ı Güncelle:**
   ```bash
   cd backend
   python restore_local_images.py
   ```

## 📋 Gerekli Dosyalar

Toplam 25 fotoğraf:

1. long-layers.jpg
2. textured-bob.jpg
3. side-swept-bangs.jpg
4. pixie-cut.jpg
5. beach-waves.jpg
6. blunt-lob.jpg
7. voluminous-curls.jpg
8. high-ponytail.jpg
9. shaggy-layers.jpg
10. asymmetrical-bob.jpg
11. soft-updo.jpg
12. curtain-bangs.jpg
13. sleek-straight.jpg
14. messy-bun.jpg
15. feathered-layers.jpg
16. braided-crown.jpg
17. undercut-volume.jpg
18. low-chignon.jpg
19. wispy-bangs.jpg
20. half-up-half-down.jpg
21. graduated-bob.jpg
22. loose-waves.jpg
23. buzz-cut.jpg
24. side-part-volume.jpg
25. fishtail-braid.jpg

## 📐 Fotoğraf Özellikleri

- **Format**: JPG veya PNG
- **Boyut**: Minimum 500x500px (ideal: 800x800px)
- **Oran**: Kare (1:1) önerilir
- **Kalite**: Yüksek çözünürlük
- **İçerik**: Net, iyi ışıklandırılmış saç modeli

## 🎨 AI ile Fotoğraf Üretme

Eğer fotoğraf bulamıyorsan, AI ile üretebilirsin:

**DALL-E / Midjourney / Stable Diffusion Prompt:**
```
Professional hairstyle photo, [hairstyle name], studio lighting, 
clean background, high quality, fashion photography style
```

Örnek:
```
Professional hairstyle photo, long layered hair, studio lighting, 
clean background, high quality, fashion photography style
```

## ⚠️ Lisans

Ticari kullanım için lisans kontrolü yap:
- ✅ Unsplash: Ücretsiz ticari kullanım
- ✅ Pexels: Ücretsiz ticari kullanım  
- ✅ Pixabay: Ücretsiz ticari kullanım

## 🔍 Kontrol

Fotoğrafları ekledikten sonra kontrol et:
```bash
cd backend
python restore_local_images.py
```

Eksik dosyaları gösterecek.
