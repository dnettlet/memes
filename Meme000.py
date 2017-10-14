# Copyright (C) 2017  Héctor Beck-Fernandez(hbeck@uta.cl), David F. Nettleton (david.nettleton@upf.edu), Lorena Recalde, Diego Saez-Trumper, Alexis Barahona-Peñaranda
# License: GNU GENERAL PUBLIC LICENSE v3.0   See LICENSE for the full license.

# -*- coding: cp1252 -*-
#import matplotlib.pyplot as plt #UnUsed < see linea 162
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

#APRIORI ALGORITHM
from apriori import apriori
printData = False

#Word management, indexing.
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

        self.read_example() # Read text
        self.indexing()     # Index

        self.actualParagraph = 0
        self.actualDoc = 0
        self.actualWord = 0
        if printData: print "Number of documents",self.numDocs
        #for e in self.pos:
            #print self.pos[e],"\n"

        

    def read_example(self, delimiter='=================================='):
        #with codecs.open(self.folderInput+"/"+self.FullpathExample,'r','utf-8') as f:#data/ 'example1.txt' #,'utf-8'
        with codecs.open(self.FullpathExample,'r','utf-8') as f:
            self.text = f.read()
        # See module "Interfaz" .fix_txt()
        self.text = self.text.replace(u'\u2019','\'') #Problem single quotes.
        self.text = self.text.replace(u'\u2018','\'') #Problem single quotes.
        self.text = self.text.replace(u'\u201c','"') #Problem double quotes.
        self.text = self.text.replace(u'\u201d','"') #Problem double quotes.        
        self.text = self.text.replace(u'\u2014',' ') #Problem unicode —.
        #u' '     ´  -> '
        self.text = self.text.replace('\r','\n')
        #Cleaning text stopword - AGREGATE MORE
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

    # Separate text in context
    def indexing(self):        
        for doc_id, doc in enumerate(self.documents):#dividing into documents
            contex = re.split('\.[\ |\n+]+', doc) #dividing into paragraphs
            for e in contex:
                if e==" ":
                    contex.remove(' ')
                if e=="":
                    contex.remove('')
            for context_id, p in enumerate(contex):# dividing into words
                p = self.remove_punc_upper(p.replace('\n',' ')) # Eliminate signs
                self.paragraph[doc_id] = self.paragraph.get(doc_id,[])
                self.paragraph[doc_id].append(p)

                for c, t in nltk.pos_tag((p).split()): #Agregate the tag NN VB ... to all the words
                    self.pos[doc_id] = self.pos.get(doc_id,[])
                    self.pos[doc_id].append((context_id, c, t)) #context_id=Number of paragraph in document
                try:
                    self.pos[doc_id].append((context_id, '.', None)) #End of paragraph
                except:
                    pass
                self.numParagraph[doc_id] = context_id
            self.numDocs = doc_id
        #The number of the word is assigned by its position in which it was aggregated to the list

    def initDocument(self, doc_id):
        if doc_id > self.numDocs:
            return None        
        self.actualDoc = doc_id
        self.actualParagraph = 0
        self.actualWord = 0

    # Advance by word. Before must initialize a document.
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

        # diccListTuple: positions of all the 1-gram Info apriori
        # F_list: output of the Apriori algorithm
        
        #print self.pos
        #Obtain a specific word
        #print self.pos[self.actualDoc][self.actualWord]
        
        """
        ## -- Test random words in the most frequent #conceptos".
        print "WORD: ",self.pos[2][33] #insurance  -->  (parrafo, concepto, tag)
        print "WORD 2: ",self.pos[2][33][0] #insurance  --> parrafo
        print "WORD: ",self.pos[14][243] #care
        print "WORD: ",self.pos[16][44] #people
        print "WORD: ",self.pos[3][1] #state
        # OK
        # tuple output ( paragraph , concept , tag )
        """
        ## DATA
        #self.pos[ doc ][ pos_palabra -1 ] === tuple of the previous word (article, adverb, etc)
        #self.pos[ doc ][ pos_palabra +1 ] === tuple of the following word
        #self.pos[ doc ][ pos_palabra ][ 0 ] === Paragraph number
        #self.pos[ doc ][ pos_palabra ][ 1 ] === concept
        #self.pos[ doc ][ pos_palabra ][ 2 ] === tag -- NN

        # List which stores the positions of the 2-gram concepts which have been found
        closed_dicc_list = {}
        
        # 1.- Prepare F2_aux: contains all possible combinations of 2 grams
        F2_grama_aux = set()
        try:
            F_list[1]
        except:
            aux = {}
            return aux
        for item_frozenset in F_list[1]:
            if len(item_frozenset) != 2:
                print "ERROR!, F[1] is not a 2-gram"
                break
            c1, c2 = item_frozenset
            F2_grama_aux.add( c1+" "+c2 )
            F2_grama_aux.add( c2+" "+c1 )

        if printData: print "Auxiliar list of 2-gram combinations", F2_grama_aux
       
        if printData: print "========================================"
        # 2.- Iterate on the complete diccListTuple, which contains the positions of all the 1-gram concepts
        # diccListTuple = { A:[ (0, 14), ... ], ... }
        for concepto in diccListTuple:
            # concept: the currently selected word                        
            for tupla_poscicion in diccListTuple[concepto]: #
                # tupla_poscicion: (num_document, position concept in given document)
                doc, posicionPalabra = tupla_poscicion

                #Obtain close words
                palabra_posterior   = self.pos[ doc ][ posicionPalabra +1 ][1] # (paragraph, concept, tag)
                palabra_anterior    = self.pos[ doc ][ posicionPalabra -1 ][1]

                concepto_2_grama_posterior  = concepto+" "+palabra_posterior
                concepto_2_grama_anterior   = palabra_anterior+" "+concepto

                if printData: print "Convinacion:",concepto.upper()+" "+palabra_posterior," \t; ", concepto_2_grama_anterior+" "+concepto.upper()

                # 3.- Verifify if the '1-gram pairs' are in the auxiliar 2-gram list (all combinations of 2 grams)
                if concepto_2_grama_posterior in F2_grama_aux:
                    closed_dicc_list[doc] = closed_dicc_list.get(doc,[])
                    closed_dicc_list[doc].append( posicionPalabra )
                    closed_dicc_list[doc].append( posicionPalabra + 1 )
                    if printData: print "\t\t2-gram found:", concepto_2_grama_posterior
                    
                if concepto_2_grama_anterior in F2_grama_aux:
                    closed_dicc_list[doc] = closed_dicc_list.get(doc,[])
                    closed_dicc_list[doc].append( posicionPalabra - 1 )
                    closed_dicc_list[doc].append( posicionPalabra )
                    if printData: print "\t\t2-gram found:", concepto_2_grama_anterior
        if printData: print "========================================"
        if printData: print "CLOSED LIST: ",closed_dicc_list

        
        if printData: print "======= 4.- Preparing n-grams ========"
        ## 4.- Prepare F_list_ngrama: must be a list of n-gram concepts -> [ 'A B', 'A B C',..
        F_list_ngrama = []
        """
        #               1-grams             2-grams           3-grams        n-gram
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

        if printData: print "====List n-grams, accordingto the output of the set F(k) in Apriori===="
        if printData: print F_list_ngrama

        # diccGramas: dictionary of dictionary
        # diccGramas: diccGramas[number_document][n_gram]
        diccGramas = {} # dictionary save the n-grams to search for, separate them by document.
        ## 5.- Search n-grams in the closed_dicc_list using the F_list_ngram ('A B',...)
        if printData: print "====Ordered set===="
        for doc in closed_dicc_list:
            diccGramas[doc] = diccGramas.get(doc, {})
            
            #closed_dicc_list[doc] : list of positions in given document (doc) :: [ 4,5,6,2,8,4,5,3,4,5,... ]
            lista_posiciones = sorted(set(closed_dicc_list[doc])) # Closed list without repeated elements.
            #print "==",lista_posiciones
            
            ## Search for continuous positions
            start = lista_posiciones[0] # Initial position of the n-gram (auxiliar)
            end = lista_posiciones[0]   # Final position of the n-gram (auxiliar)
            #print start, end, lista_posiciones
            #dicc = {}
            count_list = [start] # positions of the n-gram (auxiliar) - Final:[4,5,6] -> 4:Start, 5:End.
            for posicion_palabra in lista_posiciones[1:]: # Omit position zero, starts at this.
                #print posicion_palabra,"-->",self.pos[ doc ][ posicion_palabra ][1]
                if (end+1) == posicion_palabra: # if the next word is contiguous position - Example 5,6
                    end = posicion_palabra
                    count_list.append(posicion_palabra) # aggregate to the auxiliar list of the current n-gram
                else: # If not contiguous calculate range and save
                    n_grama_aux = end-start+1 # Calcula rango
                    
                    #for i in range(start,end+1):
                    diccGramas[doc][n_grama_aux] = diccGramas[doc].get(n_grama_aux,[])
                    diccGramas[doc][n_grama_aux].append( count_list ) # Save the current n-gram

                    count_list = [posicion_palabra] # reinitialize the list
                    start = posicion_palabra # reinitialize auxiliar variable
                    end = posicion_palabra # reinitialize auxiliar variable
            # Extract the last current n-gram.
            n_grama_aux = end-start+1
            diccGramas[doc][n_grama_aux] = diccGramas[doc].get(n_grama_aux,[])
            diccGramas[doc][n_grama_aux].append( count_list )

        if printData: print "Ordered N-grams, contains positions:"#,diccGramas
        ## Verify if exist in F_list_ngrama
        # For each n-gram which is separated by document
        for doc in diccGramas: # for each document
            for n_grama in diccGramas[doc]: # for each n-gram in document x
                if printData: print "----- Document:", doc, "\t",str(n_grama)+"_gram------"
                for pos_list in diccGramas[doc][n_grama]: # For each list which stores positions of n-gram
                    for pos in pos_list: # For each position of the current n-gram
                        #[0]: Document number
                        #[1]: Concept
                        #[2]: Type (NN)
                        if printData: print self.pos[ doc ][ pos ]#[1] # print the information of the concept in given position
                        
                        
                        
                if printData: print "-------------------------------------------------------"

            ## Eliminate 1-gram occupied by the 2-grams, eliminate 2-grams occupied by the 3-grams,etc.
            #diccGramas[doc][n_grama]

            #Iterate for normal doc - iterate n_gram inversely - eliminate from major n-gram to minor.
            
        
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
        self.verbBetweenC  = {} #verbs that have been selected between two concepts.
        self.conceptsDoc = {}
        self.conceptsList = []
        self.umbral = self.w.numDocs*umbral
        self.umbralOriginal = int(umbral*100)
        self.frequent_concepts = {}

        self.diccionario_n_grama = {}
        
        # APRIORI - var: set of concepts by document to operate with given algorithm
        # see frequent concepts
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
        #APRIORI algorithm
        if printData: print len(self.dataSet_T),(self.w.numDocs),umbral
        self.umbral_apriori = float(len(self.dataSet_T))/(self.w.numDocs)*umbral
        if printData: print "Result of apriori threshold", self.umbral_apriori
        self.F, s = apriori(self.dataSet_T, self.umbral_apriori)

        self.diccionario_n_grama = self.w.buscaPalabras(self.conceptsInforApriori, self.F)

        # Modify self.conceptsList, to later aggregate the self.M_S the n-grams
        #self.agregar_n_gramas(self.diccionario_n_grama) # Agregate n-grams to the process

        # Solution: Modify matchings in final output file
        #self.matching(self.diccionario_n_grama) # takes it to concepts_to_txt2

        self.verbsToList()#Order the verbs
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
            "Divide by zero, only one document exists"
            doc_name = self.folder+"1.- Concepts_frec "+self.nameExample+" "+str(self.umbralOriginal)+"% _Frec_"+str(self.umbral)+".txt"

        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'CONCEPT  - DOCS ID  - CANT DOC\n\n')
            for concepto in self.frequent_concepts:#conceptsList concepts
                # k: concept
                # self.frequent_concepts[k] : set of number of documents to which the concept belongs
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
            # list of documents, each list is the one to which it belongs or in which the concept is present.
            docs_aux.append( list( set(lista_documentos) ) )
        if printData: print "///////////////////////"
        if printData: print self.frequent_concepts
        for doc in diccGramas: # for each document
            for n_grama in diccGramas[doc]: # for each n-gram in document x                
                for pos_list in diccGramas[doc][n_grama]: # For each list that stores positions of the n-gram
                    
                    #print diccGramas[doc][n_grama]
                    #[0]: Numero documento
                    #[1]: Concepto
                    #[2]: Tipo (NN)
                    # info_concept[0], info_concept[1], info_concept[2]


                    #Verify if all the concepts of the n-grams are possible eliminate to later replace them
                    aux_string_verify = ""
                    aux_flag = True
                    aux_docs = []
                    for pos in pos_list:
                        info_concept = self.w.pos[ doc ][ pos ]
                        documento = info_concept[0]
                        concepto = info_concept[1]
                        
                        aux_string_verify += concepto+" "
                        
                        if self.frequent_concepts.has_key(concepto) and documento in self.frequent_concepts[concepto]:
                            aux_docs.append(-1) # omit document
                        else:
                            aux_flag = False
                            aux_docs.append(documento)
                    if  not aux_flag:
                        if printData: print "=======","false n-gram:",aux_string_verify,aux_docs, "======="
                        continue

                    else:                    
                        aux_string = ""
                        for pos in pos_list:
                            info_concept = self.w.pos[ doc ][ pos ]
                            documento = info_concept[0]
                            concepto = info_concept[1]

                            aux_string += concepto+" "

                            if self.frequent_concepts.has_key(concepto) and documento in self.frequent_concepts[concepto]:
                                #print "Replace:",concept, document
                                # Remove element
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
                # k: concept
                # self.frequent_concepts[k] : set of document numbers to which the concept belongs
                # 
                documentos = list(set(self.frequent_concepts[concepto]))#, list(set(self.frequent_concepts[k][0]))
                strAux = concepto+"  -  "+ str(documentos)+"  -  "+str(len(documentos))
                f.write(strAux+u'\n')
        f.close()

                


    #Itera, go through all the words.
    def text_to_NN_VB_SW(self):
        countDoc = 0
        self.w.initDocument(countDoc)
        word = self.w.getWord() # numParagraph, word, index doc, index word.
        wordSinLemmatize = word
        doc_id = 0
        paragraph_id = 0
        word_id = 0
        #NN_ngrama =  [] #Deactivate search for N-Grams
        while(True):
            try:
                paragraph_id = word[0]
                doc_id = word[2]
                word_id = word[3]
                tag = word[4] 
                word = self.w.remove_punc_upper(word[1])#
                wordSinLemmatize = word
                if not word in stopwords:# No lemma stopwordVB
                    word = lmtzr.lemmatize(word, 'n')#Eliminate uppercase
                    word = lmtzr.lemmatize(word, 'n')#Eliminate plural
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
                #NN_ngrama = [] #Deactivate search for N-Grams
                continue                
            #--
            if not word in stopwords:
                if 'NN' in tag:
                    self.save_concept(word, doc_id, paragraph_id, word_id)
                
                if 'VB' in tag:# possible elimination, give the NN's priority.
                    self.save_verb(wordSinLemmatize, doc_id, paragraph_id, word_id)
                """#Deactivate search for N-Grams
                if 'NN' in tag:
                    self.save_concept(word, doc_id, paragraph_id, word_id)
                    NN_ngrama.append(word)
                else:
                    if len(NN_ngrama)> 1:
                        c_ngrama = ' '.join(NN_ngrama)
                        self.save_concept(c_ngrama, doc_id, paragraph_id, word_id-1) #word_id-1: previous word
                    NN_ngrama = []
                if 'VB' in tag:# possible elimination, give the NN's priority.
                    NN_ngrama = []
                    self.save_verb(wordSinLemmatize, doc_id, paragraph_id, word_id)
                """
            else:#Borrar
                self.save_stopwordVerb(wordSinLemmatize, doc_id, paragraph_id, word_id)
            #--
            word = self.w.getWord()

    # self.frequent_concepts: the most frequent 1-grams, without any other information.
    # self.conceptsInforApriori: the most frequent 1-grams, with information for Apriori.
    # Save all the most frequent concepts above the given threshold.
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
                    #Incoming concept ordered by "c -> doc"
                    self.frequent_concepts[c] = self.frequent_concepts.get(c,[])
                    self.frequent_concepts[c].append(t[0])

                    #c: concept
                    #t[0]: document number
                    #t[1]: paragraph
                    #t[2]: word position
                    # Occupied to store all the information of the concepts (NN)<
                    
                    self.conceptsList.append((c, t))#[0], t[1], t[2]))

                    #print "FC:",c,t
                    self.conceptsInforApriori[c] = self.conceptsInforApriori.get(c,[])
                    self.conceptsInforApriori[c].append( (t[0],t[2]) )
                    #dataSet_T[t[0]] = dataSet_T.get(t[0], {} )
                    #dataSet_T[t[0]][c] = dataSet_T[t[0]].get(c, [] )
                    #dataSet_T[t[0]][c].append( (t[1],t[2]) )

                    #Store frequent concepts in dicc as a set (avoiding repetitions)
                    dataSet_T[t[0]] = dataSet_T.get(t[0], set() )
                    dataSet_T[t[0]].add( c )
                    #dataSet_T.append(
        
        
        # Once obtained the most frequent concepts (1-gram), use them in the Apriori algorithm
        dataSet_aux = []
        ## -- APRIORI --##
        #Transform to a list of lists
        for k in dataSet_T:
            #print k,":", dataSet_T[k]
            dataSet_aux.append( list(dataSet_T[k]) )

        self.dataSet_T = dataSet_aux
        #print dataSet_aux
        for e in dataSet_aux:
            if printData: print e
            
                    
        self.conceptsList = sorted(self.conceptsList, key=lambda x: x[1]) #Consecutive concepts.

        
        
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
        for i in range(i1+1, i2):#Extract all the candidates between 2 concepts.
            if self.w.pos[doc_id1][i][1] not in stopwords: 
                if 'VB' in self.w.pos[doc_id1][i][2]:
                    aux = lmtzr.lemmatize(self.w.pos[doc_id1][i][1], 'v')
                    candidates.append( aux.lower() )# Agressive form.
            else:
                if self.w.pos[doc_id1][i][1] in stopwordsVerbs:
                    candidatesSW.append(self.w.pos[doc_id1][i][1])
        # Case 1 and 2: there are candidates between concepts 1 and 2
        if len(candidates) != 0:
            # Case 1: one candidate
            if len(candidates) == 1:
                self.verbBetweenC[candidates[0]] = self.verbBetweenC.get(candidates[0],[])
                self.verbBetweenC[candidates[0]].append((doc_id1))
                return candidates[0]
            # Case 2: more than one candidate
            if len(candidates) > 1: 
                candidate_freq ={} #In the whole doc
                candidate_freq2 ={}#In a specific doc
                count=0
                for candidate in candidates:#For each candidate (verb) between concepts c1 and c2.
                    try:
                        # Times that the candidate is repeated
                        candidate_freq[candidate] = len(self.verbs[candidate])
                        for e in self.verbs[candidate]: # self.verbs[verbo] === (docId, paragraphId, wordId)
                            if e[0]==doc_id1:
                                count+=1 #Count the frequency of the verb in the specified document
                        candidate_freq2[candidate]=count 
                        count = 0 #Reinitialize count
                    except:#If no candidates are found, then search for candidates of type stopwordVerb.
                        try:
                            candidate_freq[candidate] = len(self.stopwords[candidate])
                            for e in self.stopwords[candidate]:
                                if e[0]==doc_id1:
                                    count+=1
                            candidate_freq2[candidate]=count
                            count = 0
                        except:#If cannot find verb in los stopwordVerb -> Verb is not a candidate verb. See text_to_NN_VB_ST
                            pass#The verb between concepts is not taken as a verb, according to the structure of the oration.
                        

                #CASE 1: frequency of the verb for the whole document.
                #returns the most frequent in the complete text.
                seleccionado = sorted(candidate_freq.items(), reverse= True, key=lambda x: x[1])[0]#[0] #(verb, contador)
                self.verbBetweenC[seleccionado[0]] = self.verbBetweenC.get(seleccionado[0],[])
                self.verbBetweenC[seleccionado[0]].append((doc_id1))
                return seleccionado[0]
        #Case 3: search for verb to the left, 5 words, omit stopwords
        else:
            limite = 5 # limit, number of words going backwards (omit stopwords)
            count = 1 # retrocede, decrement initial concept index i1.
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

    # Finally it will not be found in Wordnet, given that it works with 1-grams.
    # SOl: Only count the frequency of these, eliminating occurrencies in the output file
    def agregar_n_gramas(self, diccGramas):

        #diccGramas: dictionary of dictionary
        #           [doc][n-gram] (positions)
        
        # [(u'state', (0, 0, 14)), -> concept, (doc, paragraph, positionWord)
        # self.conceptsList#[0][1][0]: doc
        # self.conceptsList#[0][1][1]: paragraph
        # self.conceptsList#[0][1][2]: pos
        #print self.conceptsList
        if printData: print "asd",self.conceptsList#[0][1][2]
        if printData: print diccGramas
        for doc in diccGramas: # for each document
            for n_grama in diccGramas[doc]: # for each n-gram in document x
                if printData: print "----- Document22:", doc, "\t",str(n_grama)+"_gram------"
                for pos_list in diccGramas[doc][n_grama]: # For each list which stores positions of n-gram
                    aux_list_string_n_grama = []
                    for pos in pos_list: # For each position of the current n-gram
                        #[0]: Document number
                        #[1]: Concept
                        #[2]: Type (NN)
                        #print self.pos[ doc ][ pos ]#[1]
                        aux_list_string_n_grama.append(self.w.pos[ doc ][ pos ][1]) #aggregate concept
                    aux_string_n_grama = "_".join(aux_list_string_n_grama)
                    # If the position of the first concept (pos) is in self.conceptsList, 
                    # If the same doc, 
                    #if self.conceptsList[0][1][0] == doc and

        # Iterate self.conceptsList
        for tupla in self.conceptsList:
            lista_n_grama = self.busca_n_grama_en(diccGramas, tupla[1][0]) #doc: tupla[1][0]
            for t in lista_n_grama:
                #t[0]: position 1 of the n-gram
                if t[0] == tupla[1][2]: # position 1 of the n-gram is the same as the position of the concept in the list of concepts
                    # Eliminate the follow from the list of concepts
                    pass
                    # Modify the concept to n-gram
        # REDO VARIABLES
        
    def busca_n_grama_en(self, diccGramas, doc):
        list_aux = []
        for n_grama in diccGramas[doc].values():
            list_aux.append(n_grama)
        return list_aux # list of tuples which have positions of the n-grams
        
        

    def add_to_M_S(self):
        tupla = self.seleccionConcepts()
        while tupla!=None:
            tupla = self.seleccionConcepts()
        
    def red_semantica(self):
        #Preparing variables - concepts and verbs
        #self.frecuentConcetps() #concepts to list

        ## HERE
        # Modify  self.conceptsList
        #self.agregar_n_gramas()
        
        #self.verbsToList()#Order the verbs
        #-- Iterate aggregating concepts of a context to a M_S
        #print self.conceptsList
        """
        tupla = self.seleccionConcepts()
        while tupla!=None:
            tupla = self.seleccionConcepts()
        """
        ## HERE
        start = None
        if self.printTime:
            start = time.time()

        # self.M_S: store consecutive concepts as pairs, to later search for verbs in their vecinity.
        for c1, doc_id1, par_id1, i1, c2, doc_di2, par_id2, i2, rel_type in self.M_S:
            # Search for verbs which are close to the stored concept pairs in M_S
            verbo = self.find_verb(c1, doc_id1, par_id1, i1, c2, doc_di2, par_id2, i2)
            # redSemantica: semantic network, dictionary stores graph objects
            self.redSemantica[doc_id1] = self.redSemantica.get(doc_id1, nx.DiGraph()) # par_id1
            if not self.redSemantica[doc_id1].has_edge(c1,c2):# doc_id, change to doc_id1
                if c1==c2 and verbo == None:
                    continue
                self.redSemantica[doc_id1].add_edge(c1,c2)#Create it
                self.redSemantica[doc_id1][c1][c2]['label'] = verbo

        if self.printTime: print "Tiempo:", time.time() - start
        
    # Iterate to the end.
    # self.M_S: store consecutive concepts as pairs, to later search for verbs in their vecinities.
    def seleccionConcepts(self):
        try:
            t1 = self.conceptsList[self.actualIndex]#[1]#[self.actualParagraph]
            t2 = self.conceptsList[self.actualIndex+1]            
        except Exception as inst:
            return None
        
        if t1[1][0] == t2[1][0] and t1[1][1] == t2[1][1]: #Same doc and same context.
            self.actualIndex+=1
            rel_type = 'Normal'
            if self.is_superset(list(set(self.conceptsDoc[t1[0]])), list(set(self.conceptsDoc[t2[0]])) ): # Error. // Changed
                rel_type = 'Super'
            self.M_S.append((t1[0], t1[1][0], t1[1][1], t1[1][2],t2[0], t2[1][0], t2[1][1], t2[1][2],rel_type))
            return (t1, t2)
        else:#augment index for next context
            self.actualIndex+=1
            return (None,None)

    def is_superset(self, l1,l2):
        if len(set(l2) - set(l1)) == 0: #Eliminate elements of l2.
            return True
        return False 
    def save_concept(self, word, doc_id, paragraph_id, word_id):#Dividethem in contexts.

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
 
    def save_stopwordVerb(self, word, doc_id, paragraph_id, word_id): #Not used
        if word in stopwordsVerbs:
            self.stopwords[word] = self.stopwords.get(word,[])
            self.stopwords[word].append((doc_id, paragraph_id, word_id))

    def write_to_word(self):
        if self.write:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            try:
                folder_name = self.folder+"2.- RS_by_doc umbral_"+self.nameExample+" "+str(self.umbralOriginal)+"% _Frec_"+str(self.umbral/self.w.numDocs)+".txt"
            except:
                "There is only one document, the initial one 0 (Divide by zero error)."
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
        #Delete concepts which are equal to 1 in a lengthwise manner
        self.delConceptEqual1 = delConceptEqual1
        #Input files txt utf8
        self.folderInput = folderInput
        #TM LIST - equal similar ...
        self.tm_list = tm_list
        #Create folder - contains all the created files
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

        # Calculate IC for the most frequent concepts.
        
        self.frec = {}        
        self.calc_frec()# Calculate the frequencies of all the concepts
        
        self.N = 0
        self.cal_N() # calculate the N. Summation of the frequencies
        
        self.IC = {}
        self.calc_IC() # Calculate the IC of all concepts
        
        
        
        #FINAL STEP.
        self.memesEscogidos = {} # Dictionary of results of memes which are the same or similar.
        start = None
        if self.printTime:
            print "Choose memes according to tm (main algorithm)"
            start = time.time()
        self.largoMasFrecuente = self.escogerMemes() #Returns the length of the most frequenct meme.
        if self.printTime: print "Time:", time.time() - start

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
            li.append(m1)# stores indices/numbers of the memes.
            
        memeSimilar = {}
        masLargo = 0 #The longest meme.
        for i in range(0,len(li)):
            count = 0
            for i2 in range(0,len(li)):
                if li[i] != li[i2]:
                    tm = self.matching(self.memes[li[i]], self.memes[li[i2]])
                    #if tm==1 or tm==2: #If they are the same or similar
                    if tm in self.tm_list:
                        count += 1 
                        memeSimilar[li[i]] = memeSimilar.get(li[i], [])
                        memeSimilar[li[i]].append((self.memes[li[i]][0][3], self.memes[li[i2]][0][3], tm, li[i],li[i2]))
            if count > masLargo:
                masLargo = count

        self.memesEscogidos =  memeSimilar
        return masLargo

    def matching(self, m1, m2):
        if len(m1)==len(m2):#Same
            dist = self.distmeme(m1, m2, flag=False)#flag: prints dists False True
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

    def distmeme(self, m1, m2, flag=False):#DELETE ME
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
            
    #De Digraph to list, then order lexicographically.
    def separarGrafos(self):
        #Separate Digraph
        #ud=d.to_undirected()
        #hl=nx.connected_component_subgraphs(ud)
        #for l in hl: for e in l.edges(): print e
        #CASE1: don't move c1 and c2.
        #Separate connected graphs.
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
        #c1 does not exist in the corpus. E.g., n-grams.
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
        #c1 or c2, not found in the corpus.
        except:
            return 1.0
    
    def dist_rel(self, r1, r2):#DOUBT
        if (r1 is None) and (r2 is not None):
            return min([self.dist_rel('be',r2), self.dist_rel('have',r2)])

        elif (r1 is not None) and (r2 is None):
            return min([self.dist_rel(r1,'be'), self.dist_rel(r1,'have')])


        #distance between r1 and r2 of the tree / length of branch
        if r1==r2:
            return 0.0
        flag1 = False#Except parches
        flag2 = False#Except parches
        s = wn.synsets(r1, wn.VERB)
        
        try:#Except patches
            #r2 = lmtzr.lemmatize(r2, 'v')+'.v.01'  # None.v.01  does not exist.
            r2 = lmtzr.lemmatize(r2, 'v')  # None.v.01  does not exist.
            #s2 = wn.synset(r2)
        except:#Except patches
            flag2 = True
            self.wordExcept.append(r2+' - v')
            
        if flag2 or len(s)==0:
            return 0.0#Except patches
        
        #Reemplazar ' ' por '_'
        if ' ' in r1 or ' ' in r2:
            print "WARNING space",r1, r2 ,s #, s2
        l = []
        
        for e in s:#For each definition of r1
            dist = e.hypernym_distances()
            for arbol in e.hypernym_paths():#Tree of def in downward direction
                for syns in arbol:#each def has a set of synset (for each level of the tree)
                    if r2 in syns.lemma_names():#each set of synset has lemas, if r2 is among the lemas
                        for i in dist:#Find its distance
                            if i[0] == syns:
                                l.append( (i[1] , len(dist)-1) )
        
        l = sorted( l, key=lambda x: x[0]) #Order by 1st element of the tuple, not the second
        if len(l)==0:
            return 1.0 # No match exists
        seleccion = l[0]
        if seleccion[0] > seleccion[1]:
            print "Error 726", l[0],l[1],r1,r2
        #Sin saltos, solo posee una hoja. ej expect , look
        if seleccion[1]==0:
            return 0.0
        return (float(seleccion[0]) /seleccion[1])  #self.lengh(r1,r2)/self.lenght2(r1,r2)

    #Calculate the IC and store them in a dictionary. N: #number of files in the corpus.
    def calc_IC(self):
        for k in self.s.concepts:
            #If exists in the corpus
            try:
                self.IC[k] = -math.log(self.frec[k]/float(self.N) , 2)
            except:
                pass
    def calc_frec(self):
        for k in self.s.concepts:
            #If exists in the corpus
            try:
                self.frec[k] = corpus[k]
            #If does not exist in the corpus. For example, the n-grams.
            except:
                #REVISE
                #sol: average of the frequency of the n-grams.
                n_grama = k.split(" ")
                num_gramas = len(n_grama)
                suma = 0
                for i in n_grama:
                    #i = lmtzr.lemmatize(i, 'n')#.lower()
                    try:
                        suma += corpus[i]
                    #Bug 482: Some nouns not being lemmatised by WordNetLemmatizer().lemmatize
                    except:#Solution: remove the 's' at the end of the word.
                        try:
                            suma += corpus[i[:-1]]
                        #The word does not exist in the corpus. E.g. "obamacare"
                        except:
                            pass
                #If the n-gram is not found
                promedio = suma / num_gramas
                if promedio != 0:
                    self.frec[k] = promedio#corpus[k]
                    
    def cal_N(self):
        self.N = 0
        for k in self.frec:
            self.N += self.frec[k]
            
    #Calculate the IC of a superior concept. As abstraction, object, ...
    def IC_sup(self, c):
        #If c==None, its because an LSup could not be found for c1 or c2 in Wordnet.
        if c==None:
            return 0.0 
        try:
            return -math.log(corpus[c]/ float(self.N), 2) 
        #Word sup is not in the corpus. For example, "definite_quantity"
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
            s2 = wn.synset(lmtzr.lemmatize(c2)+'.n.01') # only the first of the definitions
        except:
            flag2=True
            self.wordExcept.append(c2+' - c')
        # Returns None, when c1 or c2 are not found in Wordnet
        if flag1 or flag2:
            return None
        
        seleccion = s1.lowest_common_hypernyms(s2)
        return seleccion[0].name().split('.')[0]#s1.lowest_common_hypernyms(s2)

    
    def excepts_to_txt(self):
        doc_name = self.folder+"3.1.- EXCEPT.umbral_"+str(self.s.umbral/self.s.w.numDocs)+"_Frec_"+str(self.s.umbralOriginal)+"_Concepts__"+self.s.nameExample+".txt"
        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'WORD - c:concept, v:verb \nNumber of word in except:'+str(len(self.wordExcept))+'\n\n')
            for e in list(set(self.wordExcept)):#conceptsList concepts
                f.write(e+u'\n')
        f.close()
    def memes_tm_1_2_to_txt(self):
        try:
            doc_name = self.folder+"3.- Meme.umbral_"+self.s.nameExample+" "+str(self.s.umbralOriginal)+"% _Frec_"+str(self.s.umbral/self.s.w.numDocs)+".txt"
        except:
            doc_name = self.folder+"3.- Meme.umbral_"+self.s.nameExample+" "+str(self.s.umbralOriginal)+"% _Frec_"+str(self.s.umbral)+".txt"
        #Ordener memes
        guardar_memes = []
        for e in self.memesEscogidos: #For each ID of self.meme
            memeID2 = []
            docID2 = []
            for i in self.memesEscogidos[e]:#DocIdMeme1, DocIdMeme2, tm, memeId1, memeId2
                memeID2.append( i[4] )
                docID2.append( i[1] ) #the doc of memes which are similar|the same
            docID2 = list(set(docID2))
            
            #Count the different "c", "r":count non empty "rel".
            conceptos = []
            relaciones = []
            for m1 in self.memes[e]:
                if not m1[0] in conceptos:
                    conceptos.append(m1[0])
                if not m1[1] in conceptos:
                    conceptos.append(m1[1])
                if (not m1[2] in relaciones) and m1[2]!=None :
                    relaciones.append(m1[2])
            # append - number meme1, meme1, IDmeme2, , number of references, number of distinct concepts, number of distinct relations.
            guardar_memes.append( (e, self.memes[e] , memeID2 , ( len(memeID2) , len(docID2) ,len(conceptos) ,  len(relaciones)) ))
            # Order with more than 1 element? D:
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
            f.write(u" All the memes \n") 
            for m1 in self.memes:
                f.write(u" #-"+str(m1)+": "+str(self.memes[m1])+"\n\n")
        f.close()

    def resultados(self):
        # Variable to store the relations
        relaciones = []
        relacion_frec = []
        
        # Extract the elements, tranform them to ordered lists of lists.
        lista = []
        lista2 = []
        lista2Sorted = []
        relaciones_doc = {}

        doc_name = self.folder+"4.- Resultado_final_RS_"+self.s.nameExample+" "+str(self.s.umbralOriginal)+"%.dot"
        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'Semantic networks \n\n')
            for doc in self.s.redSemantica:                
                for l1 in self.s.redSemantica[doc].edges(data=True):
                    #Store in variables
                    lista2.append( [ l1[0], l1[1]] ) #, l1[2]['label']) )# sorted([ l1[0], l1[1]])
                    #Store in document. beneficiary -> room	 [label=increase];
                    f.write(u" "+l1[0]+ " -> " + l1[1] + "\t[label="+ str(l1[2]['label']) +'];\n') 
                        
                    if l1[2]['label'] is None:
                        continue
                    relaciones.append( l1[2]['label'] )
                    relaciones_doc[ l1[2]['label'] ] = relaciones_doc.get( l1[2]['label'] ,[])
                    relaciones_doc[ l1[2]['label'] ].append( doc ) #Doc
        
        
        f.close()
        # Store the frequencies of concept pairs
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
        #Store the frequencies of each relation
        for r in set(relaciones):
            relacion_frec.append( (r, relaciones.count( r ), set(relaciones_doc[r]) ) )


        # Order by frequency
        relacion_frec = sorted(relacion_frec, reverse= True, key=lambda x: x[1])
        list_pares_con_frec = sorted(list_pares_con_frec, reverse= True, key=lambda x: x[1])

        doc_name = self.folder+"5.- Resultado_Final_"+self.s.nameExample+" "+str(self.s.umbralOriginal)+"%.dot"
        with io.open(doc_name, 'w', encoding='utf-8') as f:
            f.write(u'((concepto1, concepto2), frecuencia) \n\n')  
            # Write out the frequencies of the concept pairs
            for e in list_pares_con_frec:
                f.write( u'('+str(e[0][0])+','+str(e[0][1])+') '+str(e[1])+'\n')
            # Write the frequent relations
            f.write(u'\n\n(relacion, frecuencia, [docs]) \n\n') 
            for e in relacion_frec:
                f.write( u''+str(e)+'\n')
             
        f.close()

        

        
        

    
    
"""
RS_to_words = True # False True #write the semantic networks to .dot documents
print_concepts = True # False True
print_excepts_in_meme = False # False True
print_meme_tm_1_2 = True #Write the memes which are the same or
print_prob_con_dist_meme = False #Deprecated, write the concepts which were not found in the text (meme)
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
                #print "Error in "+e+", with threshold ",umbral

"""
        
