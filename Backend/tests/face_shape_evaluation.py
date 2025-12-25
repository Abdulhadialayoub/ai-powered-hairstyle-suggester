"""
Yüz Şekli Sınıflandırma Değerlendirme Scripti

Bu script, farklı yüz şekillerine sahip test görüntüleri üzerinde
sistemin performansını değerlendirir ve rapor için metrikler üretir.
"""

import os
import sys
import json
import requests
from io import BytesIO
from datetime import datetime

# Backend servislerini import et
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.face_analysis import FaceAnalyzer, NoFaceDetectedError

# Test veri seti - Pexels'tan seçilmiş portre fotoğrafları
# Not: Bu fotoğrafların yüz şekilleri görsel olarak değerlendirilmiştir
# Daha doğru sonuçlar için uzman etiketlemesi gereklidir
TEST_DATASET = {
    'oval': [
        # Oval: Yüz uzunluğu genişliğinden fazla, yumuşak hatlar
        {'name': 'Oval Portrait 1', 'url': 'https://images.pexels.com/photos/2379005/pexels-photo-2379005.jpeg?w=400'},
        {'name': 'Oval Portrait 2', 'url': 'https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?w=400'},
        {'name': 'Oval Portrait 3', 'url': 'https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?w=400'},
        {'name': 'Oval Portrait 4', 'url': 'https://images.pexels.com/photos/1043474/pexels-photo-1043474.jpeg?w=400'},
    ],
    'round': [
        # Round: Genişlik ve uzunluk yaklaşık eşit, yumuşak çene
        {'name': 'Round Portrait 1', 'url': 'https://images.pexels.com/photos/1681010/pexels-photo-1681010.jpeg?w=400'},
        {'name': 'Round Portrait 2', 'url': 'https://images.pexels.com/photos/1300402/pexels-photo-1300402.jpeg?w=400'},
        {'name': 'Round Portrait 3', 'url': 'https://images.pexels.com/photos/834863/pexels-photo-834863.jpeg?w=400'},
        {'name': 'Round Portrait 4', 'url': 'https://images.pexels.com/photos/1040881/pexels-photo-1040881.jpeg?w=400'},
    ],
    'square': [
        # Square: Geniş alın, belirgin çene hattı, keskin açılar
        {'name': 'Square Portrait 1', 'url': 'https://images.pexels.com/photos/2531553/pexels-photo-2531553.jpeg?w=400'},
        {'name': 'Square Portrait 2', 'url': 'https://images.pexels.com/photos/697509/pexels-photo-697509.jpeg?w=400'},
        {'name': 'Square Portrait 3', 'url': 'https://images.pexels.com/photos/842980/pexels-photo-842980.jpeg?w=400'},
        {'name': 'Square Portrait 4', 'url': 'https://images.pexels.com/photos/1139743/pexels-photo-1139743.jpeg?w=400'},
    ],
    'heart': [
        # Heart: Geniş alın, dar çene, sivri çene ucu
        {'name': 'Heart Portrait 1', 'url': 'https://images.pexels.com/photos/1516680/pexels-photo-1516680.jpeg?w=400'},
        {'name': 'Heart Portrait 2', 'url': 'https://images.pexels.com/photos/1212984/pexels-photo-1212984.jpeg?w=400'},
        {'name': 'Heart Portrait 3', 'url': 'https://images.pexels.com/photos/1080213/pexels-photo-1080213.jpeg?w=400'},
        {'name': 'Heart Portrait 4', 'url': 'https://images.pexels.com/photos/2887718/pexels-photo-2887718.jpeg?w=400'},
    ],
    'diamond': [
        # Diamond: Dar alın, geniş elmacık kemikleri, dar çene
        {'name': 'Diamond Portrait 1', 'url': 'https://images.pexels.com/photos/1687675/pexels-photo-1687675.jpeg?w=400'},
        {'name': 'Diamond Portrait 2', 'url': 'https://images.pexels.com/photos/1542085/pexels-photo-1542085.jpeg?w=400'},
        {'name': 'Diamond Portrait 3', 'url': 'https://images.pexels.com/photos/2406949/pexels-photo-2406949.jpeg?w=400'},
        {'name': 'Diamond Portrait 4', 'url': 'https://images.pexels.com/photos/1182825/pexels-photo-1182825.jpeg?w=400'},
    ]
}


def download_image(url):
    """URL'den görüntü indir"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"  ❌ İndirme hatası: {e}")
        return None


def run_evaluation():
    """Değerlendirme testlerini çalıştır"""
    print("=" * 60)
    print("YÜZ ŞEKLİ SINIFLANDIRMA DEĞERLENDİRMESİ")
    print("=" * 60)
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    analyzer = FaceAnalyzer()
    
    results = {
        'total': 0,
        'correct': 0,
        'failed': 0,
        'no_face': 0,
        'by_shape': {},
        'confusion_matrix': {},
        'details': []
    }
    
    # Her yüz şekli için confusion matrix başlat
    shapes = list(TEST_DATASET.keys())
    for shape in shapes:
        results['by_shape'][shape] = {'total': 0, 'correct': 0}
        results['confusion_matrix'][shape] = {s: 0 for s in shapes}
    
    # Test et
    for expected_shape, test_cases in TEST_DATASET.items():
        print(f"\n📊 {expected_shape.upper()} Yüz Şekli Testleri:")
        print("-" * 40)
        
        for test in test_cases:
            results['total'] += 1
            results['by_shape'][expected_shape]['total'] += 1
            
            print(f"  Testing: {test['name']}...", end=" ")
            
            # Görüntüyü indir
            image_data = download_image(test['url'])
            if not image_data:
                results['failed'] += 1
                print("❌ İndirilemedi")
                continue
            
            # Analiz et
            try:
                result = analyzer.analyze_face_shape(image_data)
                predicted = result['face_shape']
                confidence = result['confidence']
                
                # Sonucu kaydet
                is_correct = predicted == expected_shape
                
                if is_correct:
                    results['correct'] += 1
                    results['by_shape'][expected_shape]['correct'] += 1
                    print(f"✅ {predicted} ({confidence:.0%})")
                else:
                    print(f"❌ {predicted} ({confidence:.0%}) - Beklenen: {expected_shape}")
                
                # Confusion matrix güncelle
                if predicted in results['confusion_matrix'][expected_shape]:
                    results['confusion_matrix'][expected_shape][predicted] += 1
                
                # Detay kaydet
                results['details'].append({
                    'name': test['name'],
                    'expected': expected_shape,
                    'predicted': predicted,
                    'confidence': confidence,
                    'correct': is_correct,
                    'measurements': result.get('measurements', {})
                })
                
            except NoFaceDetectedError:
                results['no_face'] += 1
                print("⚠️ Yüz tespit edilemedi")
            except Exception as e:
                results['failed'] += 1
                print(f"❌ Hata: {e}")
    
    # Sonuçları hesapla ve yazdır
    print_results(results, shapes)
    
    # JSON olarak kaydet
    save_results(results)
    
    return results


def print_results(results, shapes):
    """Sonuçları yazdır"""
    print("\n" + "=" * 60)
    print("SONUÇLAR")
    print("=" * 60)
    
    # Genel metrikler
    valid_tests = results['total'] - results['failed'] - results['no_face']
    accuracy = results['correct'] / valid_tests * 100 if valid_tests > 0 else 0
    
    print(f"\n📈 Genel Metrikler:")
    print(f"   Toplam Test: {results['total']}")
    print(f"   Başarılı Analiz: {valid_tests}")
    print(f"   Doğru Sınıflandırma: {results['correct']}")
    print(f"   Yüz Tespit Edilemedi: {results['no_face']}")
    print(f"   Başarısız: {results['failed']}")
    print(f"   Genel Doğruluk: {accuracy:.1f}%")
    
    # Sınıf bazlı metrikler
    print(f"\n📊 Sınıf Bazlı Performans:")
    print("-" * 50)
    print(f"{'Yüz Şekli':<12} {'Toplam':<8} {'Doğru':<8} {'Doğruluk':<10}")
    print("-" * 50)
    
    for shape in shapes:
        data = results['by_shape'][shape]
        shape_acc = data['correct'] / data['total'] * 100 if data['total'] > 0 else 0
        print(f"{shape:<12} {data['total']:<8} {data['correct']:<8} {shape_acc:.1f}%")
    
    # Confusion Matrix
    print(f"\n📋 Karışıklık Matrisi (Confusion Matrix):")
    print("-" * 60)
    
    # Header
    header = "Gerçek\\Tahmin"
    for s in shapes:
        header += f" {s[:6]:>6}"
    print(header)
    print("-" * 60)
    
    # Rows
    for actual in shapes:
        row = f"{actual:<13}"
        for predicted in shapes:
            count = results['confusion_matrix'][actual].get(predicted, 0)
            row += f" {count:>6}"
        print(row)


def save_results(results):
    """Sonuçları JSON dosyasına kaydet"""
    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'evaluation_results.json')
    
    # Datetime'ı string'e çevir
    results['timestamp'] = datetime.now().isoformat()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Sonuçlar kaydedildi: {output_path}")


def calculate_metrics(results):
    """Precision, Recall, F1-Score hesapla"""
    shapes = list(results['by_shape'].keys())
    metrics = {}
    
    for shape in shapes:
        # True Positives
        tp = results['confusion_matrix'][shape].get(shape, 0)
        
        # False Positives (diğer sınıflardan bu sınıfa yanlış tahmin)
        fp = sum(results['confusion_matrix'][other].get(shape, 0) 
                 for other in shapes if other != shape)
        
        # False Negatives (bu sınıftan diğer sınıflara yanlış tahmin)
        fn = sum(results['confusion_matrix'][shape].get(other, 0) 
                 for other in shapes if other != shape)
        
        # Precision
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        
        # Recall
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        # F1-Score
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics[shape] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'tp': tp,
            'fp': fp,
            'fn': fn
        }
    
    return metrics


if __name__ == '__main__':
    results = run_evaluation()
    
    # Detaylı metrikler
    print("\n" + "=" * 60)
    print("DETAYLI METRİKLER (Precision, Recall, F1-Score)")
    print("=" * 60)
    
    metrics = calculate_metrics(results)
    
    print(f"\n{'Sınıf':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 50)
    
    for shape, m in metrics.items():
        print(f"{shape:<12} {m['precision']:.2f}         {m['recall']:.2f}         {m['f1_score']:.2f}")
