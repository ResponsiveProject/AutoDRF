
import sys, os, io, pathlib, pyclbr 

class AutoDRF(object):
    def __init__(self,ProjectPath, config={}, spacing=4):
        self.path= ProjectPath
        self.Path = Path(ProjectPath)
        self.folders = self.GetSubFolders()
        self.config = config
        self.apps = self.GetApps()
        self.appsPath = self.GetApps(ReturnPath=True)
        self.spacing= 4
        
    def GetModelsOfApp(self, AppDir):
        modelsPath = Path(AppDir).name
        #print ("modelsPath    " +modelsPath )
        modelsApp = modelsPath+".models"
        Classes = pyclbr.readmodule(modelsApp ).keys()
        #Classes = pyclbr.readmodule(str(modelsPath.absolute())).keys()
        return Classes
            
    def ProcessClassSingleScript(self, appPath, ClassName, ScriptFile, indenting=4):
        appfile = Path(appPath)
        if indenting==4:
            spacing = "    "
        else: #TODO adding dynamic identation
            spacing = "  "
        found = False
        if ScriptFile=="serializers.py":
            File = appfile.joinpath("api").joinpath("serializers.py")
            #with open(str(File.absolute())) as f:
            f = io.open(str(File.absolute()), 'r')
            #print("ProcessClassSingleScript Function - applying Class To Script : Serializer.py" + ClassName)
            for line in f:
                if ClassName+"_Serializer(serializers.ModelSerializer)" == line: #IN WILL CREATE NAMING ISSUES
                    found=True
            f.close()
                    
            if(found==False):
                
                f = io.open(str(File.absolute()), 'a')
                f.write("\n")
                f.write("\n")
                f.write("class " + ClassName + "_Serializer(serializers.ModelSerializer): \n")
                f.write(spacing + "class Meta: \n")
                f.write(spacing + spacing + "model = " + ClassName +"\n")
                f.write(spacing + spacing + "fields = '__all__' \n")
                f.write("\n")
                f.close()
                        
        elif ScriptFile=="views.py":
            #print("ProcessClassSingleScript Function - applying Class To Script : views.py" + ClassName)
            
            File = appfile.joinpath("api").joinpath("views.py")
            f = io.open(str(File.absolute()),'r')

            for line in f:
                if ClassName+"_Serializer(serializers.ModelSerializer)" ==  line:
                    found=True
            f.close()
        
            if (found==False):
                #ViewSet(viewsets.ModelViewSet):
                f = io.open(str(File.absolute()),'a')
                f.write("\n")
                f.write("class " + ClassName +"_ViewSet(viewsets.ModelViewSet): \n")
                f.write(spacing+ "queryset = "+ClassName+ ".objects.all()\n")
                f.write(spacing+ "serializer_class = " + ClassName+"_Serializer\n")
                f.write("\n")
                f.close()
                
        elif ScriptFile == "urls.py":
            #print("ProcessClassSingleScript Function - applying Class To Script : Urls.py" + ClassName)
            routerpattern = "router.register(r'" + ClassName.casefold() +"', "+ClassName + "_ViewSet" +")"
            
            
            File = appfile.joinpath("api").joinpath("urls.py")
            f = io.open(str(File.absolute()),'r')
            content = f.readlines()

            
            
            for index in range(len(content)):
                content[index]
                if routerpattern ==  content[index]:
                    return 
                else:#It does not exist
                    
                    if index==len(content)-1 : #not found at the end.
                        f.close()
                        #Searching for key words:
                        for i in range(len(content)):
                            
                            if "##RegisteringRouter" in content[i]:
                                content.insert(i+1,"\n")
                                content.insert(i+2,routerpattern )
                                break #do not repeat upon other existence
                                
                        f = io.open(str(File.absolute()),'w+')
                        f.writelines(content)
                        f.close()
     
        
    def ProcessClassAllScripts(self,AppDir,ClassName):
        scripts = ["serializers.py","views.py","urls.py"]
        for script in scripts:
            #print("ProcessClassAllScripts Function - applying Scripts :" + script)
            self.ProcessClassSingleScript(AppDir,ClassName, script, self.spacing)
            
        
    def ProcessApp(self,AppDir):
        Classes = self.GetModelsOfApp(AppDir)
        for cls in Classes:
            self.ProcessClassAllScripts(AppDir, cls)
            #print("ProcessApp Function - applying Clsass :" + cls)
            
    def ApplyProject(self):
        for AppPath in self.appsPath:
            self.CreateAPIFiles(AppPath)
            self.ProcessApp(AppPath)
            #print("ApplyProjectFunction - applying App :" + AppPath)
            
    
        
    def CreateAPIFiles(self, AppPath, indenting=4):
        
        #check for api folder
        app = Path(AppPath)
        apiFolder = app.glob("**/api/")
        temp = []
        
        if indenting==4:
            spacing = "    "
        
        for i in apiFolder:
            temp.append(i)
            #print(len(temp))
        if len(temp)== 0: #folder exist >> check for file
            #print("making .. ")
            os.mkdir(app.joinpath("api"))
            files = ["serializers.py","views.py","urls.py"]
            for filename in files:
                filePath = app.joinpath("api").joinpath(filename)
                #print(file.absolute())
                file = io.open(str(filePath.absolute()) , 'a')
                
                filetype = filePath.name
                if filetype == "serializers.py":
                    file.write("from rest_framework.serializers import ModelSerializer\n")
                    file.write("from rest_framework import serializers\n")
                    file.write("from " + app.name+".models import *")
                elif filetype == "views.py":
                    file.write("from rest_framework import viewsets, permissions\n")
                    file.write("from " + app.name +".models import * \n")
                    file.write("from " + app.name+".api.serializers import * \n")
                elif filetype == "urls.py":
                    file.write("from django.urls import path, include \n")
                    file.write("from rest_framework import routers\n")
                    file.write("from " + app.name+".api.views import * \n")  
                    file.write("\n")
                    file.write("\n")
                    file.write("from rest_framework import routers")
                    file.write("\n")
                    file.write("\n")
                    file.write("router = routers.SimpleRouter()")
                    file.write("\n")
                    file.write("\n")
                    file.write("###RegisteringRouter")
                    file.write("\n")
                    file.write("\n")
                    file.write("urlpatterns = [\n")
                    file.write(spacing + "path('', include(router.urls)),\n")
                    file.write("\n")
                    file.write(']')
            file.close()
            

    def GetSubFolders(self, path=None):
        #listing folders
            #subfolders = os.listdir(self.ProjectPath)
            #for sfolder in subfolders:
        if(path==None):
            path= self.path
            
        subfolderlist= []
        CPath = Path(path)
        subfolders = CPath.glob("**/")
        for subfolder in subfolders:
            subfolderlist.append(subfolder.name)
            #print(subfolder.name)
        try:
            Results = subfolderlist[1:]
        except:
            Results =[]
        return Results
    
    def checkIfIsApp(self, sign='models.py',path=None):
        if(path==None):
            path= self.path
        CPath = Path(path)
        
        #TODO Check if all requirements are complete
        
        pattern = "**/**/"+sign
        #print("CheckIfIsApp  " + sign)
        #print("checkIfIsApp  " + pattern)
        subfolderlist = []
        subfolders = CPath.glob(pattern)
        for subfolder in subfolders:
            subfolderlist.append(subfolder.name)
        Results = False
        if len(subfolderlist)>0:
            Results=True
            
        return Results

    
    def GetApps(self, sign='models.py', ReturnPath=False,path=None):
        AppNames = []
        AppPaths = []

        if(path==None):
            path= self.path
            
        listFolder = self.GetSubFolders(path)
        #print ("GetApps function  (1)" +str(len(listFolder)))
        for name in listFolder:
            appDir = self.Path.joinpath(name)
            appDir = str(appDir.absolute())
            Isapp = self.checkIfIsApp(path= appDir)
            #print ("GetApps function  (2)" )
            #print ("appDir " + appDir)
            #print ("Isapp " + str(Isapp))
            
            
            if Isapp==True:
                AppNames.append(name)
                AppPaths.append(appDir)
        Results=[]
        if ReturnPath==False:
            Results =AppNames
        else:
            Results = AppPaths
        return Results 
           
#=====Testing====================================================================
from pathlib import Path
def Testing():
	a = Path(os.getcwd())
	E = AutoDRF(ProjectPath=a)
	E.ApplyProject()     
   
