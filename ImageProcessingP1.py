# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 15:22:15 2019

@author: serdar
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from skimage import io, filters, img_as_ubyte, feature, exposure, transform, morphology
from skimage.color import rgb2gray, gray2rgb

import numpy as np

import qimage2ndarray

import matplotlib.pyplot as plt

from datetime import datetime

import sys

class Pencere(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.widget = MerkeziWidget()
        self.setCentralWidget(self.widget)
        self.setUI()
        self.resize(800,630)
    
    
    def setUI(self):
        self.ActionOlustur()
        self.MenuOlustur()
        
        self.setWindowTitle("Görüntü İşleme")
        self.show()
        
        
    def ActionOlustur(self):
        self.resimYukleAction = QAction("Aç", self, triggered=self.widget.dosyaAc)
        self.resimKaydetAction = QAction("Kaydet",self, triggered = self.widget.dosyaKaydet)
        self.islenmisiKullanAction = QAction("İşlenmiş resmi kullan", self, triggered=self.widget.kullanilacakResmiDegistir, checkable=True)
        
        
    def MenuOlustur(self):
        self.dosyaMenu = QMenu("Dosya",self)
        self.dosyaMenu.addAction(self.resimYukleAction)
        self.dosyaMenu.addAction(self.resimKaydetAction)
        
        self.tercihMenu = QMenu("Tercih", self)
        self.tercihMenu.addAction(self.islenmisiKullanAction)
        
        self.menuBar().addMenu(self.dosyaMenu)
        self.menuBar().addMenu(self.tercihMenu)
        
        
class MerkeziWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resimDosyaYolu = None
        self.acikResim = None
        self.islenmis = None
        
        self.islenmisiKullan = False
                
        self.setUI()
        
        
    def setUI(self):
        self.etiket = QLabel()
        pixmap = QPixmap()
        pix = pixmap.scaled(400, 600, Qt.KeepAspectRatio)
        self.etiket.setPixmap(pix)
        
        self.cozunurluk = QLabel()
        self.cozunurluk.setText("")
        self.cozunurluk.setMaximumHeight(10)
        
        resimAlani = QWidget(self)
        resimAlani.setMinimumWidth(400)
        resimAlani.setMinimumHeight(600)
        
        resimAlaniLayout = QVBoxLayout()
        resimAlaniLayout.addWidget(self.cozunurluk)
        resimAlaniLayout.addWidget(self.etiket)
        resimAlani.setLayout(resimAlaniLayout)
        
        islemAlani = QTabWidget(self)
        islemAlani.move(401,0)
        islemAlani.resize(400,600)
        
        
        self.filtreTab = QWidget()
        self.histogramTab = QWidget()
        self.uzaysalDonusumTab = QWidget()
        self.yogunlukDonusumuTab = QWidget()
        self.morfolojiTab = QWidget()
        
        islemAlani.addTab(self.filtreTab, "Filtre")
        islemAlani.addTab(self.histogramTab, "Histogram")
        islemAlani.addTab(self.uzaysalDonusumTab,"U. Dönüşüm")
        islemAlani.addTab(self.yogunlukDonusumuTab,"Y. Dönüşüm")
        islemAlani.addTab(self.morfolojiTab, "Morfoloji")
        islemAlani.setTabPosition(QTabWidget.East)
        
        
        self.filtreUI()
        self.histogramUI()
        self.uzaysalDonusumUI()
        self.yogunlukDonusumuUI()
        self.morfolojiUI()
    
        
    def dosyaAc(self):
        dosyaYolu = QFileDialog.getOpenFileName(self,"Dosya Seç", "", "Resim Dosyası (*.jpg *.png *jpeg *.xpm)")
        if dosyaYolu[0]:
            resim = io.imread(dosyaYolu[0])
            self.ekrandaGoster(resim)
           
            self.acikResim = io.imread(dosyaYolu[0])
            self.resimDosyaYolu = dosyaYolu[0]
        
        
            
    def dosyaKaydet(self):
        dosyaYolu = QFileDialog.getSaveFileName(self,"Kayıt Yeri Seç",str(datetime.timestamp(datetime.now())), "*.jpg *.png")
        print(dosyaYolu[0])
        if dosyaYolu[0]:
            io.imsave(dosyaYolu[0],self.islenmis)
            
    
    def kullanilacakResmiDegistir(self):
        self.islenmisiKullan = not self.islenmisiKullan
        
        if self.islenmisiKullan == False:
            self.acikResim = io.imread(self.resimDosyaYolu)
        
    
    def islenmisResmiAyarla(self, resim):
        if self.islenmisiKullan == True:
            self.acikResim = resim
            
        self.islenmis = resim
            
            
    def filtreUI(self):
        self.secim = QComboBox()
        self.secim.addItems(["Sobel","Hessian","Canny","Prewitt","Laplace","Sato","Unsharp mask","Threshold Niblack","Meijering","Threshold Sauvola"])
        
        uygulaButon = QPushButton("Uygula")
        uygulaButon.resize(80,30)
        uygulaButon.clicked.connect(self.filtreUygula)
        
        form = QFormLayout()
        form.addRow("Filtre Seçimi: ",self.secim)
        form.addRow(uygulaButon)
        self.filtreTab.setLayout(form)
        
        
    def histogramUI(self):
        self.histogramEtiket = QLabel()
        self.histogramEtiket.resize(200,200)
        pixmap = QPixmap()
        pix = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
        self.histogramEtiket.setPixmap(pix)
        
        histogramButon = QPushButton("Histogram Görüntüle")
        histogramButon.resize(80,30)
        histogramButon.clicked.connect(self.histogramGoruntule)
        
        esitleButon = QPushButton("Histogram Eşitle")
        esitleButon.resize(80,30)
        esitleButon.clicked.connect(self.histogramEsitle)
        
        form = QFormLayout()
        form.addRow(histogramButon)
        form.addRow(self.histogramEtiket)
        form.addRow(esitleButon)
        self.histogramTab.setLayout(form)
        
        
    def uzaysalDonusumUI(self):
        self.islemComboBox = QComboBox()
        self.islemComboBox.addItems(["Yeniden Boyutlandırma", "Döndürme", "Girdap", "Yeniden Ölçeklendirme","Kırpma"])
        self.islemComboBox.currentIndexChanged.connect(self.islemSecimiUygula)
        
        self.uzaysalDonusumStackedWidget = QStackedWidget()
        
        self.yenidenBoyutlandirmaWidget = QWidget()
        self.dondurmeWidget = QWidget()
        self.girdapWidget = QWidget()
        self.yenidenOlceklendirmeWidget = QWidget()
        self.kirpmaWidget = QWidget()
        
        self.yenidenBoyutlandirUI()
        self.dondurmeUI()
        self.girdapUI()
        self.yenidenOlceklendirmeUI()
        self.kirpmaUI()
        
        self.uzaysalDonusumStackedWidget.addWidget(self.yenidenBoyutlandirmaWidget)
        self.uzaysalDonusumStackedWidget.addWidget(self.dondurmeWidget)
        self.uzaysalDonusumStackedWidget.addWidget(self.girdapWidget)
        self.uzaysalDonusumStackedWidget.addWidget(self.yenidenOlceklendirmeWidget)
        self.uzaysalDonusumStackedWidget.addWidget(self.kirpmaWidget)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        
        form = QFormLayout()
        form.addRow("İşlem Seçimi: ",self.islemComboBox)
        form.addRow(line)
        form.addRow(self.uzaysalDonusumStackedWidget)
        self.uzaysalDonusumTab.setLayout(form)
        
        
    def yogunlukDonusumuUI(self):
        self.yogunlukIslemComboBox = QComboBox()
        self.yogunlukIslemComboBox.addItems(["Gamma","Log","Sigmoid","Equalize Adapthist"])
        self.yogunlukIslemComboBox.currentIndexChanged.connect(self.yogunlukIslemSecimiUygula)
        
        self.yogunlukDonusumuStackedWidget = QStackedWidget()
        
        self.gammaWidget = QWidget()
        self.logWidget = QWidget()
        self.sigmoidWidget = QWidget()
        self.equalizeAdapthistWidget = QWidget()
        
        self.gammaUI()
        self.logUI()
        self.sigmoidUI()
        self.equalizeAdapthistUI()
        
        self.yogunlukDonusumuStackedWidget.addWidget(self.gammaWidget)
        self.yogunlukDonusumuStackedWidget.addWidget(self.logWidget)
        self.yogunlukDonusumuStackedWidget.addWidget(self.sigmoidWidget)
        self.yogunlukDonusumuStackedWidget.addWidget(self.equalizeAdapthistWidget)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        
        form = QFormLayout()
        form.addRow("İşlem Seçimi: ",self.yogunlukIslemComboBox)
        form.addRow(line)
        form.addRow(self.yogunlukDonusumuStackedWidget)
        self.yogunlukDonusumuTab.setLayout(form)
        
    
    def morfolojiUI(self):
        self.morfolojikIslemComboBox = QComboBox()
        self.morfolojikIslemComboBox.addItems(["Erosion","Dilation"])
        self.morfolojikIslemComboBox.currentIndexChanged.connect(self.morfolojikIslemUygula)
        
        self.morfolojiStackedWidget = QStackedWidget()
        
        self.erosionWidget = QWidget()
        self.dilationWidget = QWidget()
        
        self.erosionUI()
        self.dilationUI()
        
        self.morfolojiStackedWidget.addWidget(self.erosionWidget)
        self.morfolojiStackedWidget.addWidget(self.dilationWidget)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        
        form = QFormLayout()
        form.addRow("Morfolojik İşlem: ", self.morfolojikIslemComboBox)
        form.addRow(line)
        form.addRow(self.morfolojiStackedWidget)
        self.morfolojiTab.setLayout(form)
        
        
    def ekrandaGoster(self,gosterilecekResim):
        width = gosterilecekResim.shape[1]
        height = gosterilecekResim.shape[0]
        
        qImg=None
        
        if len(gosterilecekResim.shape) == 3:

            if not gosterilecekResim.dtype == 'uint8':
                gosterilecekResim = img_as_ubyte(gosterilecekResim)
                
            qImg=qimage2ndarray.array2qimage(gosterilecekResim)
            
            
        elif len(gosterilecekResim.shape) == 2:
            if np.min(gosterilecekResim) < 0:
                gosterilecekResim = (gosterilecekResim - np.min(gosterilecekResim))/np.ptp(gosterilecekResim)
            
            if np.max(gosterilecekResim) <= 1:
                gosterilecekResim = img_as_ubyte(gosterilecekResim)
                
            qImg=qimage2ndarray.gray2qimage(gosterilecekResim)
        
        pixmap = QPixmap(qImg)
        pix = pixmap.scaled(380, 600, Qt.KeepAspectRatio)
        self.etiket.setPixmap(pix)
        
        cozString = str("Çözünürlük: {}x{}".format(width,height))
        
        self.cozunurluk.setText(cozString)
    
###############################################################################
#FİLTRE ALANI        
    
    def filtreUygula(self):
        resim = self.acikResim
        
        #filtreler için 2d arraya dönüştürülmesi
        gri = rgb2gray(resim)
        
        index = self.secim.currentIndex()
        
        filtrelenmis = None
        if index == 0:
            filtrelenmis = filters.sobel(gri)
                   
        elif index == 1:
            filtrelenmis = filters.hessian(gri)
            
        elif index == 2:
            filtrelenmis = feature.canny(gri)
            
        elif index == 3:
            filtrelenmis = filters.prewitt(gri)
            
        elif index == 4:
            filtrelenmis = filters.laplace(gri)
            
        elif index == 5:
            filtrelenmis = filters.sato(gri)
            
        elif index==6:
            filtrelenmis = filters.unsharp_mask(resim,radius= 2, amount=2)
            
        elif index==7:
            filtrelenmis = filters.threshold_niblack(gri)
            
        elif index==8:
            filtrelenmis = filters.meijering(gri)
            
        elif index==9:
            filtrelenmis = filters.threshold_sauvola(gri)
            
        self.islenmisResmiAyarla(filtrelenmis)
        self.ekrandaGoster(filtrelenmis)
            
###############################################################################
#HİSTOGRAM ALANI 
            
    def histogramGoruntule(self):
        #resmin np arraya dönüştürülmesi
        resim = self.acikResim
        
        #histogramın oluşturulması
        hist, hist_centers = exposure.histogram(resim)
        fig, ax = plt.subplots()
        ax.plot(hist_centers,hist,lw=2)
        ax.set_title('Histogram')
        fig.canvas.draw()
        
        #oluşturulan histogramın resime dönüştürülmesi(np array olarak)
        ncols, nrows = fig.canvas.get_width_height()
        X = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8).reshape(nrows, ncols, 3)
        
        #histogram resminin histogram tabında gösterilmesi
        height, width, channel = X.shape
        bytesPerLine = 3 * width
        qImg = QImage(X.data, width, height, bytesPerLine, QImage.Format_RGB888)
        
        pixmap = QPixmap(qImg)
        pix = pixmap.scaled(380, 380, Qt.KeepAspectRatio)
        self.histogramEtiket.setPixmap(pix)
        
        
    def histogramEsitle(self):
        #resmin np arraya dönüştürülmesi
        resim = self.acikResim
        
        #histogramın eşitlenmesi
        esitlenmis = exposure.equalize_hist(resim)
        
        self.islenmisResmiAyarla(esitlenmis)
        self.ekrandaGoster(esitlenmis)

###############################################################################
#UZAYSAL DÖNÜŞÜM ALANI
    def islemSecimiUygula(self):
        index = self.islemComboBox.currentIndex()
        self.uzaysalDonusumStackedWidget.setCurrentIndex(index)
            
        
    def yenidenBoyutlandir(self):
        genislik = int(self.genislikSatiri.text())
        yukseklik = int(self.yukseklikSatiri.text())
        #resmin np arraya dönüştürülmesi
        resim = self.acikResim
        
        boyutlandirilmis = transform.resize(resim,(yukseklik,genislik))
        
        self.islenmisResmiAyarla(boyutlandirilmis)
        self.ekrandaGoster(boyutlandirilmis)
        
        
    def yenidenBoyutlandirUI(self):
        self.genislikSatiri = QLineEdit()
        self.yukseklikSatiri = QLineEdit()
        
        boyutlandirmaButon = QPushButton("Yeniden Boyutlandır")
        boyutlandirmaButon.clicked.connect(self.yenidenBoyutlandir)
        
        form = QFormLayout()
        form.addRow("Genişlik:",self.genislikSatiri)
        form.addRow("Yükseklik:",self.yukseklikSatiri)
        form.addRow(boyutlandirmaButon)
        self.yenidenBoyutlandirmaWidget.setLayout(form)
        
        
    def solaDondur(self):
        aci = int(self.dondurmeAcisi.text())
        
        resim = self.acikResim
        
        dondurulmus = transform.rotate(resim,aci)
        
        self.islenmisResmiAyarla(dondurulmus)
        self.ekrandaGoster(dondurulmus)
        
        
    def sagaDondur(self):
        aci = int(self.dondurmeAcisi.text())
        
        resim = self.acikResim
        
        dondurulmus = transform.rotate(resim,360 - aci)
        
        self.islenmisResmiAyarla(dondurulmus)
        self.ekrandaGoster(dondurulmus)
        
        
    def dondurmeUI(self):
        self.dondurmeAcisi = QLineEdit()
        self.dondurmeAcisi.setText("0")
        
        boyutlandirmaButonSol = QPushButton("Sola Döndür")
        boyutlandirmaButonSol.clicked.connect(self.solaDondur)
        
        boyutlandirmaButonSag = QPushButton("Sağa Döndür")
        boyutlandirmaButonSag.clicked.connect(self.sagaDondur)
        
        dondurmeButonWidget = QWidget()
        
        dondurmeButonLayout = QHBoxLayout()
        dondurmeButonLayout.addWidget(boyutlandirmaButonSol)
        dondurmeButonLayout.addWidget(boyutlandirmaButonSag)
        dondurmeButonWidget.setLayout(dondurmeButonLayout)
        
        form = QFormLayout()
        form.addRow("Döndürme Açısı:",self.dondurmeAcisi)
        form.addRow(dondurmeButonWidget)
        self.dondurmeWidget.setLayout(form)
        
        
    def girdapUygula(self):
        resim = self.acikResim
        
        yaricap = int(self.yaricapInput.text())
        guc = float(self.gucInput.text())
        
        girdapUygulanmis = transform.swirl(resim, radius = yaricap, strength = guc)
        
        self.islenmisResmiAyarla(girdapUygulanmis)
        self.ekrandaGoster(girdapUygulanmis)
        
        
    def girdapUI(self):
        self.yaricapInput = QLineEdit()
        self.yaricapInput.setText("100")
        
        self.gucInput = QLineEdit()
        self.gucInput.setText("1.0")
        
        
        girdapButon = QPushButton("Girdap")
        girdapButon.clicked.connect(self.girdapUygula)
        
        form = QFormLayout()
        form.addRow("Yarıçap:", self.yaricapInput)
        form.addRow("Güç(float):", self.gucInput)
        form.addRow(girdapButon)
        self.girdapWidget.setLayout(form)
        
    
    def olceklendir(self):
        resim = self.acikResim
        
        olcekEn = float(self.olcekEnInput.text())
        olcekBoy = float(self.olcekBoyInput.text())
        
        olceklendirilmis = transform.rescale(resim,(olcekBoy,olcekEn), multichannel = True)
        
        self.islenmisResmiAyarla(olceklendirilmis)
        self.ekrandaGoster(olceklendirilmis)
    
        
    def yenidenOlceklendirmeUI(self):
        self.olcekEnInput = QLineEdit()
        self.olcekEnInput.setText("1.0")
        
        self.olcekBoyInput = QLineEdit()
        self.olcekBoyInput.setText("1.0")
        
        olceklendirmeButon = QPushButton("Ölçeklendir")
        olceklendirmeButon.clicked.connect(self.olceklendir)
        
        form = QFormLayout()
        form.addRow("En Ölçek:",self.olcekEnInput)
        form.addRow("Boy Ölçek:",self.olcekBoyInput)
        form.addRow(olceklendirmeButon)
        self.yenidenOlceklendirmeWidget.setLayout(form)
        
    
    def kirp(self):
        resim = self.acikResim
        x1 = int(self.x1Input.text())
        y1 = int(self.y1Input.text())
        x2 = int(self.x2Input.text())
        y2 = int(self.y2Input.text())
        
        kirpilmis = np.copy(resim[y1:y2,x1:x2])
        
        self.islenmisResmiAyarla(kirpilmis)
        self.ekrandaGoster(kirpilmis)
        
        
    def kirpmaUI(self):
        self.x1Input = QLineEdit()      
        self.y1Input = QLineEdit()
        
        self.x2Input = QLineEdit()     
        self.y2Input = QLineEdit()
        
        solUst = QWidget()
        
        solUstLayout = QHBoxLayout()
        solUstLayout.addWidget(self.x1Input)
        solUstLayout.addWidget(self.y1Input)
        solUst.setLayout(solUstLayout)
        
        sagAlt = QWidget()
        
        sagAltLayout = QHBoxLayout()
        sagAltLayout.addWidget(self.x2Input)
        sagAltLayout.addWidget(self.y2Input)
        sagAlt.setLayout(sagAltLayout)
        
        kirpmaButon = QPushButton("Kırp")
        kirpmaButon.clicked.connect(self.kirp)
        
        form = QFormLayout()
        form.addRow("Sol üst(x,y): ",solUst)
        form.addRow("Sağ Alt(x,y): ",sagAlt)
        form.addRow(kirpmaButon)
        self.kirpmaWidget.setLayout(form)
        
        
###############################################################################
#YOĞUNLUK DÖNÜŞÜMÜ ALANI
        
    def yogunlukIslemSecimiUygula(self):
        index = self.yogunlukIslemComboBox.currentIndex()
        self.yogunlukDonusumuStackedWidget.setCurrentIndex(index)
        
    
    def gammaUygula(self):
        resim = self.acikResim
        
        gammaDegeri = float(self.gammaLineEdit.text())
        gainDegeri = float(self.gammaGainLineEdit.text())
        
        gammaUygulanmis = exposure.adjust_gamma(resim,gammaDegeri, gainDegeri)
        
        self.islenmisResmiAyarla(gammaUygulanmis)
        
        self.ekrandaGoster(gammaUygulanmis)
        
    
    def gammaUI(self):
        self.gammaLineEdit = QLineEdit()
        self.gammaLineEdit.setText("1.0")
        
        self.gammaGainLineEdit = QLineEdit()
        self.gammaGainLineEdit.setText("1.0")
        
        gammaButon = QPushButton("Uygula")
        gammaButon.clicked.connect(self.gammaUygula)
        
        form = QFormLayout()
        form.addRow("Gamma: ",self.gammaLineEdit)
        form.addRow("Gain: ",self.gammaGainLineEdit)
        form.addRow(gammaButon)
        self.gammaWidget.setLayout(form)
        
        
    def logUygula(self):
        resim = self.acikResim
        
        gainDegeri = float(self.logGainLineEdit.text())
        inverse = False
        
        if self.inverseCheckBox.isChecked():
            inverse = True
        
        logUygulanmis = exposure.adjust_log(resim,gainDegeri, inverse)
        
        self.islenmisResmiAyarla(logUygulanmis)
        
        self.ekrandaGoster(logUygulanmis)
        
        
    def logUI(self):
        self.logGainLineEdit = QLineEdit()
        self.logGainLineEdit.setText("1.0")
        
        self.inverseCheckBox = QCheckBox()
        
        logButon = QPushButton("Uygula")
        logButon.clicked.connect(self.logUygula)
        
        form = QFormLayout()
        form.addRow("Gain: ", self.logGainLineEdit)
        form.addRow("Inverse: ", self.inverseCheckBox)
        form.addRow(logButon)
        self.logWidget.setLayout(form)
        
        
    def sigmoidUygula(self):
        resim = self.acikResim
        
        cutoffDegeri = float(self.sigmoidCutoffLineEdit.text())
        gainDegeri =float(self.sigmoidGainLineEdit.text())
        inverse = False
        
        if self.sigmoidInverseCheckBox.isChecked():
            inverse = True
        
        sigmoidUygulanmis = exposure.adjust_sigmoid(resim, cutoffDegeri, gainDegeri, inverse)
        
        self.islenmisResmiAyarla(sigmoidUygulanmis)
        
        self.ekrandaGoster(sigmoidUygulanmis)
        
        
    def sigmoidUI(self):
        self.sigmoidCutoffLineEdit = QLineEdit()
        self.sigmoidCutoffLineEdit.setText("0.5")
        
        self.sigmoidGainLineEdit = QLineEdit()
        self.sigmoidGainLineEdit.setText("10.0")
        
        self.sigmoidInverseCheckBox = QCheckBox()
        
        sigmoidButon = QPushButton("Uygula")
        sigmoidButon.clicked.connect(self.sigmoidUygula)
        
        form = QFormLayout()
        form.addRow("Cutoff: ", self.sigmoidCutoffLineEdit)
        form.addRow("Gain: ", self.sigmoidGainLineEdit)
        form.addRow("Inverse: ", self.sigmoidInverseCheckBox)
        form.addRow(sigmoidButon)
        self.sigmoidWidget.setLayout(form)
        
        
    def equalizeAdapthistUygula(self):
        resim = self.acikResim
        
        kernelSizeDegeri = None
        if not self.kernelSizeLineEdit.text() == "" :
            kernelSizeDegeri = float(self.kernelSizeLineEdit.text())
        clipLimitDegeri = float(self.clipLimitLineEdit.text())
        nbinsDegeri = int(self.nbinsLineEdit.text())
        
        equalizeAdapthistUygulanmis = exposure.equalize_adapthist(resim, kernelSizeDegeri, clipLimitDegeri, nbinsDegeri)
        
        self.islenmisResmiAyarla(equalizeAdapthistUygulanmis)
        
        self.ekrandaGoster(equalizeAdapthistUygulanmis)
        
    
    def equalizeAdapthistUI(self):
        self.kernelSizeLineEdit = QLineEdit()
        
        self.clipLimitLineEdit = QLineEdit()
        self.clipLimitLineEdit.setText("0.01")
        
        self.nbinsLineEdit = QLineEdit()
        self.nbinsLineEdit.setText("256")
        
        equalizeAdapthistButton = QPushButton("Uygula")
        equalizeAdapthistButton.clicked.connect(self.equalizeAdapthistUygula)
        
        form = QFormLayout()
        form.addRow("Kernel Size: ", self.kernelSizeLineEdit)
        form.addRow("Clip Limit: ", self.clipLimitLineEdit)
        form.addRow("Nbins: ", self.nbinsLineEdit)
        form.addRow(equalizeAdapthistButton)
        self.equalizeAdapthistWidget.setLayout(form)
        
        
###############################################################################
#MORFOLOJİK İŞLEM ALANI
        
        
    def morfolojikIslemUygula(self):
        index = self.morfolojikIslemComboBox.currentIndex()
        self.morfolojiStackedWidget.setCurrentIndex(index)
    
    
    def erosionUygula(self):
        resim = self.acikResim
        
        squareWidthDegeri = int(self.erosionSquareWidthLineEdit.text())
        
        erosionUygulanmis = morphology.erosion(resim, morphology.square(squareWidthDegeri))
        
        self.islenmisResmiAyarla(erosionUygulanmis)
        
        self.ekrandaGoster(erosionUygulanmis)
    
    def erosionUI(self):
        self.erosionSquareWidthLineEdit = QLineEdit()
        self.erosionSquareWidthLineEdit.setText("10")
        
        self.erosionUygulaButon = QPushButton("Uygula")
        self.erosionUygulaButon.clicked.connect(self.erosionUygula)
        
        form = QFormLayout()
        form.addRow("Square Width :", self.erosionSquareWidthLineEdit)
        form.addRow(self.erosionUygulaButon)
        self.erosionWidget.setLayout(form)
        
        
    def dilationUygula(self):
        resim = self.acikResim
        
        squareWidthDegeri = int(self.dilationSquareWidthLineEdit.text())
        
        dilationUygulanmis = morphology.dilation(resim, morphology.square(squareWidthDegeri))
        
        self.islenmisResmiAyarla(dilationUygulanmis)
        
        self.ekrandaGoster(dilationUygulanmis)
    
    
    def dilationUI(self):
        self.dilationSquareWidthLineEdit = QLineEdit()
        self.dilationSquareWidthLineEdit.setText("5")
        
        self.dilationUygulaButon = QPushButton("Uygula")
        self.dilationUygulaButon.clicked.connect(self.dilationUygula)
        
        form = QFormLayout()
        form.addRow("Square Width :", self.dilationSquareWidthLineEdit)
        form.addRow(self.dilationUygulaButon)
        self.dilationWidget.setLayout(form)
        
    
if __name__ == "__main__":
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    pencere = Pencere()
    sys.exit(app.exec())
