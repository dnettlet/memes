from bs4 import BeautifulSoup
import urllib2
#import ho.pisa as pisa
import logging
import codecs
"""
filename: nombre del archivo final
url: pagina de donde se extraera informacion
div: es un elemento html, extraer elemento especifico
"""
class HtmlExtract:
    def __init__(self, filename, pages={}, divId=None):
        self.filename=filename
        #self.url = url
        self.pages = pages#sorted(pages)
        self.divId = divId
        #print self.pages #estan desordenados
        #print "---"
        self.htmlFull2 = """ <style>
            @page {
             size: a4 ;
             font: 14px verdana;
             width: 100%;
             margin: 20px;
             line-height: 90%;
             display: block;
            }
            table {
            -pdf-keep-in-frame-mode: overflow;
            }
            li pre ul span{
            width: 250px;
            display: block;
            list-style: none;
            }
            </style>"""
        self.htmlFull=""

        self.extraerInfo()
        self.convertirTXT()

    def extraerInfo(self):
        #for titulo in self.pages:
        #for titulo in sorted(self.pages):
        print self.pages
        for url in self.pages:
            #EXTRAER HTML FROM INTERNET
            #print titulo, url
            #self.htmlFull += "<h1>"+titulo+": "+url+"</h1>"
            if url == "":
                continue            
            conn = urllib2.urlopen(url)
            html = conn.read()
            #EXTRAE DIV ESPECIFICO
            soup = BeautifulSoup(html)
            #print "SOUP\n",soup
            #html acumulador
            
            #self.htmlFull += str(soup.find("span", {"id": self.divId}))
            self.htmlFull = soup.find("span", {"id": self.divId})
            

    def convertirTXT(self):

        self.htmlFull = self.htmlFull.get_text()
        with codecs.open(self.filename+".txt", "w", "utf-8") as txt: #utf-8-sig
            txt.write(self.htmlFull)



