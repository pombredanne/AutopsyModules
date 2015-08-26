import jarray
import inspect
from java.lang import System
from java.util.logging import Level
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import TskData
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import FileIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager

import os

class GoldBuildIngestModuleFactory(IngestModuleFactoryAdapter):

    moduleName = "Gold Build"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Generate Gold Build Hash Text File"

    def getModuleVersionNumber(self):
        return "1.0"

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, ingestOptions):
        return GoldBuildIngestModule()

class GoldBuildIngestModule(FileIngestModule):
    
    _logger = Logger.getLogger(GoldBuildIngestModuleFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def startUp(self, context):
        global md5
        md5 = []

    def process(self, file):

        if ((file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNALLOC_BLOCKS) or 
            (file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNUSED_BLOCKS) or 
            (file.isFile() == False)):
            return IngestModule.ProcessResult.OK
          
        if (file.getMd5Hash()):
            md5.append(file.getMd5Hash())
            
        return IngestModule.ProcessResult.OK
 
    def shutDown(self):
        noDupes = list(set(md5))
        outPath = os.path.join(Case.getCurrentCase().getCaseDirectory(), "GoldBuild.txt")
        outFile = open(outPath,'w')
        for line in noDupes:
            outFile.write(line+'\n')
        outFile.close()
