import shutil
import requests
import os
from os.path import isfile, join
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import img2pdf


class Book:
    def __init__(self, book_url, titolo):
        self.temp_path = self.make_temp_path()
        self.url = book_url
        self.soup = self.get_json_details()
        self.label = titolo
        self.book_temp_path = self.make_book_temp_path()
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

    def makePdf(self,pdfpath):
        Pages = [f for f in os.listdir(self.imgs_path) if isfile(join(self.imgs_path, f))]
        if Pages:
            pagelist = []
            for page in Pages:
                pagepath = os.path.join(self.book_temp_path, page)
                pagelist.append(pagepath)

            pagelist = sorted(pagelist)
            pdf = os.path.join(pdfpath, f"{self.label}.pdf")
            with open(pdf, "wb") as f:
                f.write(img2pdf.convert(pagelist))

    def get_json_details(self):
        book_id = self.url.split('=')[-1:][0]
        manifest_xml = f'https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr={book_id}&azione=readBook'

        r = requests.get(manifest_xml)
        soup = bs(r.text, 'lxml')

        return soup

    def download_image(self, url, img_path):
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(img_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

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


link = input("Incolla il link del libro...\n")
titolo = input("Scrivi il titolo del libro...\n")

book = Book(link, titolo)

link_list = book.get_link_list()
book.start_download(link_list, book.label)

pdfpath = os.path.join(os.getcwd(), "PDFs")
if not os.path.exists(pdfpath):
    os.makedirs(pdfpath)

book.makePdf(pdfpath)
shutil.rmtree(temp_path)
input(f"##################################\n"
      f"####  Titolo: {book.label}\n"
      f"####  Scaricato con successo\n"
      f"##################################\n")
