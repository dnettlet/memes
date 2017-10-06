# -*- coding: cp1252 -*-
#import matplotlib.pyplot as plt #UnUsed < ver linea 162
from nltk import corpus
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import string
from itertools import permutations
from collections import Counter
import networkx as nx
import codecs
import random

import re, math
from collections import Counter
from nltk.corpus import wordnet as wn
import os, io
stopwords = corpus.stopwords.words('english') 
lmtzr = WordNetLemmatizer()
stopwordsVerbs = ['am','is','are','was',' were','be','been','being',
		  'have','has','had','having',
		  'do','does','did','doing',
                  ]

#Corpus
from Corpus.Corpus_en import corpus_en as corpus

import time

#APRIORI ALGORITMO
from apriori import apriori
printData = False

#Manejo de palabras, indexar.
class Words: 
    def __init__(self, example, folderInput):
        self.FullpathExample = example
        self.folderInput = folderInput
        self.text = ''
        self.documents = []
        self.numDocs = 0
        self.paragraph = {}
        self.numParagraph = {}
        self.pos = {}

        self.read_example() # Leer texto
        self.indexing()     # Indexar

        self.actualParagraph = 0
        self.actualDoc = 0
        self.actualWord = 0
        if printData: print "Numero documentos",self.numDocs
        #for e in self.pos:
            #print self.pos[e],"\n"

        

    def read_example(self, delimiter='=================================='):
        #with codecs.open(self.folderInput+"/"+self.FullpathExample,'r','utf-8') as f:#data/ 'example1.txt' #,'utf-8'
        with codecs.open(self.FullpathExample,'r','utf-8') as f:
            self.text = f.read()
        # Ver modulo "Interfaz" .fix_txt()
        self.text = self.text.replace(u'\u2019','\'') #Problema comillas simples.
        self.text = self.text.replace(u'\u2018','\'') #Problema comillas simples.
        self.text = self.text.replace(u'\u201c','"') #Problema comillas dobles.
        self.text = self.text.replace(u'\u201d','"') #Problema comillas dobles.        
        self.text = self.text.replace(u'\u2014',' ') #Problema unicode —.
        #u' '     ´  -> '
        self.text = self.text.replace('\r','\n')
        #Limpiando texto stopword - AGREGAR MAS
        self.text = self.text.replace('\'re',' are')
        self.text = self.text.replace('\'m',' am')
        self.text = self.text.replace('wasn\'t','was not')
        self.text = self.text.replace('wouldn\'t','would not')
        self.text = self.text.replace('don\'t','do not')
        self.text = self.text.replace('didn\'t','did not')
        self.text = self.text.replace('\'ve',' have')
        self.text = self.text.replace('she\'s','she is')
        self.text = self.text.replace('he\'s','he is')
        self.text = self.text.replace('it\'s','it is')
        self.text = self.text.replace('\'d',' would')
        self.text = self.text.replace('isn\'t','is not')
        self.text = self.text.replace('aren\'t','are not')
        
        self.documents = self.text.split(delimiter) 
        self.numDocs = len(self.documents)

        

    def remove_punc_upper(self, text_str):
        for c in string.punctuation: #'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
            text_str= text_str.replace(c," ")
        return text_str

    # Separa texto en contexto
    def indexing(self):        
        for doc_id, doc in enumerate(self.documents):#dividiendo por documentos
            contex = re.split('\.[\ |\n+]+', doc) #dividiendo por parrafos
            for e in contex:
                if e==" ":
                    contex.remove(' ')
                if e=="":
                    contex.remove('')
            for context_id, p in enumerate(contex):# dividiendo por palabras
                p = self.remove_punc_upper(p.replace('\n',' ')) # Elimina signos
                self.paragraph[doc_id] = self.paragraph.get(doc_id,[])
                self.paragraph[doc_id].append(p)

                for c, t in nltk.pos_tag((p).split()): #Agrega el tag NN VB ... a todas las palabras
                    self.pos[doc_id] = self.pos.get(doc_id,[])
                    self.pos[doc_id].append((context_id, c, t)) #context_id=Numero parrafo en el documento
                try:
                    self.pos[doc_id].append((context_id, '.', None)) #Fin paragraph
                except:
                    pass
                self.numParagraph[doc_id] = context_id
            self.numDocs = doc_id
        #El numero de la palabra viene dada por la posicion en que se agrego a la lista

    def initDocument(self, doc_id):
        if doc_id > self.numDocs:
            return None        
        self.actualDoc = doc_id
        self.actualParagraph = 0
        self.actualWord = 0

    # Avanza por palabra. Antes debe inicializar un documento.
    def getWord(self, num_paragraph = None, word_index=None):
        if word_index != None:
            self.actualWord = word_index
        try:
            temp = self.pos[self.actualDoc][self.actualWord]
        except:
            return None
        self.actualWord+=1        
        return (temp[0], temp[1], self.actualDoc, self.actualWord-1, temp[2])#[1]

    #
    def buscaPalabras(self, diccListTuple, F_list):

        # diccListTuple: posiciones de todos los 1-grama Info apriori
        # F_list: salida del algoritmo Apriori
        
        #print self.pos
        #Obtener palabra especifica
        #print self.pos[self.actualDoc][self.actualWord]
        
        """
        ## -- Prueba palabras aleatorias en los #conceptos mas frecuentes".
        print "WORD: ",self.pos[2][33] #insurance  -->  (parrafo, concepto, tag)
        print "WORD 2: ",self.pos[2][33][0] #insurance  --> parrafo
        print "WORD: ",self.pos[14][243] #care
        print "WORD: ",self.pos[16][44] #people
        print "WORD: ",self.pos[3][1] #state
        # OK
        # salida tupla ( parrafo , concept , tag )
        """
        ## DATOS
        #self.pos[ doc ][ pos_palabra -1 ] === tupla de la palabra anterior (articulo, advervio, etc)
        #self.pos[ doc ][ pos_palabra +1 ] === tupla de la palabra siguiente
        #self.pos[ doc ][ pos_palabra ][ 0 ] === Numero parrafo
        #self.pos[ doc ][ pos_palabra ][ 1 ] === concepto
        #self.pos[ doc ][ pos_palabra ][ 2 ] === tag -- NN

        # Lista que guarda las posiciones de los conceptos 2-grama encontrados
        closed_dicc_list = {}
        
        # 1.- Preparar F2_aux: contiene toda convinacion posible de 2 gramas
        F2_grama_aux = set()
        try:
            F_list[1]
        except:
            aux = {}
            return aux
        for item_frozenset in F_list[1]:
            if len(item_frozenset) != 2:
                print "ERROR!, F[1] no es 2-grama"
                break
            c1, c2 = item_frozenset
            F2_grama_aux.add( c1+" "+c2 )
            F2_grama_aux.add( c2+" "+c1 )

        if printData: print "Lista auxiliar de convinaciones 2-grama", F2_grama_aux
       
        if printData: print "========================================"
        # 2.- Iterar por todo diccListTuple, el cual contiene las posiciones de todas los conceptos 1-grama
        # diccListTuple = { A:[ (0, 14), ... ], ... }
        for concepto in diccListTuple:
            # concepto: la palabra actual seleccionada                        
            for tupla_poscicion in diccListTuple[concepto]: #
                # tupla_poscicion: (num_documento, posicion concepto en tal documento)
                doc, posicionPalabra = tupla_poscicion

                #Obtener palabra cercanas
                palabra_posterior   = self.pos[ doc ][ posicionPalabra +1 ][1] # (parrafo, concepto, tag)
                palabra_anterior    = self.pos[ doc ][ posicionPalabra -1 ][1]

                concepto_2_grama_posterior  = concepto+" "+palabra_posterior
                concepto_2_grama_anterior   = palabra_anterior+" "+concepto

                if printData: print "Convinacion:",concepto.upper()+" "+palabra_posterior," \t; ", concepto_2_grama_anterior+" "+concepto.upper()

                # 3.- Verificar si los 'pares 1-grama' estan en la lista 2-grama auxiliar (toda convinacion 2 grama)
                if concepto_2_grama_posterior in F2_grama_aux:
                    closed_dicc_list[doc] = closed_dicc_list.get(doc,[])
                    closed_dicc_list[doc].append( posicionPalabra )
                    closed_dicc_list[doc].append( posicionPalabra + 1 )
                    if printData: print "\t\t2-grama found:", concepto_2_grama_posterior
                    
                if concepto_2_grama_anterior in F2_grama_aux:
                    closed_dicc_list[doc] = closed_dicc_list.get(doc,[])
                    closed_dicc_list[doc].append( posicionPalabra - 1 )
                    closed_dicc_list[doc].append( posicionPalabra )
                    if printData: print "\t\t2-grama found:", concepto_2_grama_anterior
        if printData: print "========================================"
        if printData: print "LISTA CERRADA: ",closed_dicc_list

        
        if printData: print "======= 4.- Preparando n-gramas ========"
        ## 4.- Preparar F_list_ngrama: debe ser una lista de conceptos n-gramas -> [ 'A B', 'A B C',..
        F_list_ngrama = []
        """
        #               1-gramas             2-gramas           3-gramas        n-grama
        # F_list = [ [ A, B ,C , ...],  [(A,B), (B,C), ...], [ (A, B, C), ... ], ... ]
        """
        for n_grama in F_list[1:]:
            # n_grama = [frozenset(A,B), frozenset(B,C), ...]  ||  [ frozensets(A, B, C), ... ] ] || ...
            for frozensets in n_grama: # Omite los 1-grama      
                #print "\nfrozensets: ",frozensets
                # frozensets = frozen(A,B) || frozen(B,C) || ... || frozen(N,N,..)                

                aux_str = ""
                for num, concepto in enumerate(frozensets):
                    if printData: print concepto
                    if num != 0:
                        concepto = " "+concepto
                    aux_str += concepto
                F_list_ngrama.append(aux_str)

        if printData: print "====Lista n-gramas, segun la salida del conjunfo F(k) en Apriori===="
        if printData: print F_list_ngrama

        # diccGramas: diccionario de diccionario
        # diccGramas: diccGramas[numero_documento][n_grama]
        diccGramas = {} # diccionario guarda los n-gramas a encontrar, separandolos por documento.
        ## 5.- Buscar n-gramas en la closed_dicc_list usando la F_list_ngrama ('A B',...)
        if printData: print "====Conjunto ordenado===="
        for doc in closed_dicc_list:
            diccGramas[doc] = diccGramas.get(doc, {})
            
            #closed_dicc_list[doc] : lista de posiciones en tal documento (doc) :: [ 4,5,6,2,8,4,5,3,4,5,... ]
            lista_posiciones = sorted(set(closed_dicc_list[doc])) # Lista cerrada sin elementos repetidos.
            #print "==",lista_posiciones
            
            ## Buscar posiciones continuas
            start = lista_posiciones[0] # posicion inicial del n-grama (auxiliar)
            end = lista_posiciones[0]   # posicion final  del n-grama (auxiliar)
            #print start, end, lista_posiciones
            #dicc = {}
            count_list = [start] # posiciones del n-grama (auxiliar) - Final:[4,5,6] -> 4:Start, 5:End.
            for posicion_palabra in lista_posiciones[1:]: # Omite posicion cero, se inicia en este.
                #print posicion_palabra,"-->",self.pos[ doc ][ posicion_palabra ][1]
                if (end+1) == posicion_palabra: # si la siguiente palabra es posicion continua - Ejemplo 5,6
                    end = posicion_palabra
                    count_list.append(posicion_palabra) # se agrega a la lista auxiliar del n-grama acutal
                else: # Si no es continua calcular rango y guardar
                    n_grama_aux = end-start+1 # Calcula rango
                    
                    #for i in range(start,end+1):
                    diccGramas[doc][n_grama_aux] = diccGramas[doc].get(n_grama_aux,[])
                    diccGramas[doc][n_grama_aux].append( count_list ) # Guarda el n-grama actual

                    count_list = [posicion_palabra] # reinicia la lista
                    start = posicion_palabra # reinicia variable auxiliar
                    end = posicion_palabra # reinicia variable auxiliar
            # Extrae el ultimo n-grama actual.
            n_grama_aux = end-start+1
            diccGramas[doc][n_grama_aux] = diccGramas[doc].get(n_grama_aux,[])
            diccGramas[doc][n_grama_aux].append( count_list )

        if printData: print "N-gramas ordenados, contiene posiciones:"#,diccGramas
        ## Verificar si existen en F_list_ngrama
        # Para cada n-grama separados por documentos
        for doc in diccGramas: # por cada documento
            for n_grama in diccGramas[doc]: # por cada n-grama en documento x
                if printData: print "----- Documento:", doc, "\t",str(n_grama)+"_grama------"
                for pos_list in diccGramas[doc][n_grama]: # Para cada lista que guarda posiciones del n-grama
                    for pos in pos_list: # Para cada posicion del n-grama actual
                        #[0]: Numero documento
                        #[1]: Concepto
                        #[2]: Tipo (NN)
                        if printData: print self.pos[ doc ][ pos ]#[1] # imprime la informacion del concepto en tal pos
                        
                        
                        
                if printData: print "-------------------------------------------------------"

            ## Eliminar 1-grama ocupados en los 2-gramas, eliminar 2-gramas ocupados por los 3-gramas,etc.
            #diccGramas[doc][n_grama]

            #Iterar de por doc normal - iterar n_grama inverzo - eliminar de yamor n-grama a menor.
            
        
        return diccGramas


#.
class RedSemantica:
    def __init__(self,
                 nameExample,
                 umbral, write,
                 print_concepts,
                 folder,
                 folderInput,
                 delConceptEqual1 = False,
                 printTime = False
                 ):

        self.printTime = printTime
        
        self.delConceptEqual1 = delConceptEqual1
        self.folder = folder
        self.folderInput = folderInput
        self.FullpathExample = nameExample
        self.nameExample = nameExample.split('\\')[-1]
        self.w = Words(self.FullpathExample, self.folderInput)
        self.concepts = {}
        self.verbBetweenC  = {} #verbos que han sido seleccionados entre dos conceptos.
        self.conceptsDoc = {}
        self.conceptsList = []
        self.umbral = self.w.numDocs*umbral
        self.umbralOriginal = int(umbral*100)
        self.frequent_concepts = {}

        self.diccionario_n_grama = {}
        
        # APRIORI - var: conjunto de conceptos por documento para operar en tal algoritmo
        # ver frecuent concepts
        self.dataSet_T = []
        self.umbral_apriori = None
        self.conceptsInforApriori = {}
        

        self.verbs = {} #all verbs
        self.verbsList = []
        self.stopwords = {}
        self.verbsByContex = {}
        self.stopwordsByContex = {}
        doc_to_verb = {}
        doc_to_stopwords = {}

        self.c1 = None
        self.c2 = None
        self.actualIndex = 0
        self.actualDoc = 0
        self.actualParagraph = 0
        self.write = write #Booleano, salida a documento word (.dot)

        self.coOcurrences= nx.Graph()
        self.M_S  = [] # self.M_S: guarda conceptos consecutivos de a pares, para despues buscar verbos a su alrededor.

        self.redSemantica = {}
        
        self.text_to_NN_VB_SW()

        self.frecuentConcetps() #concepts to list
        #APRIORI algoritmo
        if printData: print len(self.dataSet_T),(self.w.numDocs),umbral
        self.umbral_apriori = float(len(self.dataSet_T))/(self.w.numDocs)*umbral
        if printData: print "Resultado umbral apriori", self.umbral_apriori
        self.F, s = apriori(self.dataSet_T, self.umbral_apriori)

        self.diccionario_n_grama = self.w.buscaPalabras(self.conceptsInforApriori, self.F)

        # Modifica self.conceptsList, para luego agregar al self.M_S los n-gramas
        #self.agregar_n_gramas(self.diccionario_n_grama) # Agrega n-gramas al proceso

        # Solución: Modificar matchings en archivo final de salida
        #self.matching(self.diccionario_n_grama) # lo lleve a concepts_to_txt2

        self.verbsToList()#Ordena los verbos
        self.add_to_M_S()
        self.red_semantica()
        
        
        self.write_to_word()
        #nx.draw(self.redSemantica[10])#[0]
        ##nx.draw(self.SS)
        #plt.show()
        if print_concepts:
            self.concepts_to_txt()
            self.concepts_to_txt2(self.diccionario_n_grama)

        #print "==============Zxcx_M_S_zxcv============"
        #print self.M_S
        #print "==============Zxcx_M_S_zxcv============"        


                
    def concepts_to_txt(self):
        try:
            doc_name = self.folder+"1.- Concepts_frec "+self.nameExample+" "+str(self.umbralOriginal)+"% _Frec_"+str(self.umbral/self.w.numDocs)+".txt"
        except:
            "Division por cero, existe un solo documento"
            doc_name = self.folder+"1.- Concepts_frec "+self.nameExample+" "+str(self.umbralOriginal)+"% _Frec_"+str(self.umbral)+".txt"

        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'CONCEPT  - DOCS ID  - CANT DOC\n\n')
            for concepto in self.frequent_concepts:#conceptsList concepts
                # k: concepto
                # self.frequent_concepts[k] : conjunto de numero documentos al que pertenece el concepto
                # 
                documentos = list(set(self.frequent_concepts[concepto]))#, list(set(self.frequent_concepts[k][0]))
                strAux = concepto+"  -  "+ str(documentos)+"  -  "+str(len(documentos))
                f.write(strAux+u'\n')
        f.close()

    def concepts_to_txt2(self, diccGramas):
        try:
            doc_name = self.folder+"1.1.- Concepts_frec "+self.nameExample+" "+str(self.umbralOriginal)+"% _Frec_"+str(self.umbral/self.w.numDocs)+".txt"
        except:
            "Division por cero, existe un solo documento"
            doc_name = self.folder+"1.- Concepts_frec "+self.nameExample+" "+str(self.umbralOriginal)+"% _Frec_"+str(self.umbral)+".txt"
        
        docs_aux = []
        for lista_documentos in self.frequent_concepts.values():
            # lista de documentos, cada lista es al cual pertenece o está el concepto.
            docs_aux.append( list( set(lista_documentos) ) )
        if printData: print "///////////////////////"
        if printData: print self.frequent_concepts
        for doc in diccGramas: # por cada documento
            for n_grama in diccGramas[doc]: # por cada n-grama en documento x                
                for pos_list in diccGramas[doc][n_grama]: # Para cada lista que guarda posiciones del n-grama
                    
                    #print diccGramas[doc][n_grama]
                    #[0]: Numero documento
                    #[1]: Concepto
                    #[2]: Tipo (NN)
                    # info_concept[0], info_concept[1], info_concept[2]


                    #Verificar si todos los conceptos del n-grama son posibles eliminar para luego reemplazarlos
                    aux_string_verify = ""
                    aux_flag = True
                    aux_docs = []
                    for pos in pos_list:
                        info_concept = self.w.pos[ doc ][ pos ]
                        documento = info_concept[0]
                        concepto = info_concept[1]
                        
                        aux_string_verify += concepto+" "
                        
                        if self.frequent_concepts.has_key(concepto) and documento in self.frequent_concepts[concepto]:
                            aux_docs.append(-1) # omite documento
                        else:
                            aux_flag = False
                            aux_docs.append(documento)
                    if  not aux_flag:
                        if printData: print "=======","n-grama false:",aux_string_verify,aux_docs, "======="
                        continue

                    else:                    
                        aux_string = ""
                        for pos in pos_list:
                            info_concept = self.w.pos[ doc ][ pos ]
                            documento = info_concept[0]
                            concepto = info_concept[1]

                            aux_string += concepto+" "

                            if self.frequent_concepts.has_key(concepto) and documento in self.frequent_concepts[concepto]:
                                #print "Reemplazar:",concepto, documento
                                # Quitar elemento
                                try:
                                    self.frequent_concepts[concepto].remove(documento)
                                    if printData: print concepto, documento
                                except:
                                    print "Error34", concepto, documento
                            else:
                                if printData: print "FALSE:",concepto, documento
                        if printData: print "=======",aux_string,"======="
                        #sdf[n_grama_aux] = sdf.get(n_grama_aux,[])
                        self.frequent_concepts[aux_string] = self.frequent_concepts.get(aux_string,[])
                        self.frequent_concepts[aux_string].append(documento)
                    
        
        if printData: print self.frequent_concepts
                    

            
                        
        
        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'CONCEPT  - DOCS ID  - CANT DOC\n\n')
            for concepto in self.frequent_concepts:#conceptsList concepts
                # k: concepto
                # self.frequent_concepts[k] : conjunto de numero documentos al que pertenece el concepto
                # 
                documentos = list(set(self.frequent_concepts[concepto]))#, list(set(self.frequent_concepts[k][0]))
                strAux = concepto+"  -  "+ str(documentos)+"  -  "+str(len(documentos))
                f.write(strAux+u'\n')
        f.close()

                


    #Itera, pasando por todas las palabras.
    def text_to_NN_VB_SW(self):
        countDoc = 0
        self.w.initDocument(countDoc)
        word = self.w.getWord() # numParrafo, word, indice doc, indice palabra.
        wordSinLemmatize = word
        doc_id = 0
        paragraph_id = 0
        word_id = 0
        #NN_ngrama =  [] #Desactiva busqueda de N-Gramas
        while(True):
            try:
                paragraph_id = word[0]
                doc_id = word[2]
                word_id = word[3]
                tag = word[4] 
                word = self.w.remove_punc_upper(word[1])#
                wordSinLemmatize = word
                if not word in stopwords:# No lemma stopwordVB
                    word = lmtzr.lemmatize(word, 'n')#Elimina mayuscula
                    word = lmtzr.lemmatize(word, 'n')#Elimina plural
                    word = word.lower()
                    wordSinLemmatize = wordSinLemmatize.lower()
            except Exception as inst:
                #print type(inst)     # the exception instance
                #print "Index error, word>", word
                word = self.w.getWord()
                if word is None:
                    countDoc += 1
                    self.w.initDocument(countDoc)
                    #print "New Doc:",countDoc
                    NN_ngrama = []
                if countDoc > self.w.numDocs:
                    break
                continue
            if word==" " or "." in word:
                #NN_ngrama = [] #Desactiva busqueda de N-Gramas
                continue                
            #--
            if not word in stopwords:
                if 'NN' in tag:
                    self.save_concept(word, doc_id, paragraph_id, word_id)
                
                if 'VB' in tag:# posible eliminacion, prioridad a los NN.
                    self.save_verb(wordSinLemmatize, doc_id, paragraph_id, word_id)
                """#Desactiva busqueda de N-Gramas
                if 'NN' in tag:
                    self.save_concept(word, doc_id, paragraph_id, word_id)
                    NN_ngrama.append(word)
                else:
                    if len(NN_ngrama)> 1:
                        c_ngrama = ' '.join(NN_ngrama)
                        self.save_concept(c_ngrama, doc_id, paragraph_id, word_id-1) #word_id-1: palabra anterior
                    NN_ngrama = []
                if 'VB' in tag:# posible eliminacion, prioridad a los NN.
                    NN_ngrama = []
                    self.save_verb(wordSinLemmatize, doc_id, paragraph_id, word_id)
                """
            else:#Borrar
                self.save_stopwordVerb(wordSinLemmatize, doc_id, paragraph_id, word_id)
            #--
            word = self.w.getWord()

    # self.frequent_concepts: los 1-grama mas frecuentes, sin nada más de informacion.
    # self.conceptsInforApriori: los 1-grama mas frecuente, con informacion para Apriori
    # Guarda todos los conceptos más frecuentes mayor al umbral dado.
    def frecuentConcetps(self):
        
        auxc = 0
        dataSet_T = {}
        #dataSet_T = []
        for c,tuple_list in self.concepts.items():
            cjto = []            
            for t in tuple_list:
                cjto.append(t[0])
            if len( set(cjto) ) > auxc:
                auxc = len( set(cjto) )
                
            if len( set(cjto) ) >= self.umbral:
                for t in tuple_list:
                    #Concepto entrante ordenado por "c -> doc"
                    self.frequent_concepts[c] = self.frequent_concepts.get(c,[])
                    self.frequent_concepts[c].append(t[0])

                    #c: concepto
                    #t[0]: numero documento
                    #t[1]: parrafo
                    #t[2]: posicion palabra
                    # Ocupado para guardar toda la información de los coneptos (NN)<
                    
                    self.conceptsList.append((c, t))#[0], t[1], t[2]))

                    #print "FC:",c,t
                    self.conceptsInforApriori[c] = self.conceptsInforApriori.get(c,[])
                    self.conceptsInforApriori[c].append( (t[0],t[2]) )
                    #dataSet_T[t[0]] = dataSet_T.get(t[0], {} )
                    #dataSet_T[t[0]][c] = dataSet_T[t[0]].get(c, [] )
                    #dataSet_T[t[0]][c].append( (t[1],t[2]) )

                    #Guarda conceptos frecuentes en dicc como conjunto (evita repitencia)
                    dataSet_T[t[0]] = dataSet_T.get(t[0], set() )
                    dataSet_T[t[0]].add( c )
                    #dataSet_T.append(
        
        
        # Una vez obtenidos los conceptos más frecuentes (1-grama), utilizarlos en algoritmo Apriori
        dataSet_aux = []
        ## -- APRIORI --##
        #Transoformar a lista de listas
        for k in dataSet_T:
            #print k,":", dataSet_T[k]
            dataSet_aux.append( list(dataSet_T[k]) )

        self.dataSet_T = dataSet_aux
        #print dataSet_aux
        for e in dataSet_aux:
            if printData: print e
            
                    
        self.conceptsList = sorted(self.conceptsList, key=lambda x: x[1]) #Conceptos consecutivos.

        
        
    def verbsToList(self): # deprecated
        for c,tuple_list in self.verbs.items():
            for t in tuple_list:
                self.verbsList.append((c, t))#[0], t[1], t[2]))        
        self.verbsList = sorted(self.verbsList, key=lambda x: x[1])
        
    def find_verb(self, c1, doc_id1, par_id1, i1, c2, doc_di2, par_id2, i2):
        if i1 > i2:
            print "ERROR<<< "+c1+":"+c2+" >>>"
        candidates = []
        candidatesSW = [] # Stopword
        for i in range(i1+1, i2):#Extrae todos los candidatos entre 2 conceptos.
            if self.w.pos[doc_id1][i][1] not in stopwords: 
                if 'VB' in self.w.pos[doc_id1][i][2]:
                    aux = lmtzr.lemmatize(self.w.pos[doc_id1][i][1], 'v')
                    candidates.append( aux.lower() )# Forma agresiva.
            else:
                if self.w.pos[doc_id1][i][1] in stopwordsVerbs:
                    candidatesSW.append(self.w.pos[doc_id1][i][1])
        # Caso 1 y 2: hay candidatos entre los conceptos 1 y 2
        if len(candidates) != 0:
            # Caso 1: un candidato
            if len(candidates) == 1:
                self.verbBetweenC[candidates[0]] = self.verbBetweenC.get(candidates[0],[])
                self.verbBetweenC[candidates[0]].append((doc_id1))
                return candidates[0]
            # Caso 2: mas de un candidato
            if len(candidates) > 1: 
                candidate_freq ={} #En todo el doc
                candidate_freq2 ={}#En un doc especifico
                count=0
                for candidate in candidates:#Para cada candidato (verbo) entre los conceptos c1 y c2.
                    try:
                        # Cantidad que se repite el candidato
                        candidate_freq[candidate] = len(self.verbs[candidate])
                        for e in self.verbs[candidate]: # self.verbs[verbo] === (docId, paragraphId, wordId)
                            if e[0]==doc_id1:
                                count+=1 #Cuenta la frecuencia del verbo en un documento especificado
                        candidate_freq2[candidate]=count 
                        count = 0 #Reinicia count
                    except:#Si no ecuentra candidatos, entonces busca candidatos del tipo stopwordVerb.
                        try:
                            candidate_freq[candidate] = len(self.stopwords[candidate])
                            for e in self.stopwords[candidate]:
                                if e[0]==doc_id1:
                                    count+=1
                            candidate_freq2[candidate]=count
                            count = 0
                        except:#Si no encuentra en verbo en los stopwordVerb -> Verbo no es un verbo candidato. ver text_to_NN_VB_ST
                            pass#El verbo entre conceptos no es tomado como verbo, segun la estructura de la oracion.
                        

                #CASO 1: frecuencia del verbo para todo el documento.
                #retorna el mas frecuentes del texto completo.
                seleccionado = sorted(candidate_freq.items(), reverse= True, key=lambda x: x[1])[0]#[0] #(verb, contador)
                self.verbBetweenC[seleccionado[0]] = self.verbBetweenC.get(seleccionado[0],[])
                self.verbBetweenC[seleccionado[0]].append((doc_id1))
                return seleccionado[0]
        #Caso 3: buscar verbo a la izq, 5 palabras, omitir stopwords
        else:
            limite = 5 # limite, numero de palabras hacia atras (omitir stopwords)
            count = 1 # retrocede, se resta al indice del concepto inicial i1.
            verbo_aux = None
            while limite >= 1:
                if not self.w.pos[doc_id1][i1-count][1] in stopwords:
                    limite -= 1
                    if self.w.pos[doc_id1][i1-count][1] == '.':
                        break
                    #try:
                    if 'NN' in self.w.pos[doc_id1][i1-count][2]:
                        break
                    if 'VB' in self.w.pos[doc_id1][i1-count][2]:
                        verbo_aux = lmtzr.lemmatize(self.w.pos[doc_id1][i1-count][1], 'v')
                        break
                count += 1
            return verbo_aux

    # Al final no se encontrará en la wordnet, ya que trabaja con 1-gramas.
    # SOl: Solo contar frecuencia de estas, eliminando ocurrencias en el archivo de salida
    def agregar_n_gramas(self, diccGramas):

        #diccGramas: diccionario de diccionario
        #           [doc][n-grama] (posiciones)
        
        # [(u'state', (0, 0, 14)), -> concepto, (doc, parrafo, posicionWord)
        # self.conceptsList#[0][1][0]: doc
        # self.conceptsList#[0][1][1]: parrafo
        # self.conceptsList#[0][1][2]: pos
        #print self.conceptsList
        if printData: print "asd",self.conceptsList#[0][1][2]
        if printData: print diccGramas
        for doc in diccGramas: # por cada documento
            for n_grama in diccGramas[doc]: # por cada n-grama en documento x
                if printData: print "----- Documento22:", doc, "\t",str(n_grama)+"_grama------"
                for pos_list in diccGramas[doc][n_grama]: # Para cada lista que guarda posiciones del n-grama
                    aux_list_string_n_grama = []
                    for pos in pos_list: # Para cada posicion del n-grama actual
                        #[0]: Numero documento
                        #[1]: Concepto
                        #[2]: Tipo (NN)
                        #print self.pos[ doc ][ pos ]#[1]
                        aux_list_string_n_grama.append(self.w.pos[ doc ][ pos ][1]) #agrega concepto
                    aux_string_n_grama = "_".join(aux_list_string_n_grama)
                    # Si la posicion del primer concepto (pos) esta en self.conceptsList, 
                    # Si mismo doc, 
                    #if self.conceptsList[0][1][0] == doc and

        # Mejor Iterar self.conceptsList
        for tupla in self.conceptsList:
            lista_n_grama = self.busca_n_grama_en(diccGramas, tupla[1][0]) #doc: tupla[1][0]
            for t in lista_n_grama:
                #t[0]: posicion 1 del n-grama
                if t[0] == tupla[1][2]: # posicion1 del n-grama igual a posicion del conepto en la lista de concepto
                    # Eliminar de la lista de conceptos los siguiente
                    pass
                    # Modificar el concepto a n-grama
        # REACER VARIABNLES!!!
        
    def busca_n_grama_en(self, diccGramas, doc):
        list_aux = []
        for n_grama in diccGramas[doc].values():
            list_aux.append(n_grama)
        return list_aux # lista de tuplas que tienen posiciones de los n-gramas
        
        

    def add_to_M_S(self):
        tupla = self.seleccionConcepts()
        while tupla!=None:
            tupla = self.seleccionConcepts()
        
    def red_semantica(self):
        #Preparando variables - conceptos y verbos
        #self.frecuentConcetps() #concepts to list

        ## AQUI
        # Modificar  self.conceptsList
        #self.agregar_n_gramas()
        
        #self.verbsToList()#Ordena los verbos
        #-- Itera agregando conceptos de un contexto a M_S
        #print self.conceptsList
        """
        tupla = self.seleccionConcepts()
        while tupla!=None:
            tupla = self.seleccionConcepts()
        """
        ## AQUI
        start = None
        if self.printTime:
            start = time.time()

        # self.M_S: guarda conceptos consecutivos de a pares, para despues buscar verbos a su alrededor.
        for c1, doc_id1, par_id1, i1, c2, doc_di2, par_id2, i2, rel_type in self.M_S:
            # Busca verbos cercanos a los pares de conceptos guardados en M_S
            verbo = self.find_verb(c1, doc_id1, par_id1, i1, c2, doc_di2, par_id2, i2)
            # redSemantica: diccionario guarda objetos de grafos
            self.redSemantica[doc_id1] = self.redSemantica.get(doc_id1, nx.DiGraph()) # par_id1
            if not self.redSemantica[doc_id1].has_edge(c1,c2):# doc_id, cambiar a doc_id1
                if c1==c2 and verbo == None:
                    continue
                self.redSemantica[doc_id1].add_edge(c1,c2)#Crearla
                self.redSemantica[doc_id1][c1][c2]['label'] = verbo

        if self.printTime: print "Tiempo:", time.time() - start
        
    # Iterar hasta el final.
    # self.M_S: guarda conceptos consecutivos de a pares, para despues buscar verbos a su alrededor.
    def seleccionConcepts(self):
        try:
            t1 = self.conceptsList[self.actualIndex]#[1]#[self.actualParagraph]
            t2 = self.conceptsList[self.actualIndex+1]            
        except Exception as inst:
            return None
        
        if t1[1][0] == t2[1][0] and t1[1][1] == t2[1][1]: #Mismo doc y mismo contexto.
            self.actualIndex+=1
            rel_type = 'Normal'
            if self.is_superset(list(set(self.conceptsDoc[t1[0]])), list(set(self.conceptsDoc[t2[0]])) ): # Error. // Cambiado
                rel_type = 'Super'
            self.M_S.append((t1[0], t1[1][0], t1[1][1], t1[1][2],t2[0], t2[1][0], t2[1][1], t2[1][2],rel_type))
            return (t1, t2)
        else:#aumentar indice para siguiente contexto
            self.actualIndex+=1
            return (None,None)

    def is_superset(self, l1,l2):
        if len(set(l2) - set(l1)) == 0: #Elimina elementos de l2.
            return True
        return False 
    def save_concept(self, word, doc_id, paragraph_id, word_id):#Dividirlos en contextos.

        if self.delConceptEqual1:
            if len(word) == 1:
                return
        
        word = lmtzr.lemmatize(word, 'n').lower()
        
        self.concepts[word] = self.concepts.get(word,[])
        self.concepts[word].append((doc_id, paragraph_id, word_id))
        
        self.conceptsDoc[word] = self.conceptsDoc.get(word,[])
        self.conceptsDoc[word].append(doc_id)
        
    def save_verb(self, word, doc_id, paragraph_id, word_id):
        word = lmtzr.lemmatize(word, 'v')
        self.verbs[word] = self.verbs.get(word,[])
        self.verbs[word].append((doc_id, paragraph_id, word_id))
 
    def save_stopwordVerb(self, word, doc_id, paragraph_id, word_id): #No usada
        if word in stopwordsVerbs:
            self.stopwords[word] = self.stopwords.get(word,[])
            self.stopwords[word].append((doc_id, paragraph_id, word_id))

    def write_to_word(self):
        if self.write:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            try:
                folder_name = self.folder+"2.- RS_by_doc umbral_"+self.nameExample+" "+str(self.umbralOriginal)+"% _Frec_"+str(self.umbral/self.w.numDocs)+".txt"
            except:
                "Hay un solo documento, el inicial 0 (Division por 0 error)."
                folder_name = self.folder+"2.- RS_by_doc umbral_"+self.nameExample+" "+str(self.umbralOriginal)+"% _Frec_"+str(self.umbral)+".txt"
            folder_dest = os.path.join(script_dir, folder_name)
            try:
                os.makedirs(folder_dest)
            except OSError:
                pass # already exists

            for doc_id in self.redSemantica:
                doc_name = folder_name+'/redes_'+str(doc_id)+'.dot'
                with io.open(doc_name, 'w', encoding='utf-8') as f:
                    for edge_tupla in self.redSemantica[doc_id].edges(data=True):
                        f.write(u" "+edge_tupla[0]+ " -> " + edge_tupla[1] + "\t[label="+ str(edge_tupla[2]['label']) +'];\n')
                f.close()


class Meme:
    def __init__(self, nameExample, umbral, write=False,
                 print_concepts=False, excepts=False,
                 print_meme=False, print_prob_con_dist_meme=False,
                 ro=1, sigma=1, print_resultados=False,
                 print_all_memes=False, fecha="None", folderInput="Files",
                 tm_list=[1,2],
                 delConceptEqual1 = False,
                 printTime = False):
        self.printTime = printTime
        #Borra conceptos de largo igual a 1
        self.delConceptEqual1 = delConceptEqual1
        #Archivos de entrada txt utf8
        self.folderInput = folderInput
        #TM LIST - equal similar ...
        self.tm_list = tm_list
        #Crear carpeta - contiene todos los archivos creados
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.fecha = fecha
        self.nameExample = nameExample.split('\\')[-1]
        self.fullPathExample = nameExample
        self.folder = self.fecha+"/"+self.nameExample+"_"+str(umbral*100)+"% _Ro"+str(ro)+"_Sigma"+str(sigma)+"/"
        folder_dest = os.path.join(script_dir, self.folder)
        try:
            os.makedirs(folder_dest)
        except OSError:
            pass # already exists

        self.print_resultados = print_resultados
        self.print_all_memes = print_all_memes
        self.wordExcept = []
        #self.wordProbCon = []
        
        self.s = RedSemantica(
            self.fullPathExample,
            umbral, write, print_concepts,
            self.folder,self.folderInput,
            self.delConceptEqual1,
            self.printTime)
        
        self.RS = self.s.redSemantica

        self.tau = 0.3#0.3
        self.sigma = sigma
        self.ro = ro
        
        self.memes = {}
        self.sort_lexicographically()

        # Calcula IC de los conceptos mas frecuentes.
        
        self.frec = {}        
        self.calc_frec()# Calcula las frecuencias de todos los conceptos
        
        self.N = 0
        self.cal_N() # calcula el N. Sumatoria de las frecuencias
        
        self.IC = {}
        self.calc_IC() # Calcula los IC de todos los conceptos
        
        
        
        #Paso final.
        self.memesEscogidos = {} # Diccionario resultados de memes iguales o similares.
        start = None
        if self.printTime:
            print "Escoger memes de acuerdo a tm (algoritmo principal)"
            start = time.time()
        self.largoMasFrecuente = self.escogerMemes() #Retorna el largo del meme mas frecuente.
        if self.printTime: print "Tiempo:", time.time() - start

        #to txt.
        if excepts:
            self.excepts_to_txt()
        if print_meme:
            self.memes_tm_1_2_to_txt()
        if print_prob_con_dist_meme:
            self.prob_to_txt()
        if self.print_resultados:
            self.resultados()
        if self.print_all_memes:
            self.all_memes()

    def escogerMemes(self):
        li = []
        for m1 in self.memes:
            li.append(m1)# guarda indices/numeros de los memes.
            
        memeSimilar = {}
        masLargo = 0 #Meme mas largo.
        for i in range(0,len(li)):
            count = 0
            for i2 in range(0,len(li)):
                if li[i] != li[i2]:
                    tm = self.matching(self.memes[li[i]], self.memes[li[i2]])
                    #if tm==1 or tm==2: #Si son iguales o similares
                    if tm in self.tm_list:
                        count += 1 
                        memeSimilar[li[i]] = memeSimilar.get(li[i], [])
                        memeSimilar[li[i]].append((self.memes[li[i]][0][3], self.memes[li[i2]][0][3], tm, li[i],li[i2]))
            if count > masLargo:
                masLargo = count

        self.memesEscogidos =  memeSimilar
        return masLargo

    def matching(self, m1, m2):
        if len(m1)==len(m2):#Igual
            dist = self.distmeme(m1, m2, flag=False)#flag: imprime dists False True
            if dist==0:
                return 1
            else:
                if 0 < dist <= self.tau:
                    return 2
                    
        elif len(m1)<len(m2):#
            dist = []
            for i in range(0, len(m2)-len(m1)+1):
                dist.append(self.distmeme( m1 , m2[i: i+len(m1)])) #
            dist = (sorted(dist))[0]
            if dist==0:
                return 3
            if 0 < dist <= self.tau:
                return 4
            
        else:#m1 > m2
            dist = []
            for i in range(0, len(m1)-len(m2)+1):
                dist.append(self.distmeme( m1[i: i+len(m2)] , m2)) #
            dist = (sorted(dist))[0]
            if dist==0:
                return 5
            if 0 < dist <= self.tau:
                return 6
        return 0

    def distmeme(self, m1, m2, flag=False):#BORRAME
        sumaDistCon1 = 0
        sumaDistCon2 = 0
        sumaRel = 0
        for i in range(0,len(m1)):
            sumaDistCon1 += self.dist_con(m1[i][0],m2[i][0])
            sumaDistCon2 += self.dist_con(m1[i][1],m2[i][1])
            sumaRel += self.dist_rel(m1[i][2],m2[i][2])
            if flag:
                print "(*)",m1[i][0],m2[i][0],sumaDistCon1,"+",m1[i][1],m2[i][1], sumaDistCon2,"+", m1[i][2],m2[i][2],sumaRel
        return self.ro*((sumaDistCon1 + sumaDistCon2)/2) + self.sigma*sumaRel
            
    #De Digraph a lista, luego ordena lexicographicamente.
    def separarGrafos(self):
        #Separar Digraph
        #ud=d.to_undirected()
        #hl=nx.connected_component_subgraphs(ud)
        #for l in hl: for e in l.edges(): print e
        #CASO1: no mover c1 y c2.
        #Separa grafos conectados.
        count = 0
        for doc_id in self.s.redSemantica:
            ud = self.s.redSemantica[doc_id].to_undirected()
            hl = nx.connected_component_subgraphs(ud)
            #for t in self.s.redSemantica[doc_id].edges():   
            for l in hl:
                #print len(l)
                for t in l.edges():
                    self.memes[count] = self.memes.get(count, [])
                    try:
                        self.memes[count].append((t[0],
                                                  t[1],
                                                  self.s.redSemantica[doc_id][ t[0] ][ t[1] ]['label'],
                                                  doc_id))
                    except:
                        self.memes[count].append((t[0],
                                                  t[1],
                                                  self.s.redSemantica[doc_id][ t[1] ][ t[0] ]['label'],
                                                  doc_id))                    
                    
                count += 1
        
    def sort_lexicographically(self):
        self.separarGrafos()
        
        #Orden Lexicografico
        """for k in self.memes:
            self.memes[k] = sorted(self.memes[k])
            #print self.memes[k]"""


    def dist_con(self, c1, c2):
        if c1 == c2:
            return 0
        #No existe c1 en corpus. Ej, n-gramas.
        try:
            l = ['abstraction', None,'None', 'entity', 'object', 'attribute', 'psychological_feature']
            superior = self.LSup(c1,c2)
            Lc1c2 = self.IC_sup(superior)
            if superior in l:
                Lc1c2 = 0.0
            d = self.IC[c1] + self.IC[c2] - 2*Lc1c2
            if d <= 2:
                return 0.0
            else:
                return (d-2) / math.log( float(self.N)**2 ,2)
        #c1 o c2, no econtrado en el corpus.
        except:
            return 1.0
    
    def dist_rel(self, r1, r2):#DUDA
        if (r1 is None) and (r2 is not None):
            return min([self.dist_rel('be',r2), self.dist_rel('have',r2)])

        elif (r1 is not None) and (r2 is None):
            return min([self.dist_rel(r1,'be'), self.dist_rel(r1,'have')])


        #distancia entre r1 y r2 del arbol / largo de la rama
        if r1==r2:
            return 0.0
        flag1 = False#Except parches
        flag2 = False#Except parches
        s = wn.synsets(r1, wn.VERB)
        
        try:#Except parches
            #r2 = lmtzr.lemmatize(r2, 'v')+'.v.01'  # None.v.01  no existe.
            r2 = lmtzr.lemmatize(r2, 'v')  # None.v.01  no existe.
            #s2 = wn.synset(r2)
        except:#Except parches
            flag2 = True
            self.wordExcept.append(r2+' - v')
            
        if flag2 or len(s)==0:
            return 0.0#Except parches
        
        #Reemplazar ' ' por '_'
        if ' ' in r1 or ' ' in r2:
            print "WARNING espacio",r1, r2 ,s #, s2
        l = []
        
        for e in s:#Para cada definicion de r1
            dist = e.hypernym_distances()
            for arbol in e.hypernym_paths():#Arbol de def hacia abajo
                for syns in arbol:#cada def tiene un cjto de synset (para cada nivel del arbol)
                    if r2 in syns.lemma_names():#cada cjto de synset tiene lemmas, si r2 esta en los lemmas
                        for i in dist:#Buscar su distancia
                            if i[0] == syns:
                                l.append( (i[1] , len(dist)-1) )
        
        l = sorted( l, key=lambda x: x[0]) #ORdena por 1er elemento de tupla, no del segundo
        if len(l)==0:
            return 1.0 # No match exists
        seleccion = l[0]
        if seleccion[0] > seleccion[1]:
            print "Error 726", l[0],l[1],r1,r2
        #Sin saltos, solo posee una hoja. ej expect , look
        if seleccion[1]==0:
            return 0.0
        return (float(seleccion[0]) /seleccion[1])  #self.lengh(r1,r2)/self.lenght2(r1,r2)

    #Calcula el IC y los guarda en un diccionario. N: #archivos del corpus.
    def calc_IC(self):
        for k in self.s.concepts:
            #Si existe en el corpus
            try:
                self.IC[k] = -math.log(self.frec[k]/float(self.N) , 2)
            except:
                pass
    def calc_frec(self):
        for k in self.s.concepts:
            #Si existe en el corpus
            try:
                self.frec[k] = corpus[k]
            #Si no existe en el corpus. Ejemplo los n-gramas.
            except:
                #REVISAR
                #sol: promedio de frecuencia de los n-gramas?
                n_grama = k.split(" ")
                num_gramas = len(n_grama)
                suma = 0
                for i in n_grama:
                    #i = lmtzr.lemmatize(i, 'n')#.lower()
                    try:
                        suma += corpus[i]
                    #Bug 482: Some nouns not being lemmatised by WordNetLemmatizer().lemmatize
                    except:#Solution: quitar la 's' final en la palabra.
                        try:
                            suma += corpus[i[:-1]]
                        #La palabra no existe en el corpus. Ej "obamacare"
                        except:
                            pass
                #Si el n-grama no se econtro
                promedio = suma / num_gramas
                if promedio != 0:
                    self.frec[k] = promedio#corpus[k]
                    
    def cal_N(self):
        self.N = 0
        for k in self.frec:
            self.N += self.frec[k]
            
    #Calcula el IC de un concepto superior. Como abstraction, object, ...
    def IC_sup(self, c):
        #Si c==None, es porque no se econtro un LSup para c1 o c2 en la wordnet.
        if c==None:
            return 0.0 
        try:
            return -math.log(corpus[c]/ float(self.N), 2) 
        #Palabra sup no está en el corpus. Ejemplo "definite_quantity"
        except:
            return 0.0 

    def LSup(self, c1, c2):
        flag1=False
        flag2=False
        try:
            s1 = wn.synset(lmtzr.lemmatize(c1)+'.n.01') #lmtzr.lemmatize(c1)  c1
        except:
            flag1=True
            self.wordExcept.append(c1+' - c')
            #print c2
        try:
            s2 = wn.synset(lmtzr.lemmatize(c2)+'.n.01') # solo el primero de las definiciones
        except:
            flag2=True
            self.wordExcept.append(c2+' - c')
        # Retornar None, cuando no se encuentra en la wordnet el c1 o c2
        if flag1 or flag2:
            return None
        
        seleccion = s1.lowest_common_hypernyms(s2)
        return seleccion[0].name().split('.')[0]#s1.lowest_common_hypernyms(s2)

    
    def excepts_to_txt(self):
        doc_name = self.folder+"3.1.- EXCEPT.umbral_"+str(self.s.umbral/self.s.w.numDocs)+"_Frec_"+str(self.s.umbralOriginal)+"_Concepts__"+self.s.nameExample+".txt"
        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'WORD - c:concept, v:verb \nCantidad de palabras en except:'+str(len(self.wordExcept))+'\n\n')
            for e in list(set(self.wordExcept)):#conceptsList concepts
                f.write(e+u'\n')
        f.close()
    def memes_tm_1_2_to_txt(self):
        try:
            doc_name = self.folder+"3.- Meme.umbral_"+self.s.nameExample+" "+str(self.s.umbralOriginal)+"% _Frec_"+str(self.s.umbral/self.s.w.numDocs)+".txt"
        except:
            doc_name = self.folder+"3.- Meme.umbral_"+self.s.nameExample+" "+str(self.s.umbralOriginal)+"% _Frec_"+str(self.s.umbral)+".txt"
        #Ordena memes
        guardar_memes = []
        for e in self.memesEscogidos: #Para cada ID de self.meme
            memeID2 = []
            docID2 = []
            for i in self.memesEscogidos[e]:#DocIdMeme1, DocIdMeme2, tm, memeId1, memeId2
                memeID2.append( i[4] )
                docID2.append( i[1] ) #los doc de memes similares|iguales
            docID2 = list(set(docID2))
            
            #Contar los "c" diferentes, "r":contar rel no vacias.
            conceptos = []
            relaciones = []
            for m1 in self.memes[e]:
                if not m1[0] in conceptos:
                    conceptos.append(m1[0])
                if not m1[1] in conceptos:
                    conceptos.append(m1[1])
                if (not m1[2] in relaciones) and m1[2]!=None :
                    relaciones.append(m1[2])
            # append - numero meme1, meme1, IDmeme2, , cantidad referencias, cantidad de conceptos distintos, cantidad de rela distintas.
            guardar_memes.append( (e, self.memes[e] , memeID2 , ( len(memeID2) , len(docID2) ,len(conceptos) ,  len(relaciones)) ))
            # Ordenar con mas de 1 elemento? D:
            guardar_memes = sorted(guardar_memes, key=lambda t: t[3], reverse=True)

        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'#Numero Meme: [ contenido del meme incluye num doc ] -> [memeId, memeId, ...]\nCantidad_conceptos_distintos, cantidad_relaciones_no_vacias\n\n')##MemeMasFrecuente:'+str(self.largoMasFrecuente)+u'\n\n')
            for g in guardar_memes:
                f.write(u'#'+str(g[0])+u'-Meme: '+str(g[1])+u' -> '+str(g[2])+
                        u'\nCantidad_doc_distintos:'+str(g[3][1])+
                        u'\nCantidad_conceptos_distintos:'+str(g[3][2])+
                        ', cantidad_relaciones_no_vacias:'+str(g[3][3])+
                        '\n\n')
        f.close()

    
    """def prob_to_txt(self):
        doc_name = "prob_con.umbral_"+str(self.s.umbral/self.s.w.numDocs)+"_Frec_"+str(self.s.umbralOriginal)+"_Concepts__"+self.s.nameExample+".txt"
        with io.open(doc_name, 'w', encoding='utf-8') as f:
            #f.write(u'CONCEPT  - DOCS ID  - CANT DOC\n\n')
            f.write(u'Dist_concept -> c1,c2 -> c en comun \n\n')
            for e in list(set(self.wordProbCon)):#c
                f.write(str(e)+u'\n')
        f.close()"""

    def all_memes(self):
        doc_name = self.folder+"6.- ALL_MEMES_"+self.s.nameExample+" "+str(self.s.umbralOriginal)+"%.dot"
        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u" Todos los memes \n") 
            for m1 in self.memes:
                f.write(u" #-"+str(m1)+": "+str(self.memes[m1])+"\n\n")
        f.close()

    def resultados(self):
        # Variable para guardar las relaciones
        relaciones = []
        relacion_frec = []
        
        # Extrae los elementos, tranformandolos a listas de listas ordenadas.
        lista = []
        lista2 = []
        lista2Sorted = []
        relaciones_doc = {}

        doc_name = self.folder+"4.- Resultado_final_RS_"+self.s.nameExample+" "+str(self.s.umbralOriginal)+"%.dot"
        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'Redes semanticas \n\n')
            for doc in self.s.redSemantica:                
                for l1 in self.s.redSemantica[doc].edges(data=True):
                    #Guarda en variables
                    lista2.append( [ l1[0], l1[1]] ) #, l1[2]['label']) )# sorted([ l1[0], l1[1]])
                    #Guarda en documento. beneficiary -> room	 [label=increase];
                    f.write(u" "+l1[0]+ " -> " + l1[1] + "\t[label="+ str(l1[2]['label']) +'];\n') 
                        
                    if l1[2]['label'] is None:
                        continue
                    relaciones.append( l1[2]['label'] )
                    relaciones_doc[ l1[2]['label'] ] = relaciones_doc.get( l1[2]['label'] ,[])
                    relaciones_doc[ l1[2]['label'] ].append( doc ) #Doc
        
        
        f.close()
        # Guarda las frecuencias de pares de conceptos
        list_pares_con_frec = []
        auxList = []
        for tupla in lista2:
            if not tupla in auxList:
                if tupla[0] != tupla[1]:
                    list_pares_con_frec.append( (
                        tupla,                
                        lista2.count( [tupla[0], tupla[1]] )
                        ) )
                    
                else:
                    list_pares_con_frec.append( (
                        tupla,                
                        lista2.count( [tupla[0], tupla[1]] )
                        ) )
                auxList.append( tupla )
            
        #------------------------------------------------------------------------------------------------------
        #Guarda las frecuencias de cada relacion
        for r in set(relaciones):
            relacion_frec.append( (r, relaciones.count( r ), set(relaciones_doc[r]) ) )


        # Ordena por frecuencia
        relacion_frec = sorted(relacion_frec, reverse= True, key=lambda x: x[1])
        list_pares_con_frec = sorted(list_pares_con_frec, reverse= True, key=lambda x: x[1])

        doc_name = self.folder+"5.- Resultado_Final_"+self.s.nameExample+" "+str(self.s.umbralOriginal)+"%.dot"
        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'((concepto1, concepto2), frecuencia) \n\n')  
            # Imprime las frecuencias de los pares de coneptos
            for e in list_pares_con_frec:
                f.write( u'('+str(e[0][0])+','+str(e[0][1])+') '+str(e[1])+'\n')
            # Imprime las relaciones frecuentes
            f.write(u'\n\n(relacion, frecuencia, [docs]) \n\n') 
            for e in relacion_frec:
                f.write( u''+str(e)+'\n')
             
        f.close()

        

        
        

    
    
"""
RS_to_words = True # False True #escribir las redes semanticas a documentos .dot
print_concepts = True # False True
print_excepts_in_meme = False # False True
print_meme_tm_1_2 = True #Imprime los memes iguales o
print_prob_con_dist_meme = False #Deprecated, imprime conceptos que no se econtraron en el texto (meme)
print_resultados = True
print_all_memes = True

#ro = [0.3, 0.5, 0.7]
#sigma = [0.7, 0.5, 0.3]
ro = [0.5]
sigma = [0.5]


examples = [
    #'example.txt',
    #'black_history_month.txt',
    #'decline_of_unions.txt',
    #'gun_debate.txt',
    #'immigration.txt',
    #'obamacare_original.txt',
    'obamacareText2.txt',
    #'obamacare_text3.txt',
    #'gun_debate_3.txt',
    ]
umbrales = [
    #0.05,
    #0.1,
    #0.2,
    #0.3,
    0.4,
    #0.5,
    #7,
    ]
fecha = "01.Enero/40%"
for e in examples:
    for umbral in umbrales:
        for i in range(0,len(ro)):            
            #try:
            Meme( e, umbral,
                  RS_to_words,
                  print_concepts,
                  print_excepts_in_meme,
                  print_meme_tm_1_2,
                  print_prob_con_dist_meme,
                  ro[i],
                  sigma[i],
                  print_resultados,
                  print_all_memes,
                  fecha)
            #except:
                #print "Error en "+e+", con umbral ",umbral

"""
        
