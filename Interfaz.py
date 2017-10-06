# -*- coding: utf-8 -*-

import wx
import wx.lib.buttons as buttons
import wx.animate
import threading
import os, time

import codecs
def replace_space_error(error):
    return (u' ' * (error.end-error.start), error.end)
codecs.register_error("replace_space", replace_space_error)

from Meme000 import Meme
from Extract import HtmlExtract
folder_image = "Img/"
#from contrasenhas.vista import VistaContrasenha
    
class Main(wx.App):
    """Clase que inicia La ventana pricnipal de la aplicación"""
    
    def OnInit(self):
        """
        Método que instancia la clase que incia la ventan principal
        """
        self.ventana = VentanaPrincipal(None)
        """Propiedad que almacena el objeto de la ventana principal """
        
        self.SetTopWindow(self.ventana)
        
        return True


class TestNB(wx.Notebook):
    """
    Clase que crea las pestañas de la aplicación
    """
    def __init__(self, parent, id, names = ["Pestana_1"]):
        
        """
        Constructor de las pestañas de la aplicación.
        
        :param parent: El objeto de la ventana principal que contendrá las diferentes pestañas
        :param id: Identificador único de la ventana
        """
        
        wx.Notebook.__init__(self, parent, id, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             # | wx.NB_MULTILINE
                             )
        """Propiedad que almacena la ventana madre donde deben ir las pestañas """
        self.parent = parent

        # Almacenar pestañas - self.pestanas[Nombre_pestana]
        self.pestanas = {}
        for pestana_name in names:
            self.pestanas[pestana_name] = wx.Panel(self)
            self.AddPage(self.pestanas[pestana_name], pestana_name)
        #self.pestana1 = wx.Panel(self)
        #self.AddPage(self.pestana1, "Gestión de Contraseñas")
        

class Gui1:
    def __init__(self, parent, interfaz2):
        
        self.printTime = True

        # TITULO
        text=wx.StaticText(parent, label="Meme",
                           pos=(10, 10) )
        text.SetForegroundColour((114,214,250)) # set text color (0,174,239) 46,145,181
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)        
        
        # Umbral % - LABEL
        text=wx.StaticText(parent, label="Umbral:   %",pos=(10, 50) )
        text.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)
        
        # Umbral % - TEXT INPUT        
        self.i_umbral = wx.TextCtrl( parent, wx.ID_ANY,
                                     u"0.35",
                                     pos=(90, 50), size=(80, 20),
                                     style=wx.TE_RICH )
        self.i_umbral.SetMaxLength( 15 )        
        self.i_umbral.SetHelpText("Capture sensitivity concepts.")

        
        # Umbral RO - LABEL
        text=wx.StaticText(parent, label="RO",pos=(180, 49) )
        text.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)
        # Umbral RO - TEXT INPUT
        self.i_ro = wx.TextCtrl( parent, wx.ID_ANY,
                                     u"0.5",
                                     pos=(205, 50), size=(80, 20),
                                     style=wx.TE_RICH )
        self.i_ro.SetMaxLength( 15 )
        self.i_ro.SetHelpText("Significance level for concepts (Ro+Sigma=1.0).")

        # Umbral SIGMA - LABEL
        text=wx.StaticText(parent, label="SIGMA",pos=(300, 49) )
        text.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)
        # Umbral SIGMA - TEXT INPUT
        self.i_sigma = wx.TextCtrl( parent, wx.ID_ANY,
                                     u"0.5",
                                     pos=(350, 50), size=(80, 20),
                                     style=wx.TE_RICH )
        self.i_sigma.SetMaxLength( 15 )
        self.i_sigma.SetHelpText("Significance level for relations (Ro+Sigma=1.0).")

        # Verificar utf-8 - BUTTON
        self.b_verify = wx.Button( parent, wx.ID_ANY,
                                     u"Verify UTF-8", (610, 15), (90, 25),
                                     0 )
        self.b_verify.Bind(wx.EVT_BUTTON, self.verify)
        self.b_verify.SetHelpText("Check if the file below is valid.")
        """
        # FIX utf-8 - BUTTON
        self.b_fix = wx.Button( parent, wx.ID_ANY,
                                     u"Fix UTF-8", (660, 15), (90, 25),
                                     0 )
        self.b_fix.Bind(wx.EVT_BUTTON, self.fix_txt)
        self.b_fix.SetHelpText("Try to fix all files from '/Files' folder.")
        """
        # Select File - BUTTON
        self.b_selectfile = wx.Button( parent, wx.ID_ANY,
                                     u"Select File", (710, 15), (90, 25),
                                     0 )
        self.b_selectfile.Bind(wx.EVT_BUTTON, self.select_file)
        self.b_selectfile.SetHelpText("Select file.")
        """
        # Update listBox txt - BUTTON
        self.b_updateList = wx.Button( parent, wx.ID_ANY,
                                     u"Update List", (760, 15), (90, 25),
                                     0 )
        self.b_updateList.Bind(wx.EVT_BUTTON, self.updateList)
        self.b_updateList.SetHelpText("Update below box.")"""

        # Archivos txt - LABEL
        text=wx.StaticText( parent, label="Archive selected",pos=(500, 25) )
        text.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)
        
        
        
        
        self.archive_path = ""
        # Archivos txt - ListBox
        self.folder_name_files = "Files"
        self.choicesTxtList = ""#self.findFiles()#["asd","zxc","qwew",]
        self.listBox1 = wx.ListBox( parent, id=-1, pos=(500, 50),
                                   size=(350,100), choices=self.choicesTxtList, style=0,
                                   validator=wx.DefaultValidator, name=wx.ListBoxNameStr)
        #self.listBox1.SetHelpText("All files in the '../File' folder will be processed.")
        self.listBox1.SetHelpText("Archive to extract information.")
        
        
        # output files - LABEL
        text=wx.StaticText( parent, label="Output Files:",pos=(10, 80) )
        text.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)
        #  - Checkboxes
        self.conceptFrecDoc = wx.CheckBox( parent, -1, u"Concept Frecuency by Doc", pos=(10, 100), size=(250,20) )
        self.conceptFrecDoc.SetValue(True)
        self.semanticNetwork = wx.CheckBox( parent, -1, u"Semantic Network", pos=(10, 120), size=(250,20) )
        self.semanticNetwork.SetValue(True)
        self.filteredMeme = wx.CheckBox( parent, -1, u"Filtered Meme", pos=(10, 140), size=(250,20) )
        self.filteredMeme.SetValue(True)
        #self.semanticNetworkOneDoc = wx.CheckBox( parent, -1, u"Semantic Network in one Doc", pos=(10, 160), size=(250,20) )
        #self.semanticNetworkOneDoc.SetValue(True)
        self.ResultsFrecuency = wx.CheckBox( parent, -1, u"Results Concepts and Relations Frecuency", pos=(10, 160), size=(250,20) )
        self.ResultsFrecuency.SetValue(True)
        self.allMemes = wx.CheckBox( parent, -1, u"All memes (whitout filter)", pos=(10, 180), size=(250,20) )

        # output files - LABEL
        text=wx.StaticText( parent, label="Filter:",pos=(270, 80) )
        text.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)
        #  - Checkboxes 2
        self.equal = wx.CheckBox( parent, -1, u"Equal", pos=(270, 100), size=(150,20) )
        self.equal.SetValue(True)
        self.similar = wx.CheckBox( parent, -1, u"Similar", pos=(270, 120), size=(150,20) )
        self.similar.SetValue(True)
        self.subset1 = wx.CheckBox( parent, -1, u"M1 subset M2", pos=(270, 140), size=(150,20) )
        self.subsimilar1 = wx.CheckBox( parent, -1, u"M1 sub-similar M2", pos=(270, 160), size=(150,20) )
        self.subset2 = wx.CheckBox( parent, -1, u"M2 subset M1", pos=(270, 180), size=(150,20) )
        self.subsimilar2 = wx.CheckBox( parent, -1, u"M2 sub-similar M1", pos=(270, 200), size=(150,20) )
        self.different = wx.CheckBox( parent, -1, u"different", pos=(270, 220), size=(150,20) )

        # Folder name for output files - LABEL
        text=wx.StaticText( parent, label="Folder Name for output files:",pos=(10, 220) )
        text.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)
        # Output files folder - TEXT
        self.output_files_folder = wx.TextCtrl( parent, -1, time.strftime("%d.%m.%Y"), pos=(10, 240), size=(200,20))
        self.output_files_folder.SetHelpText("Default folder. It can contain subfolders using /")

        # LOG - LABEL
        text=wx.StaticText( parent, label="LOG:",pos=(500, 180) )
        text.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)
        # LOG - TEXT
        self.log = wx.TextCtrl( parent, -1, "", pos=(500, 200), size=(350,100),
                                style= wx.TE_MULTILINE )
        self.log.SetEditable(False)


        # INICIAR - BUTTON
        self.b_start = wx.Button( parent, wx.ID_ANY,
                                     u"Start", (10, 280), (120, 25),
                                     0 )
        self.b_start.Bind(wx.EVT_BUTTON, self.start)
        self.b_start.SetHelpText("Before start, verify all above parameters.")

        # Help Provider - BUTTON
        self.helpButton = wx.ContextHelpButton(parent, pos=(855,15))

        
        # INTANCEAR EMOTIV
        #self.emotiv = Emo.Emotiv(self, interfaz2)
        #Run emotiv thread loop
        #self.emotiv.start()
    #----------------------------------------------------------------------
    def findFiles(self):
        return os.listdir(self.folder_name_files)
    def select_file(self, event):
        # Select a file - FileDialog
        wildcard = "Text source (*.txt)|*.txt" 
        #"Compiled Python (*.pyc)|*.pyc|" \
        #"All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            print dialog.GetPath()
            self.archive_path = dialog.GetPath()

        self.listBox1.Clear()
        self.choicesTxtList = self.archive_path
        self.listBox1.Insert(self.choicesTxtList,0) #InsertItems
        self.log.AppendText("A file has been entered\n")
    #----------------------------------------------------------------------
    def verify(self, event):
        #for filename in self.choicesTxtList:
        if self.archive_path != '':
            try:
                #f = open(self.folder_name_files+"/"+filename, "r")
                f = open(self.archive_path, "r")
                data = f.read()
                try:
                    #print "Valid utf-8"
                    data.encode("utf-8")
                    self.log.AppendText(self.archive_path+" is valid\n")
                except:
                    #print "invalid utf-8"
                    self.log.AppendText(self.archive_path+" is NOT valid\n")
            except UnicodeDecodeError:
                print "invalid utf-8"
                self.log.AppendText(self.archive_path+" exist?\n")
        else:
            self.log.AppendText("\nYou must select a file\n")

    def fix_txt(self, event):
        for filename in self.choicesTxtList:
            self.log.AppendText("Fixing "+filename+" ... ")
            #Most common problems
            text=""
            with codecs.open(self.folder_name_files+"/"+filename,'r','cp1250', "replace") as f:
                text = f.read()
                
            #Seguir rellenando
            text = text.replace(u'\u2019','\'') #Problema comillas simples.
            text = text.replace(u'\u2018','\'') #Problema comillas simples.
            text = text.replace(u'\u201c','"') #Problema comillas dobles.
            text = text.replace(u'\u201d','"') #Problema comillas dobles.        
            text = text.replace(u'\u2014',' ') #Problema unicode —.
            text = text.replace(u'\ufeff','\ ') #Problema unicode2 ??
            #text = text.replace(u'\xb4','\'') #Problema unicode2
            
            #Guarda las modificaciones - repara coding
            with codecs.open(self.folder_name_files+"/"+filename,'w','cp1250', "replace") as f:
                f.write(text)
            #Abre reemplazando por espacios los caracteres no validos
            with codecs.open(self.folder_name_files+"/"+filename,'r','utf-8', "replace_space") as f:
                text = f.read()
            #Crea un archivo limpio en UTF-8 sin errores
            f = open(self.folder_name_files+"/"+filename, "w")
            f.write(text)
            f.close()
            self.log.AppendText(" FINISH - See 'OutputFile' folder\n")
            
    
    
        
    #----------------------------------------------------------------------
    """def updateList(self, event):
        self.choicesTxtList = self.findFiles()
        self.listBox1.Clear()
        self.choicesTxtList = self.findFiles()
        self.listBox1.InsertItems(self.choicesTxtList,0)
        self.log.AppendText("Folder '/Files' has been updated\n")"""
    #----------------------------------------------------------------------
    def start(self, event):

        #tm filter
        tm_list = []
        if self.equal.GetValue():
            tm_list.append(1)
        if self.similar.GetValue():
            tm_list.append(2)
        if self.subset1.GetValue():
            tm_list.append(3)
        if self.subsimilar1.GetValue():
            tm_list.append(4)
        if self.subset2.GetValue():
            tm_list.append(5)
        if self.subsimilar2.GetValue():
            tm_list.append(6)
        if self.different.GetValue():
            tm_list.append(0)

        #Begin
        self.log.AppendText("Started ...\n")
        print_concepts                      = self.conceptFrecDoc.IsChecked()
        RS_to_words                         = self.semanticNetwork.IsChecked()
        print_meme_tm_1_2                   = self.filteredMeme.IsChecked()
        print_resultados                    = self.ResultsFrecuency.IsChecked()
        print_all_memes                     = self.allMemes.IsChecked()
        print_excepts_in_meme = False
        print_prob_con_dist_meme = False
        umbrales = [float(d) for d in self.i_umbral.GetValue().split(' ')]
        ro       = [float(d) for d in self.i_ro.GetValue().split(' ')]
        sigma    = [float(d) for d in self.i_sigma.GetValue().split(' ')]

        examples = self.archive_path#.split('\\')#[-1]#self.choicesTxtList

        fecha = "OutputFiles/"+self.output_files_folder.GetValue()#"01.Enero/"
        folderInput = "Files"

        delConceptEqual1 = True
        
        #for e in examples:
        self.log.AppendText("\tAnalyzing "+examples+"\n")#e
        for umbral in umbrales:
            self.log.AppendText("\tUmbral to "+str(umbral*100)+" ")
            for i in range(0,len(ro)):
                self.log.AppendText("with Ro: "+str(ro[i]*100)+"% and SIGMA: "+str(sigma[i]*100)+"%\n")
                #try:
                self.log.AppendText("This may take several minutes. Please wait...\n")
                Meme( examples,#e
                      umbral,
                      RS_to_words,
                      print_concepts,
                      print_excepts_in_meme,
                      print_meme_tm_1_2,
                      print_prob_con_dist_meme,
                      ro[i],
                      sigma[i],
                      print_resultados,
                      print_all_memes,
                      fecha,
                      folderInput,
                      tm_list,
                      delConceptEqual1,
                      self.printTime)
                #except:
                    #print "Error en "+e+", con umbral ",umbral
        self.log.AppendText("\tFINISH - See 'OutputFile' folder\n")
        """self.equal.IsChecked()
        self.similar.IsChecked()
        self.subset1.IsChecked()
        self.subsimilar1.IsChecked()
        self.subset2.IsChecked()
        self.subsimilar2.IsChecked()
        self.different.IsChecked()"""
    #----------------------------------------------------------------------


class Gui2:
    def __init__(self, parent):
        # VARIABLES GLOBALES
        
        
        # TITULO
        text=wx.StaticText(parent, label="Web Extractor",
                           pos=(10, 10) )
        text.SetForegroundColour((114,214,250)) # set text color (0,174,239) 46,145,181
        text.SetBackgroundColour("white") # set text color
        font = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text.SetFont(font)

        # LIST URL ALLOWED
        self.url_allowed = ['www.reuters.com',]

        # URL - LABEL
        text_url=wx.StaticText(parent, label="URL: ",pos=(30, 50) )
        text_url.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text_url.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text_url.SetFont(font)
        
        # URL - TEXT INPUT
        self.i_url = wx.TextCtrl( parent, wx.ID_ANY,
                                     u"http://www.reuters.com/article/2013/06/03/us-usa-healthcare-medicaid-idUSBRE95213A20130603",
                                     pos=(70, 50), size=(700, 20),
                                     style=wx.TE_RICH )
        self.i_url.SetMaxLength( 15 )
        self.i_url.SetHelpText("URL of publications, example: http://www.web.com/.../publication")

        # Valid url - BUTTON
        self.b_valid = wx.Button( parent, wx.ID_ANY,
                                     u"Valid URL", (680, 80), (90, 25),
                                     0 )
        self.b_valid.Bind(wx.EVT_BUTTON, self.valid)
        self.b_valid.SetHelpText("Only valid URL can be processed")

        # Archive Name - LABEL
        text_archive=wx.StaticText(parent, label="Archive Name: ",pos=(30, 120) )
        text_archive.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text_archive.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text_archive.SetFont(font)
        
        # Archive Name - TEXT INPUT
        self.i_archiveName = wx.TextCtrl( parent, wx.ID_ANY,
                                     u"Example",
                                     pos=(130, 120), size=(200, 20),
                                     style=wx.TE_RICH )
        self.i_archiveName.SetMaxLength( 15 )
        self.i_archiveName.SetHelpText("Name of the file containing the extracted information.")

        # Archive Name .txt - LABEL
        text_archive=wx.StaticText(parent, label="(.txt)",pos=(335, 120) )
        text_archive.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        text_archive.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        text_archive.SetFont(font)

        # LIST VALID URL - LABEL
        l_valid=wx.StaticText(parent, label="List of valid url: ",pos=(550, 180) )
        l_valid.SetForegroundColour((180,180,180)) # set text color (0,174,239) (23,194,255)
        l_valid.SetBackgroundColour("white") # set text color
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)        
        l_valid.SetFont(font)
        
        
        # LIST VALID URL - TEXT
        self.valid_url_list = wx.TextCtrl( parent, -1, "", pos=(550, 200), size=(200,90),
                                style= wx.TE_MULTILINE )
        self.valid_url_list.SetEditable(False)
        self.valid_url_list.SetHelpText("List of valid URL that could be processed.")
        
        for e in self.url_allowed:
            self.valid_url_list.AppendText(e+"\n")


        # LOG - TEXT
        self.log = wx.TextCtrl( parent, -1, "", pos=(30, 200), size=(500,90),
                                style= wx.TE_MULTILINE )
        self.log.SetEditable(False)

        # Extract - BUTTON
        self.b_extract = wx.Button( parent, wx.ID_ANY,
                                     u"Get", (30, 170), (90, 25),
                                     0 )
        self.b_extract.Bind(wx.EVT_BUTTON, self.extract)
        self.b_extract.SetHelpText("Begin the extraction.")
        
        # Help Provider - BUTTON
        self.helpButton = wx.ContextHelpButton(parent, pos=(855,15))
        #----------------------------------------------------------------------
    def extract(self, event):
        url = self.i_url.GetValue()
        url_list = url.split("/")
        self.log.AppendText("Extracting text from "+url_list[2]+"\n")

        # EXTRACTOR
        lista = [
            self.i_url.GetValue(), 
            ]
        HtmlExtract( self.i_archiveName.GetValue(), lista, "articleText")
        

        self.log.AppendText("FINISH\n")

    def valid(self, event):
        url = self.i_url.GetValue()
        #print url
        url_list = url.split("/")
        #print url_list
        if url_list[2] in self.url_allowed:
            self.log.AppendText(url_list[2]+" in 'valid list' for extraction\n")
        else:
            self.log.AppendText(url_list[2]+" is NOT in 'valid list' for extraction\n")


class VentanaPrincipal(wx.Frame): #wx.Notebook
    """
    Clase que crear la ventana principal de la aplicación
    """
    def __init__(self, parent):
        # VARIABLES GLOBALES
        folder_image = "Img/"

        # Help provider
        provider = wx.SimpleHelpProvider()
        wx.HelpProvider_Set(provider)
        
        # -cargar imagen background pestana 2
        #imagen_background = wx.Bitmap(folder_image+"emotiv.bmp", wx.BITMAP_TYPE_ANY)
        imagen_background = None
        width, heigh = 900, 400#imagen_background.GetSize()+(50,50)
        
        # FRAME
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,
                            title = "Meme & Extractor",
                            pos = wx.Point( -1,-1 ),
                            size=(width, heigh),
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
                            #,style= wx.CAPTION
                            # |wx.MINIMIZE_BOX
                            # |wx.CLOSE_BOX)
        # -bind - when closed
        #self.Bind(wx.EVT_CLOSE, self._when_closed)
        
        # CREAR EL MENU
        self.menu()
        
        
        # CREAR NOTEBOOKS (pestañas)
        n_pestana1 = "Main"
        n_pestana2 = "WebExtractor"
        notebook = TestNB(self, -1, names = [n_pestana1,n_pestana2])

        # CONTENIDO PESTAÑAS - notebook.pestanas[n_pestana1]

        # -background pestaña 2
        #background_p2 = wx.StaticBitmap(notebook.pestanas[n_pestana2], -1, imagen_background, (0, 0))
        # -cargar contenido pestaña 2
        #self.contenido_ventana_2(background_p2)
        #self.interfaz2 = Gui2(background_p2)
        self.interfaz2 = Gui2(notebook.pestanas[n_pestana2])
        
        # -cargar contenido pestaña 1
        #self.contenido_ventana_1(notebook.pestanas[n_pestana1])
        self.interfaz1 = Gui1(notebook.pestanas[n_pestana1], self.interfaz2)
        
        self.Show(True)
        # Le damos tamaño a la ventana
        self.Size = width, heigh

    
    def menu(self):
        
        """
        Método que crea el menú de la ventana principal. Este menú es utilizado en todas las pestañas, no cambia
        """
        self.MiMenuBar = wx.MenuBar()
        self.itemsMenu = wx.Menu()
        # CREAMOS PRIMERO LOS ITEMS
        #subItem
        self.itemsMenu.Append(100, "Example 1", "", wx.ITEM_NORMAL)
        # subItem
        item = wx.MenuItem(self.itemsMenu,110, "Example 2", "")
        ###item.SetBitmap(images.getManualBitmap())
        self.itemsMenu.AppendItem(item)
        self.itemsMenu.AppendSeparator()
        # subItem
        item = wx.MenuItem(self.itemsMenu,120, "Example 3", "")
        ###item.SetBitmap(images.getManualBitmap())
        self.itemsMenu.AppendItem(item)
        self.itemsMenu.AppendSeparator()
        # subItem
        item = wx.MenuItem(self.itemsMenu,130, "Salir", "")
        ###item.SetBitmap(images.getExitBitmap())
        self.itemsMenu.AppendItem(item)
        
        # Añadir subItems a menu
        self.MiMenuBar.Append(self.itemsMenu,"File")
        self.SetMenuBar(self.MiMenuBar)

    #----------------------------------------------------------------------

    

if __name__ == '__main__':
    
    app = Main()
    app.MainLoop()
