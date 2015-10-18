import os
import jarray
import inspect
import subprocess
from java.lang import Class
from java.lang import System
from java.sql  import DriverManager, SQLException
from java.util.logging import Level
from java.io import File
from javax.swing.filechooser import FileNameExtensionFilter
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.datamodel import ContentUtils

class YaraIngestModuleFactory(IngestModuleFactoryAdapter):
        
    moduleName = "YARA Scan"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Scan YARA Signatures"

    def getModuleVersionNumber(self):
        return "1.0"

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        return YaraIngestModule()

class YaraIngestModule(DataSourceIngestModule):

    _logger = Logger.getLogger(YaraIngestModuleFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self):
        self.context = None

    def startUp(self, context):
        self.context = context
        
        ###---EDIT HERE---###
        self.path_to_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yara.exe")
        self.path_to_rules = os.path.join(os.path.dirname(os.path.abspath(__file__)), "all.yara")   
        ###---EDIT HERE---###

    def process(self, dataSource, progressBar):
        
        progressBar.switchToIndeterminate()
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        
        ###---EDIT HERE---###
        files = fileManager.findFiles(dataSource, "%.doc", "%")
        ###---EDIT HERE---###

        numFiles = len(files)
        progressBar.switchToDeterminate(numFiles)
        fileCount = 0;

        ###---EDIT HERE---###
        reportPath = os.path.join(Case.getCurrentCase().getCaseDirectory(), "Reports", "YARA.txt")
        ###---EDIT HERE---###
        
        reportHandle = open(reportPath, 'w')
        
        for file in files:

            if self.context.isJobCancelled():
                return IngestModule.ProcessResult.OK

            if (str(file.getKnown()) != "KNOWN"):

                exportPath = os.path.join(Case.getCurrentCase().getTempDirectory(), str(file.getId())+"."+file.getNameExtension())

                ###---EDIT HERE---###
                ContentUtils.writeToFile(file, File(exportPath))
                subprocess.Popen([self.path_to_exe, self.path_to_rules, exportPath], stdout=reportHandle).communicate()[0]
                ###---EDIT HERE---###
                
                reportHandle.write(file.getParentPath()+file.getName()+'\n\n')
            
            self.log(Level.INFO, "Processing file: " + file.getName())
            fileCount += 1
            progressBar.progress(fileCount)
                
        message = IngestMessage.createMessage(IngestMessage.MessageType.DATA,
            "YARA Scan", "Scanned %d Files" % numFiles)
        IngestServices.getInstance().postMessage(message)

        reportHandle.close()
        
        Case.getCurrentCase().addReport(reportPath, "YARA Scan", "Scanned %d Files" % numFiles)
        
        return IngestModule.ProcessResult.OK
