# -*- coding: utf8 -*-
import io


#---- Information corpus -----
nombreArchivo = "en.log"

with io.open(nombreArchivo,'r') as f:#,'utf-8'
    text = f.read()
f.close()
text = text.replace(' ','')
text = text.split("\n")


nombreArchivo = nombreArchivo.split(".")[0]
doc_name = "Corpus_"+nombreArchivo+".py"


#---- Corpus ----
nombreArchivo = "en.txt"
f=file(nombreArchivo, "r")
lines=f.read().split("\n")
f.close()


nombreCorpusDicc = "corpus_"+nombreArchivo.split(".")[0] #antes del punto.
palabras={}

#c = 0

with io.open(doc_name, 'w', encoding='utf-8') as f: #
#f=file(doc_name, "w")
    #---- Information corpus -----
    f.write(u"# -*- coding: utf8 -*-\n")
    for line in text:
        if line == '':
            continue
        t = line.split(":")
        f.write(t[0]+" = "+str(t[1])+"\n")

    f.write(u"\n")

    #---- Corpus Diccionary ----
    f.write(nombreCorpusDicc+u"= {} \n")
    for line in lines:
        if line == '':
            continue
        ls = line.split(" ")
        #print ls
        #palabras[ls[0]] = ls[1]
        #key = palabra, value = frecuencia
        #try:
        ls[0] = ls[0].decode('utf-8')
        #if c == 0:
            #print ls[0]
        f.write(nombreCorpusDicc+"[u'"+ls[0]+"']="+str(ls[1])+"\n")
        #except:
            #print c, ls
            #print str(ls[0]),ls[0]
            #print str(ls[1]),ls[1],"\n"
        #c+=1

f.close()
#for k in palabras:
    #print k, palabras[k]
