"""Görüntü İşleme Motoru — Tüm algoritmalar bu modülde."""
import cv2
import numpy as np


class ImageProcessor:
    """Sampling, Quantization ve diğer tüm görüntü işleme algoritmaları."""

    # ── Metrikler ──
    @staticmethod
    def psnr(orig, proc):
        mse = np.mean((orig.astype(np.float32) - proc.astype(np.float32)) ** 2)
        if mse == 0:
            return float("inf")
        return 20 * np.log10(255.0 / np.sqrt(mse))

    # ── 02: Örnekleme (Sampling) ──
    @staticmethod
    def apply_sampling(img, factor):
        if factor < 2:
            return img.copy()
        h, w = img.shape[:2]
        small = cv2.resize(img, (max(1, w // factor), max(1, h // factor)),
                           interpolation=cv2.INTER_NEAREST)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    # ── 03: Kuantalama (Quantization) ──
    @staticmethod
    def apply_quantization(img, bits):
        bits = max(1, min(8, bits))
        levels = 2 ** bits
        step = 256 // levels
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        quant = (gray // step) * step
        return cv2.cvtColor(quant, cv2.COLOR_GRAY2BGR)

    # ── 04: Renk Uzayları ──
    @staticmethod
    def convert_color_space(img, space):
        if space == "Grayscale":
            g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        elif space == "HSV":
            return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        elif space == "Lab":
            return cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
        elif space == "R Kanalı":
            out = np.zeros_like(img); out[:, :, 2] = img[:, :, 2]; return out
        elif space == "G Kanalı":
            out = np.zeros_like(img); out[:, :, 1] = img[:, :, 1]; return out
        elif space == "B Kanalı":
            out = np.zeros_like(img); out[:, :, 0] = img[:, :, 0]; return out
        return img.copy()

    # ── 05: Enhancement ──
    @staticmethod
    def apply_histogram_eq(img):
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        eq = cv2.equalizeHist(gray)
        return cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def apply_clahe(img, clip_limit=2.0, grid_size=8):
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        clahe = cv2.createCLAHE(clipLimit=clip_limit,
                                tileGridSize=(grid_size, grid_size))
        result = clahe.apply(gray)
        return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

    # ── 06: Restorasyon ──
    @staticmethod
    def apply_gaussian_blur(img, ksize=5):
        ksize = ksize if ksize % 2 == 1 else ksize + 1
        return cv2.GaussianBlur(img, (ksize, ksize), 0)

    @staticmethod
    def apply_median_blur(img, ksize=5):
        ksize = ksize if ksize % 2 == 1 else ksize + 1
        return cv2.medianBlur(img, ksize)

    @staticmethod
    def add_noise(img, amount=30):
        rng = np.random.default_rng(42)
        noise = rng.integers(-amount, amount, img.shape, dtype=np.int16)
        return np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # ── 07: Morfolojik İşlemler ──
    @staticmethod
    def apply_morphology(img, op, ksize=5):
        ksize = max(3, ksize if ksize % 2 == 1 else ksize + 1)
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        _, binary = cv2.threshold(gray, 0, 255,
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
        ops = {"Dilation": cv2.MORPH_DILATE, "Erosion": cv2.MORPH_ERODE,
               "Opening": cv2.MORPH_OPEN, "Closing": cv2.MORPH_CLOSE}
        morph_op = ops.get(op, cv2.MORPH_DILATE)
        if morph_op == cv2.MORPH_DILATE:
            result = cv2.dilate(binary, kernel)
        elif morph_op == cv2.MORPH_ERODE:
            result = cv2.erode(binary, kernel)
        else:
            result = cv2.morphologyEx(binary, morph_op, kernel)
        return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

    # ── 08: Eşikleme (Thresholding) ──
    @staticmethod
    def apply_threshold(img, method="Global", value=128, block_size=11):
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        if method == "Global":
            _, result = cv2.threshold(gray, value, 255, cv2.THRESH_BINARY)
        elif method == "Otsu":
            _, result = cv2.threshold(gray, 0, 255,
                                      cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == "Adaptive Gaussian":
            bs = block_size if block_size % 2 == 1 else block_size + 1
            bs = max(3, bs)
            result = cv2.adaptiveThreshold(gray, 255,
                                           cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, bs, 2)
        else:
            _, result = cv2.threshold(gray, value, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

    # ── 09: Kenar Algılama ──
    @staticmethod
    def apply_edge_detection(img, method="Canny", low=50, high=150):
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        if method == "Canny":
            result = cv2.Canny(gray, low, high)
        elif method == "Sobel X":
            s = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            result = np.clip(np.abs(s) / (np.abs(s).max() + 1e-9) * 255,
                             0, 255).astype(np.uint8)
        elif method == "Sobel Y":
            s = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            result = np.clip(np.abs(s) / (np.abs(s).max() + 1e-9) * 255,
                             0, 255).astype(np.uint8)
        elif method == "Sobel Combined":
            sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            mag = cv2.magnitude(sx, sy)
            result = np.clip(mag / (mag.max() + 1e-9) * 255,
                             0, 255).astype(np.uint8)
        elif method == "Laplacian":
            lap = np.abs(cv2.Laplacian(gray, cv2.CV_64F))
            result = np.clip(lap / (lap.max() + 1e-9) * 255,
                             0, 255).astype(np.uint8)
        else:
            result = cv2.Canny(gray, low, high)
        return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

    # ── 10: K-Means Segmentasyon ──
    @staticmethod
    def apply_kmeans(img, k=4):
        Z = img.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
        _, labels, centers = cv2.kmeans(Z, k, None, criteria, 10,
                                        cv2.KMEANS_RANDOM_CENTERS)
        centers_u8 = np.uint8(centers)
        return centers_u8[labels.flatten()].reshape(img.shape)

    # ── 13: Emboss / Geometrik ──
    @staticmethod
    def apply_emboss(img, direction="SE"):
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        kernels = {
            "SE": np.array([[-2,-1,0],[-1,1,1],[0,1,2]]),
            "NW": np.array([[0,-1,-1],[1,0,-1],[1,1,0]]),
            "Diagonal": np.array([[-1,-1,0],[-1,0,1],[0,1,1]]),
        }
        k = kernels.get(direction, kernels["SE"])
        emb = cv2.filter2D(gray, -1, k)
        result = np.clip(emb + 128, 0, 255).astype(np.uint8)
        return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

    # ── Parlaklık / Kontrast ──
    @staticmethod
    def adjust_brightness_contrast(img, brightness=0, contrast=0):
        b = brightness / 100.0
        c = contrast / 100.0
        result = img.astype(np.float32)
        if c != 0:
            f = 131 * (c * 127 + 127) / (127 * (131 - c * 127))
            result = f * (result - 127) + 127
        result = result + b * 255
        return np.clip(result, 0, 255).astype(np.uint8)

    # ── Görünmezlik Pelerini (Invisibility Cloak) ──

    # Ön-hesaplanmış kerneller (her frame'de tekrar oluşturmayı önler)
    _KERNEL_CLOSE = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    _KERNEL_OPEN = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    _KERNEL_DILATE = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    @staticmethod
    def create_color_mask_fast(img, color_bgr, tolerance=30):
        """HSV uzayında seçilen renge göre maske oluşturur (Hız Optimize)."""
        # Hafif blur (3x3 daha hızlı)
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # BGR -> HSV dönüşümü (tek piksel)
        color_pixel = np.uint8([[color_bgr]])
        hsv_color = cv2.cvtColor(color_pixel, cv2.COLOR_BGR2HSV)[0][0]

        h, s, v = int(hsv_color[0]), int(hsv_color[1]), int(hsv_color[2])
        h_tol = max(10, tolerance // 2)

        # Dinamik S ve V toleransı
        s_tol = max(30, int((s / 255.0) * tolerance * 2.5))
        v_tol = max(30, int((v / 255.0) * tolerance * 2.5))

        lower = np.array([max(0, h - h_tol), max(20, s - s_tol), max(20, v - v_tol)])
        upper = np.array([min(179, h + h_tol), min(255, s + s_tol), min(255, v + v_tol)])

        # Kırmızı renk wrap-around
        if h - h_tol < 0:
            mask = (cv2.inRange(hsv, np.array([0, lower[1], lower[2]]),
                                     np.array([h + h_tol, upper[1], upper[2]])) |
                    cv2.inRange(hsv, np.array([179 + (h - h_tol), lower[1], lower[2]]),
                                     np.array([179, upper[1], upper[2]])))
        elif h + h_tol > 179:
            mask = (cv2.inRange(hsv, np.array([h - h_tol, lower[1], lower[2]]),
                                     np.array([179, upper[1], upper[2]])) |
                    cv2.inRange(hsv, np.array([0, lower[1], lower[2]]),
                                     np.array([(h + h_tol) - 179, upper[1], upper[2]])))
        else:
            mask = cv2.inRange(hsv, lower, upper)

        # Morfolojik temizlik (daha küçük kerneller = daha hızlı)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, ImageProcessor._KERNEL_CLOSE, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, ImageProcessor._KERNEL_OPEN, iterations=1)

        # Kontur analizi ile gürültü filtreleme
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return mask  # Boş maske, kontur yok

        clean_mask = np.zeros_like(mask)
        for cnt in contours:
            if cv2.contourArea(cnt) > 400:
                cv2.drawContours(clean_mask, [cnt], -1, 255, -1)

        return clean_mask

    # Eski API uyumluluğu
    @staticmethod
    def create_color_mask(img, color_bgr, tolerance=30):
        return ImageProcessor.create_color_mask_fast(img, color_bgr, tolerance)

    @staticmethod
    def apply_invisibility_static(img, color_bgr, tolerance=30):
        """Statik görüntüde seçilen rengi inpaint ile siler."""
        mask = ImageProcessor.create_color_mask_fast(img, color_bgr, tolerance)
        dilated = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
        result = cv2.inpaint(img, dilated, inpaintRadius=7, flags=cv2.INPAINT_TELEA)
        return result

    @staticmethod
    def apply_invisibility_realtime(frame, background, color_bgr, tolerance=30,
                                     prev_mask=None, mode="static",
                                     dynamic_bg=None, show_mask=False):
        """
        Kamera modunda görünmezlik pelerini efekti (Düşük Gecikmeli).

        Optimizasyonlar:
        - Temporal smoothing: %85/%15 oran (hızlı tepki, az titreme)
        - Dinamik BG: %30 öğrenme oranı (anlık güncelleme)
        - Ön-hesaplanmış kerneller
        - Boş maske fast-path (maskeleme yoksa frame'i direkt döndür)

        Returns:
            (result_frame, new_prev_mask, updated_dynamic_bg)
        """
        h, w = frame.shape[:2]

        # 1. Maske oluştur
        current_mask = ImageProcessor.create_color_mask_fast(frame, color_bgr, tolerance)

        # 2. Temporal Smoothing — hızlı tepki + az titreme
        #    %85 yeni maske, %15 eski → nesne hareket edince anında takip
        if prev_mask is not None:
            current_f = current_mask.astype(np.float32)
            smoothed_mask = cv2.addWeighted(current_f, 0.85, prev_mask, 0.15, 0)
        else:
            smoothed_mask = current_mask.astype(np.float32)

        new_prev_mask = smoothed_mask  # .copy() yerine referans (hız)

        # 3. Binary maske
        _, core_mask = cv2.threshold(smoothed_mask, 100, 255, cv2.THRESH_BINARY)
        core_mask = core_mask.astype(np.uint8)

        # Fast path: maske boşsa frame'i direkt döndür
        mask_sum = cv2.countNonZero(core_mask)
        if mask_sum == 0:
            # Dinamik BG'yi güncellemeye devam et
            updated_dynamic_bg = dynamic_bg
            if mode == "dynamic":
                if dynamic_bg is None:
                    updated_dynamic_bg = frame.copy()
                else:
                    # Tüm pikseller görünür, hızlı güncelle
                    alpha_u = 0.3
                    updated_dynamic_bg = cv2.addWeighted(
                        dynamic_bg, 1.0 - alpha_u, frame, alpha_u, 0)
            return frame, new_prev_mask, updated_dynamic_bg

        # 4. Kenar feathering (hafif, hızlı)
        dilated_core = cv2.dilate(core_mask, ImageProcessor._KERNEL_DILATE, iterations=1)
        # Dilated mask'in kendisine blur uygula (feathered alpha üret)
        # Bu yöntem edge_zone hesabından daha hızlı
        alpha_mask = cv2.GaussianBlur(dilated_core.astype(np.float32), (11, 11), 0)
        # Core bölgeyi tam opak yap
        alpha_mask = np.maximum(alpha_mask, core_mask.astype(np.float32))
        alpha_mask = np.clip(alpha_mask, 0, 255)

        # Debug: maske görünümü
        if show_mask:
            overlay = frame.copy()
            overlay[core_mask > 0] = [0, 0, 255]
            result = cv2.addWeighted(frame, 0.5, overlay, 0.5, 0)
            pct = mask_sum * 100.0 / (h * w)
            cv2.putText(result, f"MASK DEBUG - {pct:.1f}% masked ({mask_sum} px)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(result, f"Tolerance: {tolerance}  Color(BGR): {color_bgr}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            return result, new_prev_mask, dynamic_bg

        # Alfa kanalı 0-1 (3 kanallı)
        alpha_norm = alpha_mask / 255.0
        alpha_3ch = np.stack([alpha_norm, alpha_norm, alpha_norm], axis=-1)

        # 5. Arka planı hazırla
        updated_dynamic_bg = dynamic_bg

        if mode == "dynamic":
            # ─── DİNAMİK MOD: Canlı arka plan modeli ───
            if dynamic_bg is None:
                updated_dynamic_bg = frame.copy()
            else:
                # Maskelenmemiş pikselleri HIZLI güncelle (alpha=0.3 → ~3 frame'de arka plan hazır)
                not_masked = core_mask == 0
                updated_dynamic_bg = dynamic_bg.copy()
                # Vektörize güncelleme — piksel piksel yerine tüm maske
                updated_dynamic_bg = cv2.addWeighted(dynamic_bg, 0.7, frame, 0.3, 0)
                # Maskelenmiş bölgeleri eski haline geri koy (onları güncelleme)
                updated_dynamic_bg[~not_masked] = dynamic_bg[~not_masked]

            bg = updated_dynamic_bg.astype(np.float32)
        else:
            # ─── SABİT MOD ───
            if background is not None:
                if background.shape[:2] != (h, w):
                    bg = cv2.resize(background, (w, h)).astype(np.float32)
                else:
                    bg = background.astype(np.float32)
            else:
                bg = frame.astype(np.float32)

        # 6. Alpha Blending
        fg = frame.astype(np.float32)
        result = (bg * alpha_3ch + fg * (1.0 - alpha_3ch)).astype(np.uint8)

        return result, new_prev_mask, updated_dynamic_bg
