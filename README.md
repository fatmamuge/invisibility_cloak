# 🎨  Photoshop - Görüntü İşleme Stüdyosu & Görünmezlik Pelerini

PyQt5 ve OpenCV kullanılarak geliştirilmiş, gelişmiş özelliklere sahip bir masaüstü görüntü işleme ve kamera efektleri uygulamasıdır. Klasik fotoğraf düzenleme araçlarının yanı sıra, gerçek zamanlı çalışan özel bir "Harry Potter Görünmezlik Pelerini" efektine sahiptir.

## 🌟 Özellikler

### 🖼️ Görüntü İşleme Araçları
* **Temel Ayarlar:** Parlaklık ve Kontrast ayarı.
* **Görüntü Kalitesi:** Örnekleme (Sampling) ve Kuantalama (Quantization).
* **Renk Uzayları:** Grayscale, HSV, Lab ve RGB kanal ayrımları.
* **Görüntü İyileştirme (Enhancement):** Histogram Eşitleme ve CLAHE.
* **Restorasyon & Filtreler:** Gaussian Blur, Median Blur ve Gürültü Ekleme.
* **Morfolojik İşlemler:** Dilation, Erosion, Opening, Closing.
* **Segmentasyon & Eşikleme:** Global, Otsu, Adaptive Gaussian threshold ve K-Means Segmentasyon.
* **Kenar Algılama & Efektler:** Canny, Sobel, Laplacian ve Emboss (Kabartma) filtreleri.
* **Karşılaştırma Modu:** Orijinal ve işlenmiş görüntüyü anında karşılaştırabilme (Geri Al / İleri Al destekli).

### 🧙‍♂️ Gerçek Zamanlı Görünmezlik Pelerini (Kamera Efekti)
Kamera üzerinden gerçek zamanlı çalışarak belirli renkteki bir nesneyi (örneğin kırmızı bir cisim) "görünmez" yapan özel bir modül:
* **Sabit ve Dinamik Arka Plan Modu:** Daha iyi bir illüzyon için arka planı algılama.
* **Renk Seçimi:** Kamera görüntüsüne tıklayarak montun/nesnenin rengini kolayca yakalayabilme.
* **Maske Hata Ayıklama (Debug):** Algılanan alanları kırmızıyla gösteren yardımcı analiz aracı.
* Düşük gecikmeli MJPG kamera entegrasyonu.

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
Projeyi çalıştırmak için bilgisayarınızda **Python 3.7+** sürümünün yüklü olması gerekmektedir.

1. Repoyu bilgisayarınıza klonlayın:
   ```bash
   git clone git@github.com:fatmamuge/invisibility_cloak.git
   cd invisibility_cloak

2. Gerekli kütüphaneleri yüklemek için terminal veya komut satırında şu komutu çalıştırın:

pip install -r requirements.txt

3. Uygulamayı başlatın:

python photoshop_app.py
