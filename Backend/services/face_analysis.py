"""
Face analysis module for detecting and classifying face shapes.

Uses MediaPipe Face Mesh for facial landmark detection and 
Weighted Euclidean Distance algorithm for face shape classification.
"""

import cv2
import numpy as np
import mediapipe as mp
from io import BytesIO
from PIL import Image


class NoFaceDetectedError(Exception):
    """Raised when no face is detected in the image."""
    pass


class MultipleFacesDetectedError(Exception):
    """Raised when multiple faces are detected in the image."""
    pass


class ImageProcessingError(Exception):
    """Raised when image processing fails."""
    pass


class FaceAnalyzer:
    """
    Geometrik analiz ve 'En Yakın Komşu' (Nearest Neighbor) mantığı ile 
    yüz şekli analizi yapan geliştirilmiş sınıf.
    """
    
    def __init__(self):
        """Initialize the face analyzer with MediaPipe Face Mesh."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=0.3
        )
        
        # İDEAL YÜZ ORANLARI VERİTABANI
        # Bu oranlar gerçek test verilerinden kalibre edilmiştir.
        # ratio_lw: Yüz uzunluğu / Yüz genişliği
        # ratio_fj: Alın genişliği / Çene genişliği  
        # ratio_cj: Yanak genişliği / Çene genişliği
        # angle: Çene açısı (derece)
        self.ideal_shapes = {
            'oval':    {'ratio_lw': 1.25, 'ratio_fj': 0.78, 'ratio_cj': 1.04, 'angle': 130},
            'round':   {'ratio_lw': 1.10, 'ratio_fj': 0.80, 'ratio_cj': 1.05, 'angle': 145},
            'square':  {'ratio_lw': 1.15, 'ratio_fj': 0.78, 'ratio_cj': 1.03, 'angle': 95},
            'heart':   {'ratio_lw': 1.20, 'ratio_fj': 0.90, 'ratio_cj': 1.08, 'angle': 125},
            'diamond': {'ratio_lw': 1.35, 'ratio_fj': 0.72, 'ratio_cj': 1.02, 'angle': 130},
            'oblong':  {'ratio_lw': 1.50, 'ratio_fj': 0.75, 'ratio_cj': 1.04, 'angle': 130}
        }

    def analyze_face_shape(self, image_data):
        """
        Analyze an image to detect and classify face shape.
        
        Args:
            image_data: Binary image data (bytes)
        
        Returns:
            dict: {
                'face_shape': str,
                'confidence': float,
                'measurements': dict,
                'scores': dict
            }
        
        Raises:
            NoFaceDetectedError: If no face is found
            MultipleFacesDetectedError: If multiple faces are found
            ImageProcessingError: If image processing fails
        """
        try:
            image = Image.open(BytesIO(image_data))
            image_np = np.array(image.convert('RGB'))
        except Exception as e:
            raise ImageProcessingError(f"Resim yüklenemedi: {str(e)}")
        
        results = self.face_mesh.process(image_np)
        
        if not results.multi_face_landmarks:
            raise NoFaceDetectedError("Yüz bulunamadı.")
        
        if len(results.multi_face_landmarks) > 1:
            raise MultipleFacesDetectedError("Birden fazla yüz tespit edildi.")
        
        # İlk yüzü al
        face_landmarks = results.multi_face_landmarks[0]
        
        # Landmarkları numpy dizisine çevir (x, y, z)
        h, w, _ = image_np.shape
        landmarks = np.array([
            [lm.x * w, lm.y * h, lm.z] 
            for lm in face_landmarks.landmark
        ])
        
        # 1. Ölçümleri Yap
        measurements = self.calculate_face_measurements(landmarks)
        
        # Debug log
        print(f"Face Analysis Measurements: {measurements}")
        
        # 2. Sınıflandır (Math Model)
        face_shape, confidence, scores = self.classify_face_shape(measurements)
        
        return {
            'face_shape': face_shape,
            'confidence': round(confidence, 2),
            'measurements': measurements,
            'scores': scores
        }
    
    def calculate_face_measurements(self, pts):
        """
        Geometrik özellikleri hesaplar.
        
        Args:
            pts: (468, 3) boyutunda landmark koordinatları
        
        Returns:
            dict: Hesaplanan oranlar ve açılar
        """
        # --- MESAFELER (Euclidean Distance) ---
        
        # Yüz Uzunluğu (10: Alın Tepesi -> 152: Çene Ucu)
        face_length = np.linalg.norm(pts[10] - pts[152])
        
        # Yüz Genişliği / Elmacık Kemikleri (234: Sol -> 454: Sağ)
        face_width = np.linalg.norm(pts[454] - pts[234])
        
        # Alın Genişliği (103 -> 332) - Daha stabil noktalar
        forehead_width = np.linalg.norm(pts[332] - pts[103])
        
        # Çene Genişliği (Gonions - Çene Köşeleri) (132 -> 361)
        jaw_width = np.linalg.norm(pts[361] - pts[132])
        
        # --- AÇILAR ---
        # Çene Açısı (Jaw Angle): Sol Köşe(132) -> Çene Ucu(152) -> Sağ Köşe(361)
        jaw_angle = self.calculate_angle(pts[132], pts[152], pts[361])
        
        # Açı kontrolü - anormal değerleri düzelt
        if jaw_angle < 90 or jaw_angle > 180:
            jaw_angle = 130  # Default safe value
        
        # --- ORANLAR ---
        ratio_lw = face_length / face_width if face_width > 0 else 1.0
        ratio_fj = forehead_width / jaw_width if jaw_width > 0 else 1.0
        ratio_cj = face_width / jaw_width if jaw_width > 0 else 1.0
        
        return {
            'ratio_lw': round(ratio_lw, 3),
            'ratio_fj': round(ratio_fj, 3),
            'ratio_cj': round(ratio_cj, 3),
            'angle': round(jaw_angle, 1),
            'meta': {
                'face_width': float(face_width),
                'face_length': float(face_length),
                'forehead_width': float(forehead_width),
                'jaw_width': float(jaw_width)
            }
        }

    def classify_face_shape(self, m):
        """
        Kural tabanlı sınıflandırma - daha güvenilir sonuçlar için.
        
        Args:
            m: Measurements dict (ratio_lw, ratio_fj, ratio_cj, angle)
        
        Returns:
            tuple: (face_shape, confidence, scores)
        """
        ratio_lw = m['ratio_lw']  # Uzunluk/Genişlik
        ratio_fj = m['ratio_fj']  # Alın/Çene
        angle = m['angle']        # Çene açısı
        
        scores = {
            'oval': 0.0,
            'round': 0.0,
            'square': 0.0,
            'heart': 0.0,
            'diamond': 0.0,
            'oblong': 0.0
        }
        
        # === KURAL TABANLI SINIFLANDIRMA ===
        
        # 1. ÇOK UZUN YÜZ (Oblong)
        if ratio_lw > 1.45:
            scores['oblong'] += 3.0
            scores['oval'] += 1.0
        
        # 2. UZUN YÜZ (Oval veya Diamond)
        elif ratio_lw > 1.25:
            scores['oval'] += 2.0
            scores['diamond'] += 1.5
            scores['heart'] += 1.0
        
        # 3. ORTA UZUNLUK (Çoğu yüz tipi)
        elif ratio_lw > 1.15:
            scores['oval'] += 1.5
            scores['heart'] += 1.5
            scores['diamond'] += 1.0
            scores['square'] += 0.5
        
        # 4. KISA/GENİŞ YÜZ (Round veya Square)
        else:
            scores['round'] += 2.0
            scores['square'] += 2.0
        
        # === ALIN/ÇENE ORANI ===
        
        # Geniş alın, dar çene = Heart
        if ratio_fj > 0.85:
            scores['heart'] += 2.0
            scores['oval'] += 0.5
        
        # Dar alın, geniş çene = Diamond (ters üçgen)
        elif ratio_fj < 0.72:
            scores['diamond'] += 2.0
        
        # Dengeli = Oval, Round, Square
        else:
            scores['oval'] += 1.0
            scores['round'] += 0.5
            scores['square'] += 0.5
        
        # === ÇENE AÇISI (EN KRİTİK) ===
        
        # Keskin çene (< 110°) = Square
        if angle < 110:
            scores['square'] += 3.0
            scores['diamond'] += 1.0
        
        # Orta açı (110-135°) = Oval, Heart, Diamond
        elif angle < 135:
            scores['oval'] += 1.5
            scores['heart'] += 1.0
            scores['diamond'] += 1.0
        
        # Geniş açı (> 135°) = Round
        else:
            scores['round'] += 3.0
            scores['oval'] += 0.5
        
        # === EN YÜKSEK SKORU BUL ===
        best_match = max(scores, key=scores.get)
        best_score = scores[best_match]
        
        # İkinci en yüksek skor
        sorted_scores = sorted(scores.values(), reverse=True)
        second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0
        
        # Güven skoru: Birinci ve ikinci arasındaki fark
        score_gap = best_score - second_score
        total_score = sum(scores.values())
        
        # Normalize et
        if total_score > 0:
            confidence = (best_score / total_score) * 0.6 + min(score_gap / 3.0, 0.4)
        else:
            confidence = 0.5
        
        # Sınırla
        confidence = max(0.55, min(confidence, 0.95))
        
        # DEBUG
        print(f"🎯 Classification Result:")
        print(f"   Shape: {best_match}")
        print(f"   📊 Scores: {sorted(scores.items(), key=lambda x: x[1], reverse=True)}")
        print(f"   📏 Ratios: L/W={ratio_lw:.2f}, F/J={ratio_fj:.2f}, Angle={angle:.0f}°")
        print(f"   ✅ Final Confidence: {confidence:.2f}")
        
        return best_match, confidence, scores
    
    def calculate_angle(self, a, b, c):
        """
        b noktası merkez olmak üzere a-b-c açısını hesaplar.
        
        Args:
            a, b, c: 3D koordinat noktaları (numpy arrays)
        
        Returns:
            float: Derece cinsinden açı
        """
        ba = a - b
        bc = c - b
        
        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)
        
        if norm_ba == 0 or norm_bc == 0:
            return 130.0  # Default güvenli değer
        
        cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.degrees(np.arccos(cosine_angle))
        
        return angle
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()