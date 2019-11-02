# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 15:22:15 2019

@author: serdar
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from skimage import data, io, filters, img_as_ubyte, feature, exposure, transform
from skimage.color import rgb2gray, gray2rgb
from scipy.misc import imsave

import numpy as np

import matplotlib.pyplot as plt

from datetime import datetime

import sys

class Pencere(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.widget = MerkeziWidget()
        self.setCentralWidget(self.widget)
        self.setUI()
        self.resize(800,600)
    
    
    def setUI(self):
        
        self.ActionOluştur()
        self.MenuOlustur()
        
        self.setWindowTitle("Fotoşok")
        self.show()
        
        
    def ActionOluştur(self):
        self.resimYukleAction = QAction("Aç", self, triggered=self.widget.dosyaAc)
        self.resimKaydetAction = QAction("Kaydet",self, triggered= self.widget.dosyaKaydet)
        
    def MenuOlustur(self):
        self.dosyaMenu = QMenu("Dosya",self)
        self.dosyaMenu.addAction(self.resimYukleAction)
        self.dosyaMenu.addAction(self.resimKaydetAction)
        
        self.menuBar().addMenu(self.dosyaMenu)
        
class MerkeziWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.acikResim = None
        self.islenmis = None
                
        self.setUI()
        

        
    def setUI(self):
        self.etiket = QLabel(self)
        self.etiket.resize(400,600)
        pixmap = QPixmap()
        pix = pixmap.scaled(400, 600, Qt.KeepAspectRatio)
        self.etiket.setPixmap(pix)
        
        islemAlani = QTabWidget(self)
        islemAlani.move(401,0)
        islemAlani.resize(400,600)
        
        self.filtreTab = QWidget()
        self.histogramTab = QWidget()
        self.donusumTab = QWidget()
        
        islemAlani.addTab(self.filtreTab, "Filtre")
        islemAlani.addTab(self.histogramTab, "Histogram")
        islemAlani.addTab(self.donusumTab,"Dönüşüm")
        islemAlani.setTabPosition(QTabWidget.East)
        
        
        self.filtreUI()
        self.histogramUI()
        self.donusumUI()
    
        
    def deneme(self):
        pixmap = QPixmap('C:/Users/serdar/Desktop/masaustu.jpg')
        pix = pixmap.scaled(400, 600, Qt.KeepAspectRatio)
        self.etiket.setPixmap(pix)
        
    def serdar(self):
        pixmap = QPixmap('C:/Users/serdar/Desktop/züreyfa.jpg')
        form = QFormLayout()
        etiket = QLabel("serdar")
        form.addRow(etiket)
        self.resimAlani.setLayout(form)
        
    def dosyaAc(self):
        dosyaYolu = QFileDialog.getOpenFileName(self,"Dosya Seç", "", "Resim Dosyası (*.jpg *.png *jpeg *.xpm)")
        if dosyaYolu[0]:
            pixmap = QPixmap(dosyaYolu[0])
            pix = pixmap.scaled(400, 600, Qt.KeepAspectRatio)
            self.etiket.setPixmap(pix)
            
            self.acikResim = dosyaYolu[0]
        print(dosyaYolu)
        
            
    def dosyaKaydet(self):
        dosyaYolu = QFileDialog.getSaveFileName(self,"Kayıt Yeri Seç",str(datetime.timestamp(datetime.now())), "*.jpg *.png")
        print(dosyaYolu[0])
        if dosyaYolu[0]:
            io.imsave(dosyaYolu[0],self.islenmis)
            
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
        
    def donusumUI(self):
        self.islemComboBox = QComboBox()
        self.islemComboBox.addItems(["Yeniden Boyutlandırma", "Döndürme", "Kırpma"])
        self.islemComboBox.currentIndexChanged.connect(self.islemSecimiUygula)
        
        self.donusumStackedWidget = QStackedWidget()
        
        self.yenidenBoyutlandirmaWidget = QWidget()
        self.dondurmeWidget = QWidget()
        
        self.yenidenBoyutlandirUI()
        self.dondurmeUI()
        
        self.donusumStackedWidget.addWidget(self.yenidenBoyutlandirmaWidget)
        self.donusumStackedWidget.addWidget(self.dondurmeWidget)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        
        form = QFormLayout()
        form.addRow("İşlem Seçimi: ",self.islemComboBox)
        form.addRow(line)
        form.addRow(self.donusumStackedWidget)
        self.donusumTab.setLayout(form)
        
        
    def ekrandaGoster(self,gosterilecekResim):
        #filtreleme float64 tipinde 2d array çıktı veriyor ekrana basmak için bize uint8 tipinde 3d array(rgb) gerekli
        donusturulmus = gray2rgb(img_as_ubyte(gosterilecekResim))
            
        #np arrayin QImage dönüştürülmesi
        height, width, channel = donusturulmus.shape
        bytesPerLine = 3 * width
        qImg = QImage(donusturulmus.data, width, height, bytesPerLine, QImage.Format_RGB888)
        
        pixmap = QPixmap(qImg)
        pix = pixmap.scaled(400, 600, Qt.KeepAspectRatio)
        self.etiket.setPixmap(pix)
    
###############################################################################
#FİLTRE ALANI        
    
    def filtreUygula(self):
        resim = io.imread(self.acikResim)
        
        #filtreler için 2d arraya dönüştürülmesi
        gri = rgb2gray(resim)
        
        index = self.secim.currentIndex()
        if index == 0:
            filtrelenmis = filters.sobel(gri)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
        elif index == 1:
            filtrelenmis = filters.hessian(gri)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
        elif index == 2:
            filtrelenmis = feature.canny(gri)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
        elif index == 3:
            filtrelenmis = filters.prewitt(gri)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
        elif index == 4:
            filtrelenmis = filters.laplace(resim)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
        elif index == 5:
            filtrelenmis = filters.sato(gri)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
        elif index==6:
            filtrelenmis = filters.unsharp_mask(resim,radius= 2, amount=2)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
        elif index==7:
            filtrelenmis = filters.threshold_niblack(gri)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
        elif index==8:
            filtrelenmis = filters.meijering(gri)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
        elif index==9:
            filtrelenmis = filters.threshold_sauvola(gri)
            self.islenmis = filtrelenmis
            self.ekrandaGoster(filtrelenmis)
            
###############################################################################
#HİSTOGRAM ALANI 
            
    def histogramGoruntule(self):
        #resmin np arraya dönüştürülmesi
        resim = io.imread(self.acikResim)
        
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
        resim = io.imread(self.acikResim)
        
        #histogramın eşitlenmesi
        esitlenmis = exposure.equalize_hist(resim)
        
        self.islenmis = esitlenmis
        self.ekrandaGoster(esitlenmis)

###############################################################################
#DÖNÜŞÜM ALANI
    def islemSecimiUygula(self):
        index = self.islemComboBox.currentIndex()
        self.donusumStackedWidget.setCurrentIndex(index)
            
        
        
    def yenidenBoyutlandir(self):
        genislik = int(self.genislikSatiri.text())
        yukseklik = int(self.yukseklikSatiri.text())
        #resmin np arraya dönüştürülmesi
        resim = io.imread(self.acikResim)
        
        boyutlandirilmis = transform.resize(resim,(yukseklik,genislik))
        
        self.islenmis = boyutlandirilmis
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
        
    def dondurmeUI(self):
        boyutlandirmaButon = QPushButton("Döndür")
        form = QFormLayout()
        form.addRow(boyutlandirmaButon)
        self.dondurmeWidget.setLayout(form)
        
    
if __name__ == "__main__":
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    pencere = Pencere()
    sys.exit(app.exec())
