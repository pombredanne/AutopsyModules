import jarray
import inspect
from java.lang import System
from java.io import File
from java.util.logging import Level
from java.sql  import DriverManager, SQLException
from java.awt import BorderLayout
from javax.swing import BorderFactory
from javax.swing import JTextArea
from javax.swing import JScrollPane
from javax.swing import JButton
from javax.swing import JToolBar
from javax.swing import JPanel
from javax.swing import JFrame
from javax.swing import JCheckBox
from javax.swing import JTextField
from javax.swing import JLabel
from javax.swing import JFileChooser
from javax.swing.filechooser import FileNameExtensionFilter
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import TskData
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import IngestModuleGlobalSettingsPanel
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
from java.lang import IllegalArgumentException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.datamodel import ContentUtils

class MatchMetaInfoIngestModuleFactory(IngestModuleFactoryAdapter):

    def __init__(self):
        self.settings = None

    moduleName = "MatchMeta.Info"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Match Meta Information"

    def getModuleVersionNumber(self):
        return "1.0"
    
    def hasIngestJobSettingsPanel(self):
        return True

    def getIngestJobSettingsPanel(self, settings):
        self.settings = settings
        return MatchMetaInfoUISettingsPanel(self.settings)
    
    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, ingestOptions):
        return MatchMetaInfoIngestModule(self.settings)

class MatchMetaInfoIngestModule(FileIngestModule):

    _logger = Logger.getLogger(MatchMetaInfoIngestModuleFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self, settings):
        self.local_settings = settings

    def startUp(self, context):
        pass

    def process(self, file):
        try:
            if(filename):
                
                dbConn = DriverManager.getConnection("jdbc:sqlite:%s"  % filename)
                stmt = dbConn.createStatement()

                path = file.getParentPath()+file.getName()

                resultSet = stmt.executeQuery("SELECT * FROM META WHERE Path == '%s'" % path)
                
                if(resultSet.next()):
                    temp = "Future Improvement"                
                else:
                    art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT)
                    att = BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_SET_NAME.getTypeID(), 
                        MatchMetaInfoIngestModuleFactory.moduleName, "Unknown Meta")
                    art.addAttribute(att)
  
                    IngestServices.getInstance().fireModuleDataEvent(
                        ModuleDataEvent(MatchMetaInfoIngestModuleFactory.moduleName, 
                            BlackboardArtifact.ARTIFACT_TYPE.TSK_INTERESTING_FILE_HIT, None));

                stmt.close()
                dbConn.close()
                
        except:
            pass
    


        return IngestModule.ProcessResult.OK
 
    def shutDown(self):
        None

class MatchMetaInfoUISettingsPanel(IngestModuleIngestJobSettingsPanel):
    
    def __init__(self, settings):
        self.local_settings = settings
        self.initComponents()

    def initComponents(self):
        self.panel = JPanel()
        self.panel.setLayout(BorderLayout())

        toolbar = JToolBar()
        openb = JButton("Select", actionPerformed=self.onClick)

        toolbar.add(openb)

        self.area = JTextArea()
        self.area.setBorder(BorderFactory.createEmptyBorder(10, 100, 10, 100))

        pane = JScrollPane()
        pane.getViewport().add(self.area)

        self.panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10))
        self.panel.add(pane)
        self.add(self.panel)

        self.add(toolbar)

    def onClick(self, e):

        chooseFile = JFileChooser()
        filter = FileNameExtensionFilter("SQLite", ["sqlite"])
        chooseFile.addChoosableFileFilter(filter)

        ret = chooseFile.showDialog(self.panel, "Select SQLite")

        if ret == JFileChooser.APPROVE_OPTION:
            file = chooseFile.getSelectedFile()
            text = self.readPath(file)
            self.area.setText(text)

    def readPath(self, file):
        global filename
        filename = file.getCanonicalPath()
        return filename

    def getSettings(self):
        return self.local_settings
