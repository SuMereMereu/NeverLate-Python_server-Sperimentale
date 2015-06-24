'''
Created on 23/giu/2015

@author: nicola, Riccardo
'''



#CLASSES

class Settings:
    def __init__(self):
        self.vibration_status = "on"
        self.sound_status = "on"
        self.delay = -5
        self.default_settings = "t"
    
    def settings_dict(self):
        dict={}
        dict['vib'] = self.vibration_status
        dict['snd'] = self.sound_status
        dict['delay'] = self.delay
        return dict
        
class User:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.email = ""
        self.G_key = ""
        self.settings = Settings()
        self.subjects = []
            
    def User_Output_List(self):
        lista = []
        lista.append(self.username)
        lista.append(self.password)
        lista.append(self.email)
        lista.append(self.G_key)
        lista.append(self.settings.vibration_status)
        lista.append(self.settings.sound_status)
        lista.append(self.settings.default_settings)
        lista.append(self.settings.delay)
        return lista
        
class PolitoRequest:
    def __init__(self, materia, alfabetica, docente, codice):
        self.subject = materia
        self.alphabetic = alfabetica
        self.prof = docente
        self.code = codice
        self.uploaded = False
        
    def Subj_Output_List(self):                #@FEDERICO, MULTIPLE RETURN
        list = []
        list.append(self.code, self.subject, self.alphabetic, self.prof)
        return list
    
    def Subj_Output_Uploaded(self):#FOR ATTENDANCE TEABLE
        return self.uploaded
    
    
    def dict_for_session(self):
        dict={}
        dict['subj']= self.subject
        dict['alpha']= self.alphabetic
        dict['prof']= self.prof
        dict['code']= self.code
        dict['upl']= self.uploaded
        return dict
    
    def page_string(self):
        return self.subject+", "+self.alphabetic+", "+self.prof+", quadrimestre # "+self.code[9]
        
class PolitoCalendar:
    def __init__(self, subject="", comment="", professor="", classroom=""):
        self.start = ""
        self.end = ""
        self.subject = subject
        self.comment = comment
        self.professor = professor
        self.classroom = classroom