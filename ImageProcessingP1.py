# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 15:22:15 2019

@author: serdar
"""

#Serdar Dal - 05160000406

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from skimage import io, filters, img_as_ubyte, feature, exposure, transform, morphology, util
from skimage.color import rgb2gray

import numpy as np

import qimage2ndarray

import matplotlib.pyplot as plt

from datetime import datetime

import cv2

import sys

import os

class Pencere(QMainWindow):
    
    #ana pencerenin başlangıç ayarlaması yapılması
    def __init__(self):
        super().__init__()
        
        self.setUI()
        
    #ana pencerenin görsel ayarlanması
    def setUI(self):
        self.widget = MerkeziWidget()
        self.setCentralWidget(self.widget)
        
        self.ActionOlustur()
        self.MenuOlustur()
        
        self.resize(800,630)
        
        self.setWindowTitle("Görüntü İşleme")
        self.show()
        
    #menudeki butonların actionlarının oluşturulması
    def ActionOlustur(self):
        self.resimYukleAction = QAction("Aç", self, triggered=self.widget.dosyaAc)
        self.resimKaydetAction = QAction("Kaydet",self, triggered = self.widget.dosyaKaydet)
        
    #menu düzenlenmesi
    def MenuOlustur(self):
        self.dosyaMenu = QMenu("Dosya",self)
        self.dosyaMenu.addAction(self.resimYukleAction)
        self.dosyaMenu.addAction(self.resimKaydetAction)
         
        self.menuBar().addMenu(self.dosyaMenu)
        
#ana pencere içerisindeki merkezi widget classı
class MerkeziWidget(QWidget):
    #merkezi widget başlangıç ayarlaması
    def __init__(self):
        super().__init__()
        self.resimDosyaYolu = None
        self.orjinalResim = None
        self.acikResim = None
        self.islenmis = None
        self.videoDosyaYolu = None
        
        self.setUI()
        
    #merkezi widget görsel arayüz ayarlanmsaı
    def setUI(self):
        #resim bölümünün ayarlanması
        self.etiket = QLabel()
        
        self.cozunurluk = QLabel("Çözünürlük:")
        self.cozunurluk.setMaximumHeight(15)
        
        orjinaliGosterButon = QPushButton("Orjinali Göster")
        orjinaliGosterButon.setMinimumWidth(150)
        orjinaliGosterButon.pressed.connect(self.orjinalResmiGoster)
        orjinaliGosterButon.released.connect(self.islenmisResmiGoster)
        
        degisiklikleriKaydetButon = QPushButton("Değişiklikleri Onayla")
        degisiklikleriKaydetButon.setMinimumWidth(150)
        degisiklikleriKaydetButon.clicked.connect(self.degisiklikleriOnayla)
        
        butonWidget = QWidget()
        butonWidget.setMaximumHeight(30)
        
        butonLayout = QHBoxLayout()
        butonLayout.setContentsMargins(0,0,0,0)
        butonLayout.addWidget(orjinaliGosterButon)
        butonLayout.addWidget(degisiklikleriKaydetButon)
        butonLayout.addStretch(1)
        butonWidget.setLayout(butonLayout)
        
        resimAlani = QWidget(self)
        resimAlani.setMinimumWidth(400)
        resimAlani.setMinimumHeight(600)
        
        resimAlaniLayout = QVBoxLayout()
        resimAlaniLayout.setContentsMargins(0,0,0,0)
        resimAlaniLayout.addWidget(self.cozunurluk)
        resimAlaniLayout.addWidget(butonWidget)
        resimAlaniLayout.addWidget(self.etiket)
        resimAlani.setLayout(resimAlaniLayout)
        
        #işlem bölümünün ayarlanması
        islemAlani = QTabWidget(self)
        islemAlani.setFixedWidth(400)
        
        
        self.filtreTab = QWidget()
        self.histogramTab = QWidget()
        self.uzaysalDonusumTab = QWidget()
        self.yogunlukDonusumuTab = QWidget()
        self.morfolojiTab = QWidget()
        self.videoIslemeTab = QWidget()
        
        islemAlani.addTab(self.filtreTab, "Filtre")
        islemAlani.addTab(self.histogramTab, "Histogram")
        islemAlani.addTab(self.uzaysalDonusumTab,"U. Dönüşüm")
        islemAlani.addTab(self.yogunlukDonusumuTab,"Y. Dönüşüm")
        islemAlani.addTab(self.morfolojiTab, "Morfoloji")
        islemAlani.addTab(self.videoIslemeTab, "Video İşleme")
        islemAlani.setTabPosition(QTabWidget.East)
        
        
        self.filtreUI()
        self.histogramUI()
        self.uzaysalDonusumUI()
        self.yogunlukDonusumuUI()
        self.morfolojiUI()
        self.videoIslemeUI()
        
        layout = QHBoxLayout()
        layout.addWidget(resimAlani)
        layout.addWidget(islemAlani)
        self.setLayout(layout)
        
    
    #resim seçme ve gerekli değişkenlerin ayarlanması
    def dosyaAc(self):
        dosyaYolu = QFileDialog.getOpenFileName(self,"Dosya Seç", "", "Resim Dosyası (*.jpg *.png *jpeg *.xpm *tiff)")
        if dosyaYolu[0]:
            resim = io.imread(dosyaYolu[0])
            self.ekrandaGoster(resim)
           
            self.acikResim = io.imread(dosyaYolu[0])
            self.resimDosyaYolu = dosyaYolu[0]
            self.orjinalResim = self.acikResim
            self.islenmis = self.acikResim
        
        
    #timestamp ile dosya kaydedilmesi
    def dosyaKaydet(self):
        dosyaYolu = QFileDialog.getSaveFileName(self,"Kayıt Yeri Seç",str(datetime.timestamp(datetime.now())), "*.jpg *.png")
        print(dosyaYolu[0])
        if dosyaYolu[0]:
            io.imsave(dosyaYolu[0],self.islenmis)
        
    #başlangıçta açılan resim ile işlenmiş resim arasında tercihin yapılması
    def islenmisResmiAyarla(self, resim):          
        self.islenmis = resim
        
    
    def orjinalResmiGoster(self):
        self.ekrandaGoster(self.orjinalResim)
        
    
    def islenmisResmiGoster(self):
        self.ekrandaGoster(self.islenmis)
        
        
    def degisiklikleriOnayla(self):
        self.acikResim = self.islenmis
    
            
    #filtre sekmesinin görsel ayarlanması       
    def filtreUI(self):
        self.secim = QComboBox()
        self.secim.addItems(["Sobel","Hessian","Canny","Prewitt","Laplace","Sato","Unsharp mask","Threshold Niblack","Meijering","Threshold Sauvola","Invert","Threshold Otsu"])
        
        uygulaButon = QPushButton("Uygula")
        uygulaButon.resize(80,30)
        uygulaButon.clicked.connect(self.filtreUygula)
        
        form = QFormLayout()
        form.addRow("Filtre Seçimi: ",self.secim)
        form.addRow(uygulaButon)
        self.filtreTab.setLayout(form)
        
    #histogram sekmesinin görsel ayarlanması   
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
        
    #uzaysal dönüşüm sekmesinin görsel ayarlanması    
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
        
    #yoğunluk dönüşümü sekmesinin görsel ayarlanması    
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
        
    #morfoloji sekmesinin görsel ayarlanması
    def morfolojiUI(self):
        self.morfolojikIslemComboBox = QComboBox()
        self.morfolojikIslemComboBox.addItems(["Erosion","Dilation","Opening","Closing","White Tophat","BlackTophat","Skeletonize","Thin","Remove Small Objects","Medial Axis"])
        self.morfolojikIslemComboBox.currentIndexChanged.connect(self.morfolojikIslemUygula)
        
        self.morfolojiStackedWidget = QStackedWidget()
        
        self.squareWidthIslemlerWidget = QWidget()
        self.skeletonizeWidget= QWidget()
        self.thinWidget = QWidget()
        self.removeSmallObjectsWidget = QWidget()
        self.medialAxisWidget = QWidget()
        
        self.morfolojiSquareWidthIslemlerUI()
        self.skeletonizeUI()
        self.thinUI()
        self.removeSmallObjectsUI()
        self.medialAxisUI()

        self.morfolojiStackedWidget.addWidget(self.squareWidthIslemlerWidget)
        self.morfolojiStackedWidget.addWidget(self.skeletonizeWidget)
        self.morfolojiStackedWidget.addWidget(self.thinWidget)
        self.morfolojiStackedWidget.addWidget(self.removeSmallObjectsWidget)
        self.morfolojiStackedWidget.addWidget(self.medialAxisWidget)
             
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        
        form = QFormLayout()
        form.addRow("Morfolojik İşlem: ", self.morfolojikIslemComboBox)
        form.addRow(line)
        form.addRow(self.morfolojiStackedWidget)
        self.morfolojiTab.setLayout(form)
        
    #video işleme sekmesinin görsel ayarlanması    
    def videoIslemeUI(self):
        islemIsmiLabel = QLabel("Canny Kenar Belirleme")
        islemIsmiLabel.setStyleSheet("font:15pt;" "font-weight:bold;")
        
        self.videoAdiLabel = QLabel()
        
        videoAcButon = QPushButton("Video Seç")
        videoAcButon.clicked.connect(self.videoSec)
        
        izleButon = QPushButton("İzle (Çıkış: 'q')")
        izleButon.clicked.connect(self.islenmisVideoIzle)
        
        videoKaydetButon = QPushButton("Videoyu Kaydet")
        videoKaydetButon.clicked.connect(self.islenmisVideoKaydet)
        
        self.kayitDurumuLabel = QLabel()
        
        form = QFormLayout()
        form.addRow(islemIsmiLabel)
        form.addRow("Video Adı: ", self.videoAdiLabel)
        form.addRow(videoAcButon)
        form.addRow(izleButon)
        form.addRow(videoKaydetButon)
        form.addRow(self.kayitDurumuLabel)
        self.videoIslemeTab.setLayout(form)
    
        
    #fonksiyona verilen numpy arrayinin QImage tipine çevirilip ekranda gösterilmesi    
    def ekrandaGoster(self,gosterilecekResim):
        width = gosterilecekResim.shape[1]
        height = gosterilecekResim.shape[0]
        
        qImg=None
        
        #rgb resimlerin çevirilmesi
        if len(gosterilecekResim.shape) == 3:
                
            qImg=qimage2ndarray.array2qimage(gosterilecekResim, normalize=True)
            
        #gri tonlamalı ve siyah beyaz resimlerin çevirilmesi    
        elif len(gosterilecekResim.shape) == 2:
            #arrayde 0-1 aralığındaki 2d resimler QImage'e çevirilirken 0-1 arasına normalize edilir
            if np.min(gosterilecekResim) >= 0 and np.max(gosterilecekResim) <=1 :
                
                qImg=qimage2ndarray.gray2qimage(gosterilecekResim, normalize=(0,1))
                
            else:
                
                qImg=qimage2ndarray.gray2qimage(gosterilecekResim, normalize=True)
                
        #resmin label içerisine yerleştirilmesi ve çözünürlük bilgisinin gösterilmesi
        pixmap = QPixmap(qImg)
        pix = pixmap.scaled(self.etiket.size(), Qt.KeepAspectRatio)
        self.etiket.setPixmap(pix)
        
        cozString = str("Çözünürlük: {}x{}".format(width,height))
        
        self.cozunurluk.setText(cozString)
    
###############################################################################
#FİLTRE ALANI        
    #seçilen filtrenin uygulanıp ekranda gösterilmesini sağlayan fonksiyon
    def filtreUygula(self):
        resim = self.acikResim
        
        #filtreler için 2d arraya dönüştürülmesi
        gri = rgb2gray(resim)
        
        index = self.secim.currentIndex()
        
        filtrelenmis = None
        #sobel filtresi
        if index == 0:
            filtrelenmis = filters.sobel(gri)
        #hessian filtresi           
        elif index == 1:
            filtrelenmis = filters.hessian(gri)
        #canny filtresi    
        elif index == 2:
            filtrelenmis = feature.canny(gri).astype(int)
        #prewitt filtresi    
        elif index == 3:
            filtrelenmis = filters.prewitt(gri)
        #laplace filtresi    
        elif index == 4:
            filtrelenmis = filters.laplace(gri)
        #sato filtresi    
        elif index == 5:
            filtrelenmis = filters.sato(gri)
        #unsharp mask filtresi    
        elif index==6:
            filtrelenmis = filters.unsharp_mask(resim,radius= 2, amount=2)
        #niblack filtresi    
        elif index==7:
            filtrelenmis = filters.threshold_niblack(gri)
        #meijering filtresi    
        elif index==8:
            filtrelenmis = filters.meijering(gri)
        #threshold sauvola filtresi    
        elif index==9:
            filtrelenmis = filters.threshold_sauvola(gri)
        #invert filtresi 
        elif index==10:
            filtrelenmis = util.invert(gri)
        #otsu'nun threshold değerine göre siyah beyaz ayırma filtresi    
        elif index == 11:
            threshold = filters.threshold_otsu(gri)
            filtrelenmis = gri >= threshold
            filtrelenmis = filtrelenmis.astype(int)
            
        self.islenmisResmiAyarla(filtrelenmis)
        self.ekrandaGoster(filtrelenmis)
            
###############################################################################
#HİSTOGRAM ALANI 
    #resime ait histogramın oluşturulup ilgili sekmede görüntülenmesi        
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
        
    #histogramın eşitlenmesi    
    def histogramEsitle(self):
        #resmin np arraya dönüştürülmesi
        resim = self.acikResim
        
        #histogramın eşitlenmesi
        esitlenmis = exposure.equalize_hist(resim)
        
        self.islenmisResmiAyarla(esitlenmis)
        self.ekrandaGoster(esitlenmis)

###############################################################################
#UZAYSAL DÖNÜŞÜM ALANI
    #comboboxtan seçilen işlemin ekrana getirilmesi
    def islemSecimiUygula(self):
        index = self.islemComboBox.currentIndex()
        self.uzaysalDonusumStackedWidget.setCurrentIndex(index)
            
    #yeniden boyutlandırma işleminin uygulanması    
    def yenidenBoyutlandir(self):
        genislik = int(self.genislikSatiri.text())
        yukseklik = int(self.yukseklikSatiri.text())
        #resmin np arraya dönüştürülmesi
        resim = self.acikResim
        
        boyutlandirilmis = transform.resize(resim,(yukseklik,genislik))
        
        self.islenmisResmiAyarla(boyutlandirilmis)
        self.ekrandaGoster(boyutlandirilmis)
        
    #yeniden boyutlandırma görsel arayüzünün ayarlanması   
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
        
    #resmi sola döndürme    
    def solaDondur(self):
        aci = int(self.dondurmeAcisi.text())
        
        resim = self.acikResim
        
        dondurulmus = transform.rotate(resim,aci)
        
        self.islenmisResmiAyarla(dondurulmus)
        self.ekrandaGoster(dondurulmus)
        
    #resmi sağa döndürme   
    def sagaDondur(self):
        aci = int(self.dondurmeAcisi.text())
        
        resim = self.acikResim
        
        dondurulmus = transform.rotate(resim,360 - aci)
        
        self.islenmisResmiAyarla(dondurulmus)
        self.ekrandaGoster(dondurulmus)
        
    #resim döndürme ekranının görsel ayarlanması    
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
        
    #girdap efektinin uygulanması    
    def girdapUygula(self):
        resim = self.acikResim
        
        yaricap = int(self.yaricapInput.text())
        guc = float(self.gucInput.text())
        
        girdapUygulanmis = transform.swirl(resim, radius = yaricap, strength = guc)
        
        self.islenmisResmiAyarla(girdapUygulanmis)
        self.ekrandaGoster(girdapUygulanmis)
        
    #girdap görsel arayüzünün ayarlanması    
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
        
    #resime ölçeklendirme uygulanması
    def olceklendir(self):
        resim = self.acikResim
        
        olcekEn = float(self.olcekEnInput.text())
        olcekBoy = float(self.olcekBoyInput.text())
        
        olceklendirilmis = transform.rescale(resim,(olcekBoy,olcekEn), multichannel = True)
        
        self.islenmisResmiAyarla(olceklendirilmis)
        self.ekrandaGoster(olceklendirilmis)
    
    #ölçeklendirme görsel arayüzünün ayarlanması    
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
        
    #resime kırpma uygulanması
    def kirp(self):
        resim = self.acikResim
        #kırpılacak kısmın sol üst köşe koordinatlarının seçilmesi
        x1 = int(self.x1Input.text())
        y1 = int(self.y1Input.text())
        #kırpılacak resmin sağ alt köşe koordinatlarının seçilmesi
        x2 = int(self.x2Input.text())
        y2 = int(self.y2Input.text())
        
        kirpilmis = np.copy(resim[y1:y2,x1:x2])
        
        self.islenmisResmiAyarla(kirpilmis)
        self.ekrandaGoster(kirpilmis)
        
    #kirpma görsel arayüzünün ayarlanması    
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
    #comboboxtan seçilen işlemin ekrana getirilmesi    
    def yogunlukIslemSecimiUygula(self):
        index = self.yogunlukIslemComboBox.currentIndex()
        self.yogunlukDonusumuStackedWidget.setCurrentIndex(index)
        
    #gamma uygulanması
    def gammaUygula(self):
        resim = self.acikResim
        
        gammaDegeri = float(self.gammaLineEdit.text())
        gainDegeri = float(self.gammaGainLineEdit.text())
        
        gammaUygulanmis = exposure.adjust_gamma(resim,gammaDegeri, gainDegeri)
        
        self.islenmisResmiAyarla(gammaUygulanmis)
        
        self.ekrandaGoster(gammaUygulanmis)
        
    #gamma görsel arayüzünün ayarlanması
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
        
    #log uygulanması    
    def logUygula(self):
        resim = self.acikResim
        
        gainDegeri = float(self.logGainLineEdit.text())
        inverse = False
        
        if self.inverseCheckBox.isChecked():
            inverse = True
        
        logUygulanmis = exposure.adjust_log(resim,gainDegeri, inverse)
        
        self.islenmisResmiAyarla(logUygulanmis)
        
        self.ekrandaGoster(logUygulanmis)
        
    #log görsel arayüzünün ayarlanması    
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
        
    #sigmoid uygulanması    
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
        
    #sigmoid görsel arayüzünün ayarlanması    
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
        
    #equalize adapthist uygulanması    
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
        
    #equalize adapthist görsel arayüzünün ayarlanması
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
        
    #combobox seçimine göre işlem ekranının getirilmesi    
    def morfolojikIslemUygula(self):
        index = self.morfolojikIslemComboBox.currentIndex()
        
        #ilk 6 morfolojik işlem aynı parametre aldığı için tek fonksiyonda işleniyor
        if index < 6:
            self.morfolojiStackedWidget.setCurrentIndex(0)
            
        else:
            self.morfolojiStackedWidget.setCurrentIndex(index - 5)
        
    #square width parametresi alan morfolojik işlemlerin uygulanması
    def morfolojiSquareWidthIslemUygula(self):
        resim = self.acikResim
        
        if len(resim.shape) == 3:
            resim = rgb2gray(resim)
        
        index = self.morfolojikIslemComboBox.currentIndex()
        
        morfolojikIslemUygulanmis = None
        
        squareWidthDegeri = int(self.morfolojiSquareWidthLineEdit.text())
        
        #erosion işlemi
        if index == 0:
            morfolojikIslemUygulanmis = morphology.erosion(resim, morphology.square(squareWidthDegeri))
        #dilation işlemi
        elif index ==1:
            morfolojikIslemUygulanmis = morphology.dilation(resim, morphology.square(squareWidthDegeri))
        #opening işlemi
        elif index ==2:
            morfolojikIslemUygulanmis = morphology.opening(resim, morphology.square(squareWidthDegeri))
        #closing işlemi    
        elif index ==3:
            morfolojikIslemUygulanmis = morphology.closing(resim, morphology.square(squareWidthDegeri))
        #white tophat işlemi
        elif index ==4:
            morfolojikIslemUygulanmis = morphology.white_tophat(resim, morphology.square(squareWidthDegeri))
        #black tophat işlemi
        elif index ==5:
            morfolojikIslemUygulanmis = morphology.black_tophat(resim, morphology.square(squareWidthDegeri))
            
        self.islenmisResmiAyarla(morfolojikIslemUygulanmis)
        
        self.ekrandaGoster(morfolojikIslemUygulanmis)
        
    #square width parametresi alan işlemleri gerçekleştirmeyi sağlayan görsel arayüzün ayarlanması    
    def morfolojiSquareWidthIslemlerUI(self):
        self.morfolojiSquareWidthLineEdit = QLineEdit()
        self.morfolojiSquareWidthLineEdit.setText("10")
        
        morfolojiSquareWidthUygulaButon = QPushButton("Uygula")
        morfolojiSquareWidthUygulaButon.clicked.connect(self.morfolojiSquareWidthIslemUygula)
        
        form = QFormLayout()
        form.addRow("Square Width: ", self.morfolojiSquareWidthLineEdit)
        form.addRow(morfolojiSquareWidthUygulaButon)
        self.squareWidthIslemlerWidget.setLayout(form)
        
    #skeletonize morfolojik işleminin uygulanması    
    def skeletonizeUygula(self):
        resim = self.acikResim
        
        if len(resim.shape) == 3:
            resim = rgb2gray(resim)
            
        skeletonizeUygulanmis = morphology.skeletonize(resim).astype(int)
        
        self.islenmisResmiAyarla(skeletonizeUygulanmis)
        
        self.ekrandaGoster(skeletonizeUygulanmis)
        
    #skeletonize görsel arayüzünün ayarlanması
    def skeletonizeUI(self):
        skeletonizeUygulaButon = QPushButton("Uygula")
        skeletonizeUygulaButon.clicked.connect(self.skeletonizeUygula)
        
        form = QFormLayout()
        form.addRow(skeletonizeUygulaButon)
        self.skeletonizeWidget.setLayout(form)
        
    #thin işleminin uygulanması
    def thinUygula(self):
        resim = self.acikResim
        
        if len(resim.shape) == 3:
            resim = rgb2gray(resim)
            
        iterationDegeri = int(self.thinIterationLineEdit.text())
        
        thinUygulanmis = morphology.thin(resim, iterationDegeri).astype(int)
        
        self.islenmisResmiAyarla(thinUygulanmis)
        
        self.ekrandaGoster(thinUygulanmis)
        
    #thin görsel arayünün ayarlanması
    def thinUI(self):
        self.thinIterationLineEdit = QLineEdit()
        self.thinIterationLineEdit.setText("1")
        
        thinUygulaButon = QPushButton("Uygula")
        thinUygulaButon.clicked.connect(self.thinUygula)
        
        form = QFormLayout()
        form.addRow("Iteration: ", self.thinIterationLineEdit)
        form.addRow(thinUygulaButon)
        self.thinWidget.setLayout(form)
        
    #remove small objects işleminin uygulanması
    def removeSmallObjectsUygula(self):
        resim = self.acikResim
        
        minSizeDegeri = int(self.minSizeLineEdit.text())
        
        removeSmallObjectsUygulanmis = morphology.remove_small_objects(resim, minSizeDegeri)
        
        self.islenmisResmiAyarla(removeSmallObjectsUygulanmis)
        
        self.ekrandaGoster(removeSmallObjectsUygulanmis)
    
    #remove small objects görsel arayüzünün ayarlanması
    def removeSmallObjectsUI(self):
        self.minSizeLineEdit = QLineEdit()
        self.minSizeLineEdit.setText("64")
        
        removeSmallObjectsUygulaButon = QPushButton("Uygula")
        removeSmallObjectsUygulaButon.clicked.connect(self.removeSmallObjectsUygula)
        
        form = QFormLayout()
        form.addRow("Min. Size: ", self.minSizeLineEdit)
        form.addRow(removeSmallObjectsUygulaButon)
        self.removeSmallObjectsWidget.setLayout(form)
        
    #medial axis uygulanması
    def medialAxisUygula(self):
        resim = self.acikResim
        
        medialAxisUygulanmis = morphology.medial_axis(resim).astype(int)
        
        self.islenmisResmiAyarla(medialAxisUygulanmis)
        
        self.ekrandaGoster(medialAxisUygulanmis)
        
    #medial axis görsel arayüzünün ayarlanması
    def medialAxisUI(self):
        medialAcisUygulaButon = QPushButton("Uygula")
        medialAcisUygulaButon.clicked.connect(self.medialAxisUygula)
        
        form = QFormLayout()
        form.addRow(medialAcisUygulaButon)
        self.medialAxisWidget.setLayout(form)
        
###############################################################################
#VİDEO İŞLEME ALANI
    
    #video seçme işlemi    
    def videoSec(self):
        dosyaYolu = QFileDialog.getOpenFileName(self,"Video Seç", "", "Video Dosyası(*)")
        if dosyaYolu[0]:
            bas, son = os.path.split(dosyaYolu[0])
            self.videoAdiLabel.setText(son)
            
            self.videoDosyaYolu = dosyaYolu[0]
            
    #bir pencerede kenar belirleme filtresi uygulanmış videonun gösterilmesi
    def islenmisVideoIzle(self):
        if self.videoDosyaYolu:
            
            cap = cv2.VideoCapture(self.videoDosyaYolu)
            
            #her frame tek tek işleniyor
            while(1):
                ret, frame = cap.read()
                
                #son frame e geldiyse çık
                if ret == 0:
                    break
                #canny filtresinin uygulanması
                edges = cv2.Canny(frame, 100, 200)
                
                #işlenen frame'in ekrana basılması
                cv2.imshow('Edges', edges)
            
                #çıkmak için q tuşuna basınız
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("işlem iptal edildi")
                    break

            cv2.destroyAllWindows()
            cap.release()
    
    
    def islenmisVideoKaydet(self):
        #seçilmiş bir video varsa
        if self.videoDosyaYolu:
            #kayıt dosya yolu seçilmesi
            dosyaYolu = QFileDialog.getSaveFileName(self,"Kayıt Yeri Seç",str(datetime.timestamp(datetime.now())), "*.avi")
            if dosyaYolu[0]:
                
                #geri bildirim mesajı gösterilmesi
                self.kayitDurumuLabel.setStyleSheet("color:orange")
                self.kayitDurumuLabel.setText("İşleniyor...")
                
                cap = cv2.VideoCapture(self.videoDosyaYolu)
                
                #video çözünürlüğü
                frame_width = int(cap.get(3))
                frame_height = int(cap.get(4))
                
                out = cv2.VideoWriter(dosyaYolu[0],cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width,frame_height))
                
                #her frame tek tek işleniyor
                while(1):
                    ret, frame = cap.read()
                    
                    #son frame e geldiyse çık
                    if ret == 0:
                        break
                    
                    #canny filtresinin uygulanması
                    edges = cv2.Canny(frame, 100, 200)
                    
                    #canny filtresi binary 2d çıktı veriyor
                    #bize 3d lazım olduğu için rgb ye çeviriyoruz
                    backtorgb = cv2.cvtColor(edges,cv2.COLOR_GRAY2RGB)
                    
                    #framein yazılması
                    out.write(backtorgb)
    
                cv2.destroyAllWindows()
                cap.release()
                out.release()
                
                #geri bildirim mesajı gösterilmesi
                self.kayitDurumuLabel.setStyleSheet("color:green")
                self.kayitDurumuLabel.setText("Tamamlandı!")
                
        
#pencerenin oluşturularak programın başlatılması    
if __name__ == "__main__":
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    pencere = Pencere()
    sys.exit(app.exec())
