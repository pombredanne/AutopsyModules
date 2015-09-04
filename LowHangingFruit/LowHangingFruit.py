import jarray
import inspect
from java.lang import System
from java.util.logging import Level
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
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import FileIngestModule
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import IngestModuleGlobalSettingsPanel
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.autopsy.coreutils import Logger
from java.lang import IllegalArgumentException

import os

class LowHangingFruitFactory(IngestModuleFactoryAdapter):
    
    def __init__(self):
        self.settings = None

    moduleName = "Low Hanging Fruit"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Unique hashes not previously seen to run against external sources"

    def getModuleVersionNumber(self):
        return "1.0"

    def hasIngestJobSettingsPanel(self):
        return True

    def getIngestJobSettingsPanel(self, settings):
        self.settings = settings
        return LowHangingFruitUISettingsPanel(self.settings)

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, ingestOptions):
        return LowHangingFruit(self.settings)

class LowHangingFruit(FileIngestModule):

    _logger = Logger.getLogger(LowHangingFruitFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self, settings):
        self.local_settings = settings

    def startUp(self, context):
        global md5
        md5 = []

    def process(self, file):
        
        if(file.getMd5Hash()):
            if (str(file.getKnown()) != "KNOWN"):
                md5.append(file.getMd5Hash())
            
        return IngestModule.ProcessResult.OK

    def shutDown(self):
        noDupes = list(set(md5))
        outPath = os.path.join(Case.getCurrentCase().getCaseDirectory(), "LowHangingFruit.txt")
        outFile = open(outPath,'w')
        for line in noDupes:
            outFile.write(line+'\n')
        outFile.close()

class LowHangingFruitUISettingsPanel(IngestModuleIngestJobSettingsPanel):
    
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

        ret = chooseFile.showDialog(self.panel, "Select SQLite Database")

        if ret == JFileChooser.APPROVE_OPTION:
            file = chooseFile.getSelectedFile()
            text = self.readPath(file)
            self.area.setText(text)

    def readPath(self, file):
        filename = file.getCanonicalPath()
        return filename

    def getSettings(self):
        return self.local_settings
