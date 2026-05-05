"""PyQt5 Photoshop Uygulaması — Ana UI"""
import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QComboBox, QFileDialog, QScrollArea,
    QGroupBox, QDockWidget, QStatusBar, QAction, QToolBar, QSplitter,
    QSpinBox, QMessageBox, QSizePolicy, QFrame, QColorDialog
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon, QFont, QPalette, QColor
from image_processor import ImageProcessor


DARK_STYLE = """
QMainWindow { background-color: #0d1117; }
QWidget { background-color: #0d1117; color: #e0e0e0; font-family: 'Segoe UI', 'Ubuntu', sans-serif; }
QMenuBar { background-color: #161b22; color: #e0e0e0; border-bottom: 1px solid #30363d; font-size: 13px; }
QMenuBar::item:selected { background-color: #1f6feb; border-radius: 4px; }
QMenu { background-color: #161b22; color: #e0e0e0; border: 1px solid #30363d; }
QMenu::item:selected { background-color: #1f6feb; }
QToolBar { background-color: #161b22; border: none; spacing: 4px; padding: 4px; }
QToolButton { background-color: transparent; color: #e0e0e0; border: 1px solid transparent; border-radius: 6px; padding: 8px 12px; font-size: 12px; min-width: 90px; }
QToolButton:hover { background-color: #1f6feb33; border: 1px solid #1f6feb; }
QToolButton:checked { background-color: #1f6feb; color: white; }
QPushButton { background-color: #21262d; color: #e0e0e0; border: 1px solid #30363d; border-radius: 6px; padding: 8px 16px; font-size: 12px; }
QPushButton:hover { background-color: #1f6feb; border-color: #1f6feb; }
QPushButton:pressed { background-color: #1158c7; }
QGroupBox { border: 1px solid #30363d; border-radius: 8px; margin-top: 12px; padding-top: 20px; font-weight: bold; font-size: 13px; color: #58a6ff; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QSlider::groove:horizontal { border: none; height: 6px; background: #30363d; border-radius: 3px; }
QSlider::handle:horizontal { background: #1f6feb; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }
QSlider::handle:horizontal:hover { background: #58a6ff; }
QSlider::sub-page:horizontal { background: #1f6feb; border-radius: 3px; }
QComboBox { background-color: #21262d; color: #e0e0e0; border: 1px solid #30363d; border-radius: 6px; padding: 6px 10px; font-size: 12px; }
QComboBox:hover { border-color: #1f6feb; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView { background-color: #161b22; color: #e0e0e0; border: 1px solid #30363d; selection-background-color: #1f6feb; }
QSpinBox { background-color: #21262d; color: #e0e0e0; border: 1px solid #30363d; border-radius: 6px; padding: 4px 8px; }
QLabel { color: #b0bec5; }
QStatusBar { background-color: #161b22; color: #8b949e; border-top: 1px solid #30363d; font-size: 12px; }
QScrollArea { border: none; }
QDockWidget { color: #e0e0e0; font-weight: bold; }
QDockWidget::title { background-color: #161b22; padding: 8px; border-bottom: 1px solid #30363d; }
QSplitter::handle { background-color: #30363d; }
"""


def cv2_to_qpixmap(img, max_w=None, max_h=None):
    if img is None:
        return QPixmap()
    if len(img.shape) == 2:
        h, w = img.shape
        data = np.ascontiguousarray(img)
        qimg = QImage(data.data, w, h, w, QImage.Format_Grayscale8).copy()
    else:
        rgb = np.ascontiguousarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
    pix = QPixmap.fromImage(qimg)
    if max_w and max_h:
        pix = pix.scaled(max_w, max_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return pix


class ImageCanvas(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #010409; border: 1px solid #30363d; border-radius: 8px;")
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setText("📷 Görüntü yüklemek için Dosya → Aç\n\nveya Görünmezlik Pelerini için\nSağdaki menüden 📹 Kamerayı Aç'a tıklayın!")
        self.setFont(QFont("Segoe UI", 14))
        self._current_cv_img = None  # Tıklama ile renk almak için
        self.color_pick_callback = None  # Renk seçilince çağrılacak fonksiyon

    def show_image(self, img):
        if img is None:
            return
        self._current_cv_img = img.copy()
        pix = cv2_to_qpixmap(img, self.width() - 20, self.height() - 20)
        self.setPixmap(pix)

    def mousePressEvent(self, event):
        """Görüntüye tıklayarak renk seçme."""
        if self.color_pick_callback and self._current_cv_img is not None and self.pixmap():
            # Tıklama pozisyonunu görüntü koordinatlarına çevir
            pix = self.pixmap()
            # Pixmap'in label içindeki konumu (ortalanmış)
            x_offset = (self.width() - pix.width()) // 2
            y_offset = (self.height() - pix.height()) // 2
            click_x = event.x() - x_offset
            click_y = event.y() - y_offset
            if 0 <= click_x < pix.width() and 0 <= click_y < pix.height():
                # Pixmap koordinatlarını orijinal görüntü koordinatlarına ölçekle
                img_h, img_w = self._current_cv_img.shape[:2]
                real_x = int(click_x * img_w / pix.width())
                real_y = int(click_y * img_h / pix.height())
                real_x = min(max(0, real_x), img_w - 1)
                real_y = min(max(0, real_y), img_h - 1)
                bgr = self._current_cv_img[real_y, real_x].tolist()
                self.color_pick_callback(bgr)
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)


class ToolPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.widgets = {}
        self._build_all_tools()
        self.layout.addStretch()

    def _make_group(self, title, widgets_list):
        grp = QGroupBox(title)
        lay = QVBoxLayout()
        lay.setSpacing(6)
        for w in widgets_list:
            if isinstance(w, tuple):
                row = QHBoxLayout()
                for item in w:
                    row.addWidget(item)
                lay.addLayout(row)
            else:
                lay.addWidget(w)
        grp.setLayout(lay)
        return grp

    def _make_slider(self, name, min_v, max_v, default, label_fmt="{}"):
        lbl = QLabel(label_fmt.format(default, default))
        lbl.setStyleSheet("color: #58a6ff; font-weight: bold; font-size: 12px;")
        sl = QSlider(Qt.Horizontal)
        sl.setRange(min_v, max_v)
        sl.setValue(default)
        sl.valueChanged.connect(lambda v: lbl.setText(label_fmt.format(v, v)))
        self.widgets[name] = sl
        self.widgets[name + "_lbl"] = lbl
        return lbl, sl

    def _build_all_tools(self):
        # ── Parlaklık / Kontrast ──
        bl, bs = self._make_slider("brightness", -100, 100, 0, "Parlaklık: {}")
        cl, cs = self._make_slider("contrast", -100, 100, 0, "Kontrast: {}")
        btn_bc = QPushButton("✨ Uygula")
        btn_bc.clicked.connect(lambda: self.app.apply_tool("brightness_contrast"))
        self.layout.addWidget(self._make_group("☀️ Parlaklık / Kontrast", [bl, bs, cl, cs, btn_bc]))

        # ── Sampling ──
        sl, ss = self._make_slider("sampling_factor", 2, 16, 4, "Faktör: 1/{}")
        btn_s = QPushButton("📐 Örnekleme Uygula")
        btn_s.clicked.connect(lambda: self.app.apply_tool("sampling"))
        self.layout.addWidget(self._make_group("📐 Örnekleme (Sampling)", [sl, ss, btn_s]))

        # ── Quantization ──
        ql, qs = self._make_slider("quant_bits", 1, 8, 4, "Bit: {}")
        btn_q = QPushButton("🎨 Kuantalama Uygula")
        btn_q.clicked.connect(lambda: self.app.apply_tool("quantization"))
        self.layout.addWidget(self._make_group("🎨 Kuantalama (Quantization)", [ql, qs, btn_q]))

        # ── Renk Uzayları ──
        cb_color = QComboBox()
        cb_color.addItems(["Grayscale", "HSV", "Lab", "R Kanalı", "G Kanalı", "B Kanalı"])
        self.widgets["color_space"] = cb_color
        btn_c = QPushButton("🌈 Dönüştür")
        btn_c.clicked.connect(lambda: self.app.apply_tool("color_space"))
        self.layout.addWidget(self._make_group("🌈 Renk Uzayları", [cb_color, btn_c]))

        # ── Enhancement ──
        cb_enh = QComboBox()
        cb_enh.addItems(["Histogram Eşitleme", "CLAHE"])
        self.widgets["enhancement_type"] = cb_enh
        el, es = self._make_slider("clahe_clip", 10, 80, 20, "CLAHE Clip: {:.1f}")
        btn_e = QPushButton("📊 Enhancement Uygula")
        btn_e.clicked.connect(lambda: self.app.apply_tool("enhancement"))
        self.layout.addWidget(self._make_group("📊 Enhancement", [cb_enh, el, es, btn_e]))

        # ── Restorasyon ──
        cb_blur = QComboBox()
        cb_blur.addItems(["Gaussian Blur", "Median Blur"])
        self.widgets["blur_type"] = cb_blur
        rl, rs = self._make_slider("blur_ksize", 3, 31, 5, "Kernel: {}×{}")
        btn_noise = QPushButton("🔊 Gürültü Ekle")
        btn_noise.clicked.connect(lambda: self.app.apply_tool("add_noise"))
        btn_r = QPushButton("🔧 Filtre Uygula")
        btn_r.clicked.connect(lambda: self.app.apply_tool("restoration"))
        self.layout.addWidget(self._make_group("🔧 Restorasyon", [cb_blur, rl, rs, btn_noise, btn_r]))

        # ── Morfolojik ──
        cb_morph = QComboBox()
        cb_morph.addItems(["Dilation", "Erosion", "Opening", "Closing"])
        self.widgets["morph_op"] = cb_morph
        ml, ms = self._make_slider("morph_ksize", 3, 21, 5, "Kernel: {}×{}")
        btn_m = QPushButton("⚙️ Morfoloji Uygula")
        btn_m.clicked.connect(lambda: self.app.apply_tool("morphology"))
        self.layout.addWidget(self._make_group("⚙️ Morfolojik İşlemler", [cb_morph, ml, ms, btn_m]))

        # ── Thresholding ──
        cb_th = QComboBox()
        cb_th.addItems(["Global", "Otsu", "Adaptive Gaussian"])
        self.widgets["thresh_method"] = cb_th
        tl, ts = self._make_slider("thresh_value", 0, 255, 128, "Eşik: {}")
        t2l, t2s = self._make_slider("thresh_block", 3, 51, 11, "Blok: {}")
        btn_t = QPushButton("◼ Eşikleme Uygula")
        btn_t.clicked.connect(lambda: self.app.apply_tool("threshold"))
        self.layout.addWidget(self._make_group("◼ Eşikleme (Thresholding)", [cb_th, tl, ts, t2l, t2s, btn_t]))

        # ── Edge Detection ──
        cb_edge = QComboBox()
        cb_edge.addItems(["Canny", "Sobel X", "Sobel Y", "Sobel Combined", "Laplacian"])
        self.widgets["edge_method"] = cb_edge
        e1l, e1s = self._make_slider("edge_low", 0, 300, 50, "Alt eşik: {}")
        e2l, e2s = self._make_slider("edge_high", 0, 300, 150, "Üst eşik: {}")
        btn_ed = QPushButton("🔍 Kenar Algıla")
        btn_ed.clicked.connect(lambda: self.app.apply_tool("edge_detection"))
        self.layout.addWidget(self._make_group("🔍 Kenar Algılama", [cb_edge, e1l, e1s, e2l, e2s, btn_ed]))

        # ── K-Means ──
        kl, ks = self._make_slider("kmeans_k", 2, 16, 4, "K = {}")
        btn_k = QPushButton("🧩 K-Means Uygula")
        btn_k.clicked.connect(lambda: self.app.apply_tool("kmeans"))
        self.layout.addWidget(self._make_group("🧩 K-Means Segmentasyon", [kl, ks, btn_k]))

        # ── Emboss ──
        cb_emb = QComboBox()
        cb_emb.addItems(["SE", "NW", "Diagonal"])
        self.widgets["emboss_dir"] = cb_emb
        btn_emb = QPushButton("🏔️ Emboss Uygula")
        btn_emb.clicked.connect(lambda: self.app.apply_tool("emboss"))
        self.layout.addWidget(self._make_group("🏔️ Emboss / Kabartma", [cb_emb, btn_emb]))

        # ── Görünmezlik Pelerini ──
        self.cloak_color = [0, 0, 255]  # Varsayılan: kırmızı (BGR)

        # Durum etiketi
        self.cloak_status = QLabel("⏸️ Kamera kapalı")
        self.cloak_status.setStyleSheet(
            "color: #8b949e; font-weight: bold; font-size: 13px; "
            "padding: 6px; border: 2px solid #30363d; border-radius: 6px; "
            "background-color: #161b22;")
        self.cloak_status.setAlignment(Qt.AlignCenter)

        # Renk göstergesi
        self.cloak_color_label = QLabel("🎨 Cisim rengi: Henüz seçilmedi")
        self.cloak_color_label.setStyleSheet(
            "color: #8b949e; font-weight: bold; font-size: 12px; "
            "padding: 4px; border: 2px dashed #30363d; border-radius: 4px;")
        self.cloak_color_label.setAlignment(Qt.AlignCenter)

        il, i_s = self._make_slider("cloak_tolerance", 5, 80, 30, "Tolerans: {}")

        # Arka Plan Modu Seçimi
        cb_mode = QComboBox()
        cb_mode.addItems(["Sabit Arka Plan (Klasik)", "Dinamik Arka Plan (Canlı)"])
        self.widgets["cloak_bg_mode"] = cb_mode

        # Adım 1: Kamerayı aç
        btn_cam_start = QPushButton("1️⃣  📹 Kamerayı Aç")
        btn_cam_start.setStyleSheet(
            "QPushButton { background-color: #1a472a; border-color: #2ea043; font-size: 13px; padding: 10px; }"
            "QPushButton:hover { background-color: #2ea043; }")
        btn_cam_start.clicked.connect(lambda: self.app.start_cloak_camera())

        # Adım 2: Arka planı kaydet
        btn_save_bg = QPushButton("2️⃣  📸 Arka Planı Kaydet")
        btn_save_bg.setStyleSheet(
            "QPushButton { background-color: #1a3a5c; border-color: #1f6feb; font-size: 13px; padding: 10px; }"
            "QPushButton:hover { background-color: #1f6feb; }")
        btn_save_bg.clicked.connect(lambda: self.app.save_cloak_background())

        # Adım 3: Cisim rengini yakala (görüntüye tıkla)
        btn_pick_from_cam = QPushButton("3️⃣  🎨 Cisimin Rengini Yakala\n(Görüntüye tıklayın)")
        btn_pick_from_cam.setStyleSheet(
            "QPushButton { background-color: #4a1a4a; border-color: #a855f7; font-size: 13px; padding: 10px; }"
            "QPushButton:hover { background-color: #a855f7; }")
        btn_pick_from_cam.clicked.connect(lambda: self.app.enable_color_pick_mode())

        # Adım 4: Efekti başlat
        btn_start_effect = QPushButton("4️⃣  🧙 Görünmezlik Efektini Başlat")
        btn_start_effect.setStyleSheet(
            "QPushButton { background-color: #5c3a1a; border-color: #f59e0b; font-size: 13px; padding: 10px; }"
            "QPushButton:hover { background-color: #f59e0b; color: black; }")
        btn_start_effect.clicked.connect(lambda: self.app.start_cloak_effect())

        # Maske Debug Butonu
        btn_mask_debug = QPushButton("🔴 Maske Görünümü (Debug)")
        btn_mask_debug.setCheckable(True)
        btn_mask_debug.setStyleSheet(
            "QPushButton { background-color: #3a1a1a; border-color: #ef4444; font-size: 12px; padding: 8px; }"
            "QPushButton:hover { background-color: #ef4444; }"
            "QPushButton:checked { background-color: #ef4444; color: white; }")
        btn_mask_debug.clicked.connect(lambda checked: self.app.toggle_mask_debug(checked))
        self.widgets["mask_debug_btn"] = btn_mask_debug

        # Durdur
        btn_cam_stop = QPushButton("⏹️ Kamerayı Durdur")
        btn_cam_stop.setStyleSheet(
            "QPushButton { background-color: #4a1a1a; border-color: #da3633; }"
            "QPushButton:hover { background-color: #da3633; }")
        btn_cam_stop.clicked.connect(lambda: self.app.stop_cloak_camera())

        # Renk paleti ile seçme (alternatif)
        btn_pick_dialog = QPushButton("🎨 Renk Paletinden Seç (Alternatif)")
        btn_pick_dialog.clicked.connect(self._pick_cloak_color)

        cam_info = QLabel(
            "Adımlar:\n"
            "1. Kamerayı açın\n"
            "2. (Sadece Sabit Modda) Sahneyi boş bırakıp arka planı kaydedin\n"
            "3. Cisimi gösterip rengini yakalayın\n"
            "4. Efekti başlatın — cisim görünmez olacak!\n"
            "\n💡 İpucu: Sabit mod en iyi sonucu verir!")
        cam_info.setStyleSheet("color: #8b949e; font-size: 11px; padding: 6px;")
        cam_info.setWordWrap(True)

        self.layout.addWidget(self._make_group(
            "🧙 Görünmezlik Pelerini (Harry Potter)",
            [self.cloak_status, cb_mode, cam_info,
             btn_cam_start, btn_save_bg, btn_pick_from_cam, btn_pick_dialog,
             self.cloak_color_label, il, i_s,
             btn_start_effect, btn_mask_debug, btn_cam_stop]))

    def _pick_cloak_color(self):
        """Renk seçici dialog açar."""
        cur = QColor(self.cloak_color[2], self.cloak_color[1], self.cloak_color[0])
        color = QColorDialog.getColor(cur, self, "Cisim Rengini Seçin")
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            self.cloak_color = [b, g, r]  # BGR
            self._update_color_display(r, g, b)

    def _update_color_display(self, r, g, b):
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.cloak_color_label.setText(f"🎨 Cisim rengi: R={r} G={g} B={b}")
        self.cloak_color_label.setStyleSheet(
            f"color: {hex_color}; font-weight: bold; font-size: 12px; "
            f"padding: 4px; border: 2px solid {hex_color}; border-radius: 4px; "
            f"background-color: #161b22;")

    def update_status(self, text, color="#8b949e"):
        self.cloak_status.setText(text)
        self.cloak_status.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 13px; "
            f"padding: 6px; border: 2px solid {color}; border-radius: 6px; "
            f"background-color: #161b22;")


class PhotoshopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 GSB Photoshop — Görüntü İşleme Stüdyosu")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 850)

        self.processor = ImageProcessor()
        self.original_img = None
        self.current_img = None
        self.undo_stack = []
        self.redo_stack = []

        # Kamera modu için
        self.camera = None
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self._camera_tick)
        self.cloak_background = None
        self.cloak_effect_active = False
        self.cloak_picking_color = False

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()

    def _setup_ui(self):
        # Canvas
        self.canvas = ImageCanvas()

        # Tool panel in scroll area
        self.tool_panel = ToolPanel(self)
        scroll = QScrollArea()
        scroll.setWidget(self.tool_panel)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(300)
        scroll.setMaximumWidth(360)
        scroll.setStyleSheet("QScrollArea { border: none; } QScrollBar:vertical { background: #0d1117; width: 8px; } QScrollBar::handle:vertical { background: #30363d; border-radius: 4px; } QScrollBar::handle:vertical:hover { background: #58a6ff; }")

        # Info panel
        self.info_label = QLabel("Görüntü bilgisi burada gösterilecek")
        self.info_label.setStyleSheet("background-color: #161b22; padding: 10px; border-radius: 6px; font-size: 12px; color: #8b949e; border: 1px solid #30363d;")
        self.info_label.setMaximumHeight(60)
        self.info_label.setAlignment(Qt.AlignCenter)

        # Main layout
        center_layout = QVBoxLayout()
        center_layout.addWidget(self.canvas, 1)
        center_layout.addWidget(self.info_label)
        center_widget = QWidget()
        center_widget.setLayout(center_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(center_widget)
        splitter.addWidget(scroll)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        self.setCentralWidget(splitter)

        # Toolbar
        toolbar = QToolBar("Araçlar")
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)

        btn_open = QPushButton("📂 Aç")
        btn_open.clicked.connect(self.open_image)
        toolbar.addWidget(btn_open)

        btn_save = QPushButton("💾 Kaydet")
        btn_save.clicked.connect(self.save_image)
        toolbar.addWidget(btn_save)

        toolbar.addSeparator()

        btn_cam = QPushButton("📹 Kamerayı Aç (Görünmezlik)")
        btn_cam.setStyleSheet(
            "QPushButton { background-color: #1a472a; border-color: #2ea043; color: white; }"
            "QPushButton:hover { background-color: #2ea043; }")
        btn_cam.clicked.connect(self.start_cloak_camera)
        toolbar.addWidget(btn_cam)

        toolbar.addSeparator()

        btn_undo = QPushButton("↩️ Geri Al")
        btn_undo.clicked.connect(self.undo)
        toolbar.addWidget(btn_undo)

        btn_redo = QPushButton("↪️ İleri Al")
        btn_redo.clicked.connect(self.redo)
        toolbar.addWidget(btn_redo)

        toolbar.addSeparator()

        btn_reset = QPushButton("🔄 Orijinale Dön")
        btn_reset.clicked.connect(self.reset_to_original)
        toolbar.addWidget(btn_reset)

        btn_compare = QPushButton("👁️ Karşılaştır")
        btn_compare.setCheckable(True)
        btn_compare.clicked.connect(self.toggle_compare)
        self.btn_compare = btn_compare
        toolbar.addWidget(btn_compare)

        self.addToolBar(toolbar)

    def _setup_menu(self):
        mb = self.menuBar()
        file_menu = mb.addMenu("Dosya")
        file_menu.addAction(self._action("Aç", "Ctrl+O", self.open_image))
        file_menu.addAction(self._action("Kaydet", "Ctrl+S", self.save_image))
        file_menu.addAction(self._action("Farklı Kaydet", "Ctrl+Shift+S", self.save_as))
        file_menu.addSeparator()
        file_menu.addAction(self._action("Çıkış", "Ctrl+Q", self.close))

        edit_menu = mb.addMenu("Düzenle")
        edit_menu.addAction(self._action("Geri Al", "Ctrl+Z", self.undo))
        edit_menu.addAction(self._action("İleri Al", "Ctrl+Y", self.redo))
        edit_menu.addAction(self._action("Orijinale Dön", "Ctrl+R", self.reset_to_original))

    def _action(self, text, shortcut, slot):
        a = QAction(text, self)
        a.setShortcut(shortcut)
        a.triggered.connect(slot)
        return a

    def _setup_statusbar(self):
        self.statusBar().showMessage("Hazır — Bir görüntü açın")

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Görüntü Aç", "",
            "Görüntüler (*.png *.jpg *.jpeg *.bmp *.tiff *.webp);;Tüm dosyalar (*)")
        if path:
            img = cv2.imread(path)
            if img is not None:
                self.original_img = img.copy()
                self.current_img = img.copy()
                self.undo_stack.clear()
                self.redo_stack.clear()
                self._refresh()
                self.statusBar().showMessage(f"Yüklendi: {os.path.basename(path)}")

    def save_image(self):
        if self.current_img is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Görüntü Kaydet", "output.png",
            "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp)")
        if path:
            cv2.imwrite(path, self.current_img)
            self.statusBar().showMessage(f"Kaydedildi: {path}")

    def save_as(self):
        self.save_image()

    def _push_undo(self):
        if self.current_img is not None:
            self.undo_stack.append(self.current_img.copy())
            if len(self.undo_stack) > 30:
                self.undo_stack.pop(0)
            self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.current_img.copy())
            self.current_img = self.undo_stack.pop()
            self._refresh()
            self.statusBar().showMessage("↩️ Geri alındı")

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.current_img.copy())
            self.current_img = self.redo_stack.pop()
            self._refresh()
            self.statusBar().showMessage("↪️ İleri alındı")

    def reset_to_original(self):
        if self.original_img is not None:
            self._push_undo()
            self.current_img = self.original_img.copy()
            self._refresh()
            self.statusBar().showMessage("🔄 Orijinale dönüldü")

    def toggle_compare(self, checked):
        if self.original_img is not None:
            if checked:
                self.canvas.show_image(self.original_img)
                self.statusBar().showMessage("👁️ Orijinal gösteriliyor")
            else:
                self.canvas.show_image(self.current_img)
                self.statusBar().showMessage("👁️ İşlenmiş gösteriliyor")

    def _refresh(self):
        if self.current_img is not None:
            self.canvas.show_image(self.current_img)
            h, w = self.current_img.shape[:2]
            ch = 1 if len(self.current_img.shape) == 2 else self.current_img.shape[2]
            psnr_txt = ""
            if self.original_img is not None:
                try:
                    p = self.processor.psnr(self.original_img, self.current_img)
                    psnr_txt = f"  |  PSNR: {p:.1f} dB" if p != float('inf') else "  |  PSNR: ∞ (özdeş)"
                except:
                    pass
            self.info_label.setText(
                f"📏 Boyut: {w}×{h}  |  Kanal: {ch}  |  "
                f"Dtype: {self.current_img.dtype}  |  "
                f"Min: {self.current_img.min()} Max: {self.current_img.max()}"
                f"{psnr_txt}")

    def apply_tool(self, tool_name):
        if self.current_img is None:
            QMessageBox.warning(self, "Uyarı", "Önce bir görüntü yükleyin!")
            return
        self._push_undo()
        w = self.tool_panel.widgets
        P = self.processor
        img = self.current_img

        try:
            if tool_name == "brightness_contrast":
                self.current_img = P.adjust_brightness_contrast(
                    img, w["brightness"].value(), w["contrast"].value())
            elif tool_name == "sampling":
                self.current_img = P.apply_sampling(img, w["sampling_factor"].value())
            elif tool_name == "quantization":
                self.current_img = P.apply_quantization(img, w["quant_bits"].value())
            elif tool_name == "color_space":
                self.current_img = P.convert_color_space(img, w["color_space"].currentText())
            elif tool_name == "enhancement":
                if w["enhancement_type"].currentText() == "Histogram Eşitleme":
                    self.current_img = P.apply_histogram_eq(img)
                else:
                    self.current_img = P.apply_clahe(img, w["clahe_clip"].value() / 10.0)
            elif tool_name == "add_noise":
                self.current_img = P.add_noise(img)
            elif tool_name == "restoration":
                ksize = w["blur_ksize"].value()
                if w["blur_type"].currentText() == "Gaussian Blur":
                    self.current_img = P.apply_gaussian_blur(img, ksize)
                else:
                    self.current_img = P.apply_median_blur(img, ksize)
            elif tool_name == "morphology":
                self.current_img = P.apply_morphology(
                    img, w["morph_op"].currentText(), w["morph_ksize"].value())
            elif tool_name == "threshold":
                self.current_img = P.apply_threshold(
                    img, w["thresh_method"].currentText(),
                    w["thresh_value"].value(), w["thresh_block"].value())
            elif tool_name == "edge_detection":
                self.current_img = P.apply_edge_detection(
                    img, w["edge_method"].currentText(),
                    w["edge_low"].value(), w["edge_high"].value())
            elif tool_name == "kmeans":
                self.statusBar().showMessage("⏳ K-Means hesaplanıyor...")
                QApplication.processEvents()
                self.current_img = P.apply_kmeans(img, w["kmeans_k"].value())
            elif tool_name == "emboss":
                self.current_img = P.apply_emboss(img, w["emboss_dir"].currentText())
            elif tool_name == "invisibility_static":
                color_bgr = self.tool_panel.cloak_color
                tol = w["cloak_tolerance"].value()
                self.statusBar().showMessage("⏳ Görünmezlik Pelerini uygulanıyor...")
                QApplication.processEvents()
                self.current_img = P.apply_invisibility_static(img, color_bgr, tol)
            elif tool_name == "show_cloak_mask":
                color_bgr = self.tool_panel.cloak_color
                tol = w["cloak_tolerance"].value()
                mask = P.create_color_mask(img, color_bgr, tol)
                # Maskeyi renkli overlay olarak göster
                overlay = img.copy()
                overlay[mask > 0] = [0, 0, 255]  # Kırmızı ile göster
                self.current_img = cv2.addWeighted(img, 0.5, overlay, 0.5, 0)

            self._refresh()
            self.statusBar().showMessage(f"✅ {tool_name} uygulandı")
        except Exception as e:
            self.undo()
            QMessageBox.critical(self, "Hata", f"İşlem hatası:\n{str(e)}")

    # ── Kamera Modu (Görünmezlik Pelerini) ──

    def start_cloak_camera(self):
        """Adım 1: Kamerayı açar, sadece canlı görüntü gösterir."""
        if self.camera is not None:
            self.stop_cloak_camera()
        self.camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
        # Düşük gecikme ayarları
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        # MJPG codec — USB kameralarda ham formattan çok daha hızlı
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        if not self.camera.isOpened():
            QMessageBox.critical(self, "Hata",
                "Kamera açılamadı!\n\nKontrol edin:\n"
                "• Kamera bağlı mı?\n"
                "• Başka uygulama kullanıyor olabilir\n"
                "• Terminalde: ls /dev/video*")
            self.camera = None
            return
        self.cloak_background = None
        self.cloak_effect_active = False
        self.cloak_picking_color = False
        self.prev_cloak_mask = None
        self.dynamic_background = None
        self.show_mask_debug = False
        self.canvas.color_pick_callback = None
        self.camera_timer.start(33)  # ~30 FPS
        self.tool_panel.update_status("📹 Kamera açık — Canlı yayın", "#2ea043")
        self.statusBar().showMessage("📹 Kamera açıldı! Şimdi Adım 2: Arka planı kaydedin.")

    def save_cloak_background(self):
        """Adım 2: Şu anki frame'i arka plan olarak kaydeder."""
        if self.camera is None:
            QMessageBox.warning(self, "Uyarı", "Önce kamerayı açın! (Adım 1)")
            return
        # Birkaç frame alıp medyan hesapla
        frames = []
        self.tool_panel.update_status("📸 Arka plan kaydediliyor...", "#1f6feb")
        self.statusBar().showMessage("📸 Arka plan kaydediliyor... Sahneyi boş bırakın!")
        QApplication.processEvents()
        for _ in range(30):
            ret, f = self.camera.read()
            if ret:
                frames.append(cv2.flip(f, 1))
        if frames:
            self.cloak_background = np.median(
                np.array(frames), axis=0).astype(np.uint8)
            self.tool_panel.update_status("✅ Arka plan kaydedildi!", "#2ea043")
            self.statusBar().showMessage(
                "✅ Arka plan kaydedildi! Şimdi Adım 3: Cisimi gösterip rengini yakalayın.")
        else:
            QMessageBox.warning(self, "Hata", "Arka plan kaydedilemedi!")

    def enable_color_pick_mode(self):
        """Adım 3: Kullanıcı görüntüye tıklayarak cisim rengini seçer."""
        if self.camera is None:
            QMessageBox.warning(self, "Uyarı", "Önce kamerayı açın! (Adım 1)")
            return
        self.cloak_picking_color = True
        self.canvas.color_pick_callback = self._on_color_picked
        self.tool_panel.update_status(
            "🎯 CISIMIN ÜZERİNE TIKLAYIN!", "#a855f7")
        self.statusBar().showMessage(
            "🎯 Cisimi kameranın önünde tutun ve CISIMin üzerine tıklayın!")

    def _on_color_picked(self, bgr):
        """Kullanıcı görüntüye tıkladığında çağrılır."""
        self.tool_panel.cloak_color = bgr
        r, g, b = bgr[2], bgr[1], bgr[0]  # BGR -> RGB
        self.tool_panel._update_color_display(r, g, b)
        self.cloak_picking_color = False
        self.canvas.color_pick_callback = None
        self.tool_panel.update_status(
            f"🎨 Renk yakalandı! R={r} G={g} B={b}", "#a855f7")
        self.statusBar().showMessage(
            f"✅ Cisim rengi yakalandı! Şimdi Adım 4: Efekti başlatın.")

    def start_cloak_effect(self):
        """Adım 4: Görünmezlik efektini aktif eder."""
        if self.camera is None:
            QMessageBox.warning(self, "Uyarı", "Önce kamerayı açın! (Adım 1)")
            return
        
        mode_text = self.tool_panel.widgets["cloak_bg_mode"].currentText()
        is_dynamic = "Dinamik" in mode_text
        
        if not is_dynamic and self.cloak_background is None:
            QMessageBox.warning(self, "Uyarı", "Sabit Modda önce arka planı kaydetmelisiniz! (Adım 2)")
            return
        self.cloak_effect_active = True
        self.canvas.color_pick_callback = None
        self.tool_panel.update_status(
            "🧙 GÖRÜNMEZLIK AKTİF!", "#f59e0b")
        self.statusBar().showMessage(
            "🧙 Görünmezlik Pelerini aktif! Cismi kameranın önüne getirin!")

    def toggle_mask_debug(self, checked):
        """Maske debug görünümünü açar/kapar."""
        self.show_mask_debug = checked
        if checked:
            self.statusBar().showMessage("🔴 MASKE DEBUG aktif — kırmızı alanlar maskelenen bölgeleri gösterir")
        else:
            self.statusBar().showMessage("🧙 Görünmezlik efekti aktif")

    def stop_cloak_camera(self):
        """Kamerayı durdurur."""
        self.camera_timer.stop()
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.cloak_effect_active = False
        self.cloak_picking_color = False
        self.prev_cloak_mask = None
        self.dynamic_background = None
        self.show_mask_debug = False
        self.canvas.color_pick_callback = None
        self.tool_panel.update_status("⏸️ Kamera kapalı", "#8b949e")
        self.statusBar().showMessage("⏹️ Kamera durduruldu")
        if self.current_img is not None:
            self._refresh()

    def _camera_tick(self):
        """Her frame'de çağrılır — düşük gecikmeli."""
        if self.camera is None or not self.camera.isOpened():
            self.stop_cloak_camera()
            return

        # Buffer flush: eski frame'leri at, en son frame'i al
        # Bu, OS seviyesindeki buffer birikimini önler
        self.camera.grab()  # 1. eski frame'i at
        self.camera.grab()  # 2. eski frame'i at
        ret, frame = self.camera.read()  # 3. en güncel frame'i oku
        if not ret:
            return

        frame = cv2.flip(frame, 1)  # Ayna efekti

        mode_text = self.tool_panel.widgets["cloak_bg_mode"].currentText()
        is_dynamic = "Dinamik" in mode_text
        mode_str = "dynamic" if is_dynamic else "static"

        # Efekt aktifse: görünmezlik uygula
        if self.cloak_effect_active and (is_dynamic or self.cloak_background is not None):
            color_bgr = self.tool_panel.cloak_color
            tol = self.tool_panel.widgets["cloak_tolerance"].value()
            result, new_mask, updated_dbg = self.processor.apply_invisibility_realtime(
                frame, self.cloak_background, color_bgr, tol,
                self.prev_cloak_mask, mode_str,
                dynamic_bg=self.dynamic_background,
                show_mask=self.show_mask_debug)
            self.prev_cloak_mask = new_mask
            self.dynamic_background = updated_dbg

            # Ekranda mod göstergesi (OSD)
            if not self.show_mask_debug:
                mode_label = "SABIT" if mode_str == "static" else "DİNAMİK"
                cv2.putText(result, f"Mod: {mode_label} | Tol: {tol}",
                           (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            self.canvas.show_image(result)
            self.current_img = result
        else:
            # Normal canlı yayın
            display = frame.copy()
            if self.cloak_picking_color:
                # Renk seçim modunda: hedef işareti göster
                cv2.putText(display, "CISMIN UZERINE TIKLAYIN",
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
                cv2.rectangle(display, (3, 3),
                             (frame.shape[1]-3, frame.shape[0]-3), (255, 0, 255), 3)
            self.canvas.show_image(display)
            self.current_img = frame

    def closeEvent(self, event):
        self.stop_cloak_camera()
        super().closeEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.camera is None and self.current_img is not None:
            show_original = hasattr(self, 'btn_compare') and self.btn_compare.isChecked()
            self.canvas.show_image(self.original_img if show_original else self.current_img)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)
    window = PhotoshopApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
