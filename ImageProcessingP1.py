# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 15:22:15 2019

@author: serdar
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from skimage import data, io, filters, img_as_ubyte
from skimage.color import rgb2gray, gray2rgb
from scipy.misc import imsave

import numpy as np

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
        
        islemAlani.addTab(self.filtreTab, "Filtre")
        islemAlani.addTab(self.histogramTab, "Histogram")
        islemAlani.setTabPosition(QTabWidget.East)
        
        
        self.filtreUI()
    
        
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
            
    def dosyaKaydet(self):
        dosyaYolu = QFileDialog.getSaveFileName(self,"Kayıt Yeri Seç",str(datetime.timestamp(datetime.now())), "*.jpg *.png")
        print(dosyaYolu[0])
        if dosyaYolu[0]:
            io.imsave(dosyaYolu[0],self.islenmis)
            
    def filtreUI(self):
        secim = QComboBox()
        secim.addItem("Sobel")
        
        uygulaButon = QPushButton("Uygula")
        uygulaButon.resize(80,30)
        uygulaButon.clicked.connect(self.filtreUygula)
        
        form = QFormLayout()
        form.addRow("Filtre Seçimi: ",secim)
        form.addRow(uygulaButon)
        self.filtreTab.setLayout(form)
    
    def filtreUygula(self):
        resim = io.imread(self.acikResim)
        
        #sobel filtresi için 2d arraya dönüştürülmesi
        gri = rgb2gray(resim)
        
        filtrelenmis = filters.sobel(gri)
        
        self.islenmis = filtrelenmis
        
        #filtreleme float64 tipinde 2d array çıktı veriyor ekrana basmak için bize uint8 tipinde 3d array(rgb) gerekli
        donusturulmus = gray2rgb(img_as_ubyte(filtrelenmis))
        
        #np arrayin QImage dönüştürülmesi
        height, width, channel = donusturulmus.shape
        bytesPerLine = 3 * width
        qImg = QImage(donusturulmus.data, width, height, bytesPerLine, QImage.Format_RGB888)
        
        pixmap = QPixmap(qImg)
        pix = pixmap.scaled(400, 600, Qt.KeepAspectRatio)
        self.etiket.setPixmap(pix)


    
if __name__ == "__main__":
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    pencere = Pencere()
    sys.exit(app.exec())
