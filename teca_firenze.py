import shutil
import urllib.request
from fpdf import FPDF
from PIL import Image
import requests
import json
import os
from os import listdir
from os.path import isfile, join
from tqdm import tqdm
from bs4 import BeautifulSoup as bs


class Book:
    def __init__(self, book_url, titolo):
        self.temp_path = self.make_temp_path()
        self.url = book_url
        self.soup = self.get_json_details()


        self.label = titolo
        self.imgs_path = self.make_book_temp_path()

    def make_img_path(self, index, book_img_path):
        cifre = len(str(index))
        if cifre == 1:
            file = "000" + str(index) + ".jpeg"
        elif cifre == 2:
            file = "00" + str(index) + ".jpeg"
        elif cifre == 3:
            file = "0" + str(index) + ".jpeg"
        else:
            file = str(index) + ".jpeg"

        img_path = os.path.join(book_img_path, file)
        return img_path

    def make_temp_path(self):
        temp_path = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        return temp_path

    def make_book_temp_path(self):
        bookpath = os.path.join(temp_path, f"{self.label}")
        if not os.path.exists(bookpath):
            os.makedirs(bookpath)
        return bookpath

    def makePdf(self, pdfpath):
        Pages = [f for f in os.listdir(self.imgs_path) if isfile(join(self.imgs_path, f))]
        listPages = tqdm(Pages, "Creando PDF  ", unit="Pagina", leave=False)
        if Pages:
            pdfpdf_file_path = os.path.join(pdfpath, f"{self.label}.pdf")

            coverimage = os.path.join(self.imgs_path, Pages[0])
            cover = Image.open(coverimage)
            width, height = cover.size

            pdf = FPDF(unit="pt", format=[width, height])

            for page in listPages:
                pdf.add_page()
                pdf.image(os.path.join(self.imgs_path, page), 0, 0)

            pdf.output(pdfpdf_file_path, "F")

    def get_json_details(self):
        self.url = "https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr=BNCF0003862255"
        book_id = self.url.split('=')[-1:][0]
        manifest_xml = f'https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr={book_id}&azione=readBook'

        r = requests.get(manifest_xml)
        soup = bs(r.text, 'lxml')

        return soup

    def download_image(self, url, img_path):
        urllib.request.urlretrieve(url, img_path)

    def download_book(self, list):
        for index, url in enumerate(list):
            img_path = self.make_img_path(index, self.imgs_path)
            self.download_image(url, img_path)

    def start_download(self, link_list, label):
        tq_list = tqdm(link_list, f"Scaricando {label}  ", unit="pagina", leave=False)
        self.download_book(tq_list)
        tq_list.close()

    def get_link_list(self):
        soup = self.soup
        classes_list = soup.find_all('immagine')
        link_list = []
        for immagine in classes_list:
            img_id = immagine['id']
            img_sq = immagine['mx-libro:sequenza']
            img_url = f"https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr={img_id}&azione=showImg&sequence={img_sq}"
            link_list.append(img_url)
        return link_list


temp_path = os.path.join(os.getcwd(), 'temp')
if not os.path.exists(temp_path):
    os.makedirs(temp_path)


link = input("Incolla il link del libro...")
titolo = input("Incolla il titolo del libro...")

book = Book(link, titolo)

try:
    link_list = book.get_link_list()
    book.start_download(link_list, book.label)

    pdfpath = os.path.join(os.getcwd(), "PDFs")
    if not os.path.exists(pdfpath):
        os.makedirs(pdfpath)

    book.makePdf(pdfpath)

    print(f"##################################\n"
          f"####  Titolo: {book.label}\n"
          f"####  Scaricato con successo\n"
          f"##################################\n")
except:
    print(f"Un errore ha impedito di scaricare {book.label}")

shutil.rmtree(temp_path)