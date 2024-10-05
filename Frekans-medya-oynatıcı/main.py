import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QMessageBox, QSlider, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class MedyaSekmesi(QWidget):
    def __init__(self, dosya_adi):
        super().__init__()
        self.düzen = QVBoxLayout(self)
        self.oyuncu = QMediaPlayer()

        self.süre_label = QLabel("00:00 / 00:00", self)
        self.süre_label.setAlignment(Qt.AlignCenter)
        self.düzen.addWidget(self.süre_label)

        if self.resim_dosyasi_mi(dosya_adi):
            self.label = QLabel("Resim Yükleniyor...", self)
            self.label.setAlignment(Qt.AlignCenter)
            self.düzen.addWidget(self.label)
            self.resmi_yukle(dosya_adi)
        elif self.video_dosyasi_mi(dosya_adi):
            self.video_widget = QVideoWidget(self)
            self.düzen.addWidget(self.video_widget)
            self.medya_kontrollerini_kur()
            self.videoyu_yukle(dosya_adi)
        elif self.ses_dosyasi_mi(dosya_adi):
            self.setStyleSheet("background-color: black;")
            self.medya_kontrollerini_kur()
            self.sesi_yukle(dosya_adi)

    def medya_kontrollerini_kur(self):
        self.kontrol_düzeni = QHBoxLayout()

        self.oynat_butonu = QPushButton("Oynat")
        self.oynat_butonu.setStyleSheet("background-color: #6B6B6B; color: white;")
        self.oynat_butonu.clicked.connect(self.medya_oynat)
        self.kontrol_düzeni.addWidget(self.oynat_butonu)

        self.durdur_butonu = QPushButton("Durdur")
        self.durdur_butonu.setStyleSheet("background-color: #6B6B6B; color: white;")
        self.durdur_butonu.clicked.connect(self.medya_durdur)
        self.kontrol_düzeni.addWidget(self.durdur_butonu)

        self.dongu_butonu = QPushButton("Döngü")
        self.dongu_butonu.setCheckable(True)
        self.dongu_butonu.setStyleSheet("background-color: #6B6B6B; color: white;")
        self.dongu_butonu.clicked.connect(self.donguyu_ac_kapa)
        self.kontrol_düzeni.addWidget(self.dongu_butonu)

        self.seek_slayt = QSlider(Qt.Horizontal)
        self.seek_slayt.sliderMoved.connect(self.konumu_ayarla)
        self.kontrol_düzeni.addWidget(self.seek_slayt)

        self.düzen.addLayout(self.kontrol_düzeni)

        self.oyuncu.positionChanged.connect(self.konumu_guncelle)
        self.oyuncu.durationChanged.connect(self.sure_guncelle)
        self.oyuncu.mediaStatusChanged.connect(self.medya_durumunu_kontrol_et)

        self.dongu = False

    def resmi_yukle(self, dosya_adi):
        try:
            pixmap = QPixmap(dosya_adi)
            if pixmap.isNull():
                raise ValueError("Resim açılamadı.")
            self.label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.label.setText("")
        except Exception as e:
            QMessageBox.critical(self, "Hata", "Bu dosya desteklenmiyor: " + str(e))

    def videoyu_yukle(self, dosya_adi):
        self.oyuncu.setMedia(QMediaContent(QUrl.fromLocalFile(dosya_adi)))
        self.oyuncu.setVideoOutput(self.video_widget)
        self.oyuncu.play()

    def sesi_yukle(self, dosya_adi):
        self.oyuncu.setMedia(QMediaContent(QUrl.fromLocalFile(dosya_adi)))
        self.oyuncu.play()

    def medya_oynat(self):
        self.oyuncu.play()

    def medya_durdur(self):
        self.oyuncu.pause()

    def konumu_ayarla(self, konum):
        self.oyuncu.setPosition(konum)

    def konumu_guncelle(self, konum):
        self.seek_slayt.setValue(konum)
        self.süre_label.setText(self.zaman_formatla(konum) + " / " + self.zaman_formatla(self.oyuncu.duration()))

    def sure_guncelle(self, sure):
        self.seek_slayt.setRange(0, sure)

    def medya_durumunu_kontrol_et(self, durum):
        if durum == QMediaPlayer.EndOfMedia and self.dongu:
            self.oyuncu.setPosition(0)
            self.oyuncu.play()

    def donguyu_ac_kapa(self):
        self.dongu = not self.dongu

    def zaman_formatla(self, ms):
        saniye = ms // 1000
        dakika = saniye // 60
        saniye = saniye % 60
        return f"{dakika:02}:{saniye:02}"

    def resim_dosyasi_mi(self, dosya_adi):
        geçerli_uzantilar = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
        return any(dosya_adi.lower().endswith(uzanti) for uzanti in geçerli_uzantilar)

    def video_dosyasi_mi(self, dosya_adi):
        geçerli_uzantilar = [".mp4", ".avi", ".mov", ".mkv", ".flv"]
        return any(dosya_adi.lower().endswith(uzanti) for uzanti in geçerli_uzantilar)

    def ses_dosyasi_mi(self, dosya_adi):
        geçerli_uzantilar = [".mp3", ".wav", ".ogg", ".flac"]
        return any(dosya_adi.lower().endswith(uzanti) for uzanti in geçerli_uzantilar)

class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Medya Gösterici")

        self.sekmeler = QTabWidget()
        self.setCentralWidget(self.sekmeler)

        self.artı_label = QLabel("+", self)
        self.artı_label.setAlignment(Qt.AlignCenter)
        self.artı_label.setStyleSheet("font-size: 64px; color: gray;")
        self.sekmeler.addTab(self.artı_label, "Yeni Medya Yükle")

        self.sekmeler.setTabsClosable(True)
        self.sekmeler.tabCloseRequested.connect(self.sekme_kapat)

        self.resize(800, 600)

        self.setAcceptDrops(True)

    def sekme_kapat(self, indeks):
        if indeks > 0:
            medya_sekmesi = self.sekmeler.widget(indeks)
            medya_sekmesi.oyuncu.stop()
            self.sekmeler.removeTab(indeks)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        dosya_adi = event.mimeData().urls()[0].toLocalFile()
        if os.path.isfile(dosya_adi):
            self.sekme_ekle(dosya_adi)
        else:
            QMessageBox.warning(self, "Uyarı", "Bu dosya bir medya dosyası değil.")

    def sekme_ekle(self, dosya_adi):
        yeni_sekme = MedyaSekmesi(dosya_adi)
        self.sekmeler.addTab(yeni_sekme, os.path.basename(dosya_adi))

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self.sekmeler.currentIndex() == 0:
            dosya_adi, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "Medya Dosyaları (*.mp3 *.wav *.ogg *.flac *.mp4 *.avi *.mov *.mkv *.gif *.jpg *.jpeg *.png *.bmp)")
            if dosya_adi:
                self.sekme_ekle(dosya_adi)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec_())
