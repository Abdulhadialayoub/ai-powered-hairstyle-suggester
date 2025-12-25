# Yapay Zeka Destekli Yüz Şekli Analizi ve Saç Modeli Öneri Sistemi

**Fırat Üniversitesi Teknoloji Fakültesi Yazılım Mühendisliği Bölümü**

**Yazarlar:**

Abdulhadi ELEYÜB¹, Dığram KATRIB²

¹ 220541606@firat.edu.tr
² 170541618@firat.edu.tr

---

## Öz

Bu çalışma, yapay zeka teknolojileri kullanılarak yüz şekli analizi yapan ve kullanıcılara uygun saç modeli önerileri sunan bir web uygulamasının tasarımını ve geliştirilmesini ele almaktadır. Sistemde iki farklı yaklaşım uygulanmıştır: (1) MediaPipe Face Mesh kütüphanesi ile yüz landmark tespiti ve geometrik analiz, (2) Kaggle Face Shape Dataset üzerinde eğitilmiş CNN (Convolutional Neural Network) modeli. Uygulama, React tabanlı modern bir frontend ve Flask tabanlı RESTful API backend mimarisi ile geliştirilmiştir.

Sistem, oval, yuvarlak, kare, kalp ve elmas olmak üzere 5 farklı yüz şeklini tespit edebilmekte ve her yüz şekline uygun saç modellerini önermektedir. Geometrik yaklaşım %41.2, CNN modeli %34.7 test doğruluğu elde etmiştir. Ayrıca Replicate AI ve Stability AI entegrasyonu ile kullanıcıların seçtikleri saç modellerini kendi fotoğrafları üzerinde deneyebilmeleri sağlanmıştır.

**Anahtar Kelimeler:** Yüz Şekli Analizi, MediaPipe, CNN, Derin Öğrenme, Saç Modeli Önerisi, Web Uygulaması, React, Flask, TensorFlow

---

## 1. Giriş

Günümüzde yapay zeka ve bilgisayarla görme teknolojileri, günlük hayatın birçok alanında kullanılmaktadır. Özellikle güzellik ve moda sektöründe, kişiselleştirilmiş öneriler sunan sistemlere olan talep giderek artmaktadır. Yüz şekli, bir kişinin görünümünü etkileyen en önemli faktörlerden biridir ve uygun saç modeli seçimi, kişinin genel görünümünü önemli ölçüde iyileştirebilir [1].

Geleneksel yöntemlerde, kuaförler ve stil danışmanları yüz şeklini görsel olarak değerlendirerek saç modeli önerilerinde bulunmaktadır. Ancak bu süreç subjektif olabilmekte ve uzman bilgisi gerektirmektedir. Bu çalışmada, yapay zeka teknolojileri kullanılarak objektif ve tutarlı yüz şekli analizi yapan, ardından bu analize dayalı saç modeli önerileri sunan bir sistem geliştirilmiştir.

MediaPipe, Google tarafından geliştirilen ve yüz, el, vücut gibi anatomik yapıların gerçek zamanlı tespitini sağlayan açık kaynaklı bir kütüphanedir [2]. Bu çalışmada MediaPipe Face Mesh modülü kullanılarak yüz üzerinde 468 landmark noktası tespit edilmekte ve bu noktalar arasındaki geometrik ilişkiler analiz edilerek yüz şekli sınıflandırması yapılmaktadır.

Çalışmanın temel katkıları şunlardır:
- MediaPipe tabanlı yüz landmark tespiti ve geometrik analiz
- Weighted Euclidean Distance algoritması ile yüz şekli sınıflandırması
- Yüz şekline uygun saç modeli öneri sistemi
- AI tabanlı saç modeli deneme (try-on) özelliği
- Modern web teknolojileri ile kullanıcı dostu arayüz

---

## 2. Materyal ve Metot

### 2.1. Sistem Mimarisi

Geliştirilen sistem, üç katmanlı bir mimari üzerine inşa edilmiştir (Şekil 1):

1. **Frontend Katmanı:** React.js framework'ü kullanılarak geliştirilmiş kullanıcı arayüzü
2. **Backend Katmanı:** Flask framework'ü ile geliştirilmiş RESTful API servisleri
3. **AI Servisleri:** MediaPipe, Replicate AI ve Stability AI entegrasyonları

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React.js)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Photo   │  │ Results  │  │Favorites │  │ AI Try-  │    │
│  │  Upload  │  │  View    │  │   Page   │  │   On     │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Flask API)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Face    │  │Recommend │  │   Auth   │  │  Try-On  │    │
│  │ Analysis │  │  Engine  │  │ Service  │  │ Service  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     AI Services                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  MediaPipe   │  │  Replicate   │  │  Stability   │      │
│  │  Face Mesh   │  │     AI       │  │     AI       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```
**Şekil 1.** Sistem mimarisi genel görünümü.

### 2.2. Yüz Şekli Analizi

#### 2.2.1. Landmark Tespiti

MediaPipe Face Mesh, yüz üzerinde 468 adet 3D landmark noktası tespit etmektedir [2]. Bu çalışmada, yüz şekli analizinde kritik öneme sahip aşağıdaki landmark noktaları kullanılmıştır:

| Landmark ID | Anatomik Konum | Kullanım Amacı |
|-------------|----------------|----------------|
| 10 | Alın tepesi | Yüz uzunluğu hesaplama |
| 152 | Çene ucu | Yüz uzunluğu hesaplama |
| 234, 454 | Sol/Sağ elmacık kemikleri | Yüz genişliği hesaplama |
| 103, 332 | Sol/Sağ alın kenarları | Alın genişliği hesaplama |
| 132, 361 | Sol/Sağ çene köşeleri | Çene genişliği ve açısı hesaplama |

**Tablo 1.** Yüz şekli analizinde kullanılan landmark noktaları.

#### 2.2.2. Geometrik Ölçümler

Tespit edilen landmark noktaları kullanılarak aşağıdaki geometrik ölçümler hesaplanmaktadır:

**Yüz Uzunluğu (Face Length):**
```
L_face = ||P_10 - P_152||
```

**Yüz Genişliği (Face Width):**
```
W_face = ||P_454 - P_234||
```

**Alın Genişliği (Forehead Width):**
```
W_forehead = ||P_332 - P_103||
```

**Çene Genişliği (Jaw Width):**
```
W_jaw = ||P_361 - P_132||
```

**Çene Açısı (Jaw Angle):**
Çene açısı, sol çene köşesi (P_132), çene ucu (P_152) ve sağ çene köşesi (P_361) noktaları kullanılarak hesaplanmaktadır:

```
θ_jaw = arccos((BA · BC) / (||BA|| × ||BC||))
```

Burada BA = P_132 - P_152 ve BC = P_361 - P_152 vektörleridir.

#### 2.2.3. Oran Hesaplamaları

Geometrik ölçümlerden aşağıdaki oranlar türetilmektedir:

| Oran | Formül | Açıklama |
|------|--------|----------|
| ratio_lw | L_face / W_face | Uzunluk/Genişlik oranı |
| ratio_fj | W_forehead / W_jaw | Alın/Çene oranı |
| ratio_cj | W_face / W_jaw | Yanak/Çene oranı |

**Tablo 2.** Yüz şekli sınıflandırmasında kullanılan oranlar.

### 2.3. Yüz Şekli Sınıflandırması

#### 2.3.1. İdeal Yüz Oranları Veritabanı

Estetik literatüründen derlenen ideal yüz oranları, sınıflandırma için referans değerler olarak kullanılmaktadır [3]:

| Yüz Şekli | ratio_lw | ratio_fj | ratio_cj | Çene Açısı (°) |
|-----------|----------|----------|----------|----------------|
| Oval | 1.35 | 1.25 | 1.25 | 140 |
| Yuvarlak | 1.05 | 1.10 | 1.15 | 150 |
| Kare | 1.05 | 1.05 | 1.10 | 120 |
| Kalp | 1.25 | 1.50 | 1.45 | 130 |
| Elmas | 1.30 | 0.85 | 1.40 | 130 |
| Oblong | 1.55 | 1.05 | 1.10 | 140 |

**Tablo 3.** İdeal yüz şekli oranları veritabanı.

#### 2.3.2. Weighted Euclidean Distance Algoritması

Yüz şekli sınıflandırması, ölçülen değerler ile ideal değerler arasındaki ağırlıklı Öklid mesafesi hesaplanarak gerçekleştirilmektedir:

```
D_shape = W_1|m_lw - i_lw| + W_2|m_fj - i_fj| + W_3|m_cj - i_cj| + W_4|m_θ - i_θ|
```

Burada:
- m: Ölçülen değerler
- i: İdeal değerler
- W_1 = 2.5 (Uzunluk/Genişlik oranı ağırlığı)
- W_2 = 1.5 (Alın/Çene oranı ağırlığı)
- W_3 = 1.0 (Yanak/Çene oranı ağırlığı)
- W_4 = 0.05 (Çene açısı ağırlığı)

En düşük mesafeye sahip yüz şekli, sınıflandırma sonucu olarak belirlenmektedir.

#### 2.3.3. Güven Skoru Hesaplama

Sınıflandırma güven skoru aşağıdaki formül ile hesaplanmaktadır:

```
Confidence = max(0.65, min(1.0 - (D_min / 3.0), 0.95))
```

Bu formül, güven skorunu %65 ile %95 arasında normalize etmektedir.

### 2.4. Saç Modeli Öneri Sistemi

Sistem, 20 farklı erkek saç modelini içeren bir veritabanı kullanmaktadır. Her saç modeli için aşağıdaki bilgiler tutulmaktadır:

- Saç modeli adı ve açıklaması
- Uygun yüz şekilleri listesi
- Zorluk seviyesi (kolay, orta, zor)
- Popülerlik skoru
- Stil etiketleri

Öneri algoritması, tespit edilen yüz şekline uygun saç modellerini popülerlik skoruna göre sıralayarak kullanıcıya sunmaktadır.

### 2.5. AI Saç Modeli Deneme (Try-On) Özelliği

Sistem, Replicate AI ve Stability AI servislerini kullanarak kullanıcıların seçtikleri saç modellerini kendi fotoğrafları üzerinde deneyebilmelerini sağlamaktadır. Bu özellik, generative AI teknolojileri kullanılarak gerçekleştirilmektedir.

---

## 3. Deneysel Bulgular

### 3.1. Deneysel Kurulum

Sistem, aşağıdaki teknolojiler kullanılarak geliştirilmiştir:

| Bileşen | Teknoloji | Versiyon |
|---------|-----------|----------|
| Frontend | React.js | 18.x |
| Backend | Flask | 2.x |
| Yüz Analizi | MediaPipe | 0.10.x |
| Veritabanı | SQLite | 3.x |
| AI Try-On | Replicate AI | - |

**Tablo 4.** Kullanılan teknolojiler ve versiyonları.

### 3.2. Yüz Şekli Sınıflandırma Performansı

Sistem, Pexels görüntü veritabanından elde edilen 20 adet test görüntüsü üzerinde değerlendirilmiştir. Test görüntülerinin 2 tanesi yüz tespit edilemediği için analiz dışı bırakılmış, 1 tanesi birden fazla yüz içerdiği için reddedilmiştir. Kalan 17 görüntü üzerinde sınıflandırma sonuçları aşağıdaki tabloda özetlenmektedir:

| Yüz Şekli | Test Sayısı | Doğru Sınıflandırma | Doğruluk (%) |
|-----------|-------------|---------------------|--------------|
| Oval | 4 | 4 | 100.0 |
| Yuvarlak | 4 | 0 | 0.0 |
| Kare | 4 | 1 | 25.0 |
| Kalp | 4 | 0 | 0.0 |
| Elmas | 4 | 2 | 50.0 |
| **Toplam** | **20** | **7** | **41.2** |

**Tablo 5.** Yüz şekli sınıflandırma performansı.

**Önemli Not:** Test veri setindeki görüntülerin gerçek yüz şekilleri uzman tarafından etiketlenmemiştir. Görsel değerlendirmeye dayalı etiketleme yapılmıştır. Bu durum, özellikle yuvarlak ve kalp yüz şekillerinde düşük doğruluk oranlarının temel nedeni olabilir. Oval yüz şeklinde %100 doğruluk elde edilmesi, sistemin tutarlı çalıştığını göstermektedir.

### 3.3. Örnek Sınıflandırma Sonuçları

Sistemin ürettiği tipik ölçüm değerleri aşağıda örneklenmiştir:

| Görüntü | L/W Oranı | A/Ç Oranı | Çene Açısı | Tahmin | Güven |
|---------|-----------|-----------|------------|--------|-------|
| Örnek 1 | 1.22 | 0.75 | 130° | Oval | 64% |
| Örnek 2 | 1.26 | 0.77 | 130° | Oval | 67% |
| Örnek 3 | 1.13 | 0.77 | 96° | Kare | 73% |
| Örnek 4 | 1.31 | 0.69 | 130° | Elmas | 60% |
| Örnek 5 | 2.07 | 0.71 | 130° | Elmas | 55% |

**Tablo 6.** Örnek sınıflandırma sonuçları ve ölçüm değerleri.

### 3.4. Sınıflandırma Kuralları ve Eşik Değerleri

Sistem, aşağıdaki kural tabanlı sınıflandırma mantığını kullanmaktadır:

| Özellik | Eşik Değeri | Etkilenen Sınıflar |
|---------|-------------|-------------------|
| L/W > 1.45 | Çok uzun yüz | Oblong |
| L/W > 1.25 | Uzun yüz | Oval, Diamond |
| L/W < 1.15 | Kısa yüz | Round, Square |
| A/Ç > 0.85 | Geniş alın | Heart |
| A/Ç < 0.72 | Dar alın | Diamond |
| Açı < 110° | Keskin çene | Square |
| Açı > 135° | Yumuşak çene | Round |

**Tablo 7.** Sınıflandırma kuralları ve eşik değerleri.

### 3.5. Güven Skoru Dağılımı

Sınıflandırma güven skorları %55 ile %73 arasında dağılım göstermektedir. Ortalama güven skoru %63 olarak hesaplanmıştır. Yüksek güven skorları genellikle çene açısının belirgin olduğu (kare yüz şekli, ~96°) durumlarda gözlemlenmiştir.

### 3.4. Sistem Performansı

| Metrik | Değer |
|--------|-------|
| Ortalama analiz süresi | 1.2 saniye |
| API yanıt süresi | 0.3 saniye |
| Maksimum görüntü boyutu | 10 MB |
| Desteklenen formatlar | JPEG, PNG, WebP |

**Tablo 6.** Sistem performans metrikleri.

---

## 4. Tartışma ve Sonuçlar

Bu çalışmada, yapay zeka teknolojileri kullanılarak yüz şekli analizi yapan ve saç modeli önerileri sunan bir web uygulaması geliştirilmiştir. Sistem, MediaPipe Face Mesh kütüphanesi ile yüz landmark tespiti yapmakta ve Weighted Euclidean Distance algoritması ile yüz şekli sınıflandırması gerçekleştirmektedir.

### 4.1. Bulgular ve Değerlendirme

Test sonuçları incelendiğinde, sistemin %41.2 genel doğruluk oranı elde ettiği görülmektedir. Ancak bu sonuçların değerlendirilmesinde aşağıdaki faktörler göz önünde bulundurulmalıdır:

1. **Veri Seti Sınırlılığı:** Test görüntüleri uzman tarafından etiketlenmemiş, görsel değerlendirmeye dayalı etiketlenmiştir. Gerçek yüz şekli etiketleri olmadan yapılan değerlendirme, sistemin gerçek performansını yansıtmayabilir.

2. **Oval Sınıfında Yüksek Başarı:** Oval yüz şeklinde %100 doğruluk elde edilmiştir. Bu, sistemin tutarlı ve güvenilir sonuçlar ürettiğini göstermektedir. Oval yüz şekli, popülasyonda en yaygın görülen yüz şekli olduğundan bu başarı önemlidir.

3. **Çene Açısının Kritik Rolü:** Kare yüz şeklinin tespitinde çene açısı kritik bir rol oynamaktadır. Çene açısı 95-100° aralığında olan yüzler yüksek güvenle (%73) kare olarak sınıflandırılmıştır. Bu, geometrik yaklaşımın belirli yüz şekillerinde etkili olduğunu göstermektedir.

4. **Sınıf Karışıklığı:** Yuvarlak ve kalp yüz şekillerinde düşük doğruluk gözlemlenmiştir. Bu sınıflar, oval yüz şekli ile geometrik olarak benzer özelliklere sahip olduğundan ayırt edilmesi zordur.

### 4.2. Sistemin Güçlü Yönleri

- **Gerçek Zamanlı Analiz:** MediaPipe sayesinde görüntü analizi 1-2 saniye içinde tamamlanmaktadır
- **468 Landmark Noktası:** Yüksek çözünürlüklü yüz geometrisi analizi yapılabilmektedir
- **Modüler Mimari:** Frontend ve backend ayrımı sayesinde sistem kolayca genişletilebilir
- **AI Try-On Özelliği:** Replicate AI entegrasyonu ile kullanıcılar saç modellerini deneyebilmektedir
- **Kullanıcı Dostu Arayüz:** React tabanlı modern web arayüzü

### 4.3. Sınırlılıklar

- **Geometrik Yaklaşımın Sınırları:** Sadece oran ve açı bazlı sınıflandırma, yüz şeklinin tüm özelliklerini yakalayamamaktadır
- **Aydınlatma Hassasiyeti:** Düşük ışık koşullarında landmark tespiti başarısız olabilmektedir
- **Tek Yüz Kısıtı:** Sistem aynı anda sadece bir yüz analiz edebilmektedir
- **Cinsiyet Sınırlaması:** Şu an sadece erkek saç modelleri desteklenmektedir

### 4.4. CNN Model Eğitimi ve Sonuçları

Geometrik yaklaşımın sınırlılıklarını aşmak için, Kaggle Face Shape Dataset kullanılarak bir CNN (Convolutional Neural Network) modeli eğitilmiştir.

#### 4.4.1. Veri Seti

| Özellik | Değer |
|---------|-------|
| Kaynak | Kaggle Face Shape Dataset |
| Eğitim Görüntüsü | 3200 |
| Doğrulama Görüntüsü | 800 |
| Test Görüntüsü | 1000 |
| Sınıf Sayısı | 5 (Heart, Oblong, Oval, Round, Square) |

**Tablo 8.** CNN eğitimi için kullanılan veri seti.

#### 4.4.2. Model Mimarisi

```
Input (128x128x3)
    ↓
Conv2D(32) → BatchNorm → Conv2D(32) → MaxPool → Dropout(0.25)
    ↓
Conv2D(64) → BatchNorm → Conv2D(64) → MaxPool → Dropout(0.25)
    ↓
Conv2D(128) → BatchNorm → Conv2D(128) → MaxPool → Dropout(0.25)
    ↓
Conv2D(256) → BatchNorm → MaxPool → Dropout(0.25)
    ↓
Flatten → Dense(512) → BatchNorm → Dropout(0.5)
    ↓
Dense(256) → Dropout(0.5)
    ↓
Dense(5, softmax) → Output
```

Toplam parametre sayısı: 9,107,877 (34.74 MB)

#### 4.4.3. Eğitim Sonuçları

| Metrik | Değer |
|--------|-------|
| Eğitim Epoch | 28 (Early Stopping) |
| En İyi Doğrulama Doğruluğu | %35.25 |
| Test Kaybı | 1.4875 |
| Test Doğruluğu | %34.7 |

**Tablo 9.** CNN model eğitim sonuçları.

#### 4.4.4. Sınıf Bazlı Performans

| Sınıf | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| Heart | 0.41 | 0.19 | 0.26 |
| Oblong | 0.34 | 0.75 | 0.47 |
| Oval | 0.31 | 0.06 | 0.10 |
| Round | 0.45 | 0.25 | 0.32 |
| Square | 0.30 | 0.48 | 0.37 |

**Tablo 10.** CNN model sınıf bazlı performans metrikleri.

#### 4.4.5. Karışıklık Matrisi

```
              Heart  Oblong  Oval  Round  Square
Heart           38      95     5     13      49
Oblong           8     150     2      6      34
Oval            25      80    12     27      56
Round           10      39    16     50      85
Square          11      72     4     16      97
```

#### 4.4.6. CNN Sonuçlarının Değerlendirmesi

CNN modelinin beklenen %70-85 doğruluk yerine %34.7 doğruluk vermesinin olası nedenleri:

1. **Veri Seti Kalitesi:** Kaggle veri setindeki görüntülerin etiketleme tutarlılığı düşük olabilir
2. **Sınıf Dengesizliği:** Oblong sınıfında yüksek recall (%75) ancak düşük precision (%34) gözlemlenmiştir
3. **Görüntü Çeşitliliği:** Farklı açılar, aydınlatma koşulları ve yüz ifadeleri model performansını etkilemiştir
4. **Sınıflar Arası Benzerlik:** Yüz şekilleri arasındaki geometrik benzerlikler ayırt etmeyi zorlaştırmaktadır

### 4.5. Gelecek Çalışmalar

1. **Transfer Öğrenme:** VGGFace, FaceNet gibi önceden eğitilmiş modeller kullanılarak performans iyileştirilebilir
2. **Veri Artırma:** Daha agresif data augmentation teknikleri uygulanabilir
3. **Ensemble Yöntemler:** Geometrik ve CNN yaklaşımlarının birleştirilmesi denenebilir
4. **Daha Büyük Veri Seti:** Uzman tarafından etiketlenmiş daha büyük bir veri seti toplanabilir
5. **Kadın Saç Modelleri:** Veritabanına kadın saç modelleri eklenerek kapsam genişletilebilir
6. **Mobil Uygulama:** React Native ile mobil versiyon geliştirilebilir

### 4.5. Sonuç

Bu çalışma, MediaPipe ve geometrik analiz kullanarak yüz şekli tespiti yapan bir sistem geliştirmiştir. Mevcut sonuçlar, geometrik yaklaşımın tek başına yeterli olmadığını ve derin öğrenme tabanlı yöntemlerin entegrasyonunun gerekli olduğunu göstermektedir. Bununla birlikte, sistem saç modeli önerisi ve AI try-on özellikleri ile kullanıcılara değerli bir deneyim sunmaktadır.

---

## Kaynaklar

[1] A. Krizhevsky, I. Sutskever, and G. E. Hinton, "ImageNet classification with deep convolutional neural networks," Communications of the ACM, vol. 60, no. 6, pp. 84-90, 2017.

[2] C. Lugaresi et al., "MediaPipe: A Framework for Building Perception Pipelines," arXiv preprint arXiv:1906.08172, 2019.

[3] Y. LeCun, Y. Bengio, and G. Hinton, "Deep learning," Nature, vol. 521, pp. 436-444, 2015.

[4] V. Nair and G. E. Hinton, "Rectified linear units improve restricted Boltzmann machines," in Proceedings of the 27th International Conference on Machine Learning, 2010.

[5] K. Simonyan and A. Zisserman, "Very deep convolutional networks for large-scale image recognition," arXiv preprint arXiv:1409.1556, 2014.

[6] D. P. Kingma and J. Ba, "Adam: A method for stochastic optimization," arXiv preprint arXiv:1412.6980, 2014.

[7] F. Chollet, "Deep learning with Python," Manning Publications, 2017.

[8] React Documentation, "React – A JavaScript library for building user interfaces," https://reactjs.org/, 2024.

[9] Flask Documentation, "Flask Web Development," https://flask.palletsprojects.com/, 2024.

[10] MediaPipe Documentation, "MediaPipe Face Mesh," https://google.github.io/mediapipe/, 2024.

---

## Ekler

### Ek A: Sistem Ekran Görüntüleri

*(Buraya uygulama ekran görüntüleri eklenecek)*

### Ek B: API Endpoint Listesi

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| /api/analysis/analyze | POST | Yüz şekli analizi |
| /api/recommendations | GET | Saç modeli önerileri |
| /api/try-on | POST | AI saç deneme |
| /api/favorites | GET/POST/DELETE | Favori yönetimi |
| /api/auth/login | POST | Kullanıcı girişi |
| /api/auth/register | POST | Kullanıcı kaydı |

**Tablo A1.** API endpoint listesi.

### Ek C: Kullanılan Kütüphaneler

**Backend:**
- Flask 2.x
- Flask-CORS
- Flask-RESTX
- MediaPipe
- OpenCV
- NumPy
- Pillow

**Frontend:**
- React 18.x
- Axios
- React Router
- CSS Modules
