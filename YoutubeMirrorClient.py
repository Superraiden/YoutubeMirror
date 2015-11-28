#!/usr/bin/env python

import sqlite3
import datetime
from enum import Enum
import PyQt5
from PyQt5.QtSql import (QSqlDatabase, QSqlQuery)
from PyQt5.QtCore import pyqtSlot
import PyQt5.QtCore as C
import PyQt5.QtMultimedia as M
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QListWidgetItem, QHeaderView, QTableWidgetItem, \
    QAbstractItemView, QLayout
from PyQt5 import QtGui


from PyQt5.QtCore import (pyqtSignal, pyqtSlot, Q_ARG, QAbstractItemModel,
        QFileInfo, qFuzzyCompare, QMetaObject, QModelIndex, QObject, Qt,
        QThread, QTime, QUrl)
from PyQt5.QtGui import QColor, qGray, QImage, QPainter, QPalette
from PyQt5.QtMultimedia import (QAbstractVideoBuffer, QMediaContent,
        QMediaMetaData, QMediaPlayer, QMediaPlaylist, QVideoFrame, QVideoProbe)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog,
        QFormLayout, QHBoxLayout, QLabel, QListView, QMessageBox, QPushButton,
        QSizePolicy, QSlider, QStyle, QToolButton, QVBoxLayout, QWidget)

from YoutubeMirrorClientMain import Ui_MainWindow

class VideoTableStates(Enum):
    VIDLISTMIN = 1
    VIDLISTSMALL = 2
    EQUAL = 3
    VIDDATASMALL = 4
    VIDDATAMIN = 5

class CalculatorForm(QMainWindow):
    def __init__(self, parent=None):
        super(CalculatorForm, self).__init__(parent)
        self.currentTableState = VideoTableStates.EQUAL

        self.videoTableState = 3
        self.url= C.QUrl.fromLocalFile("c:\Lazer.mp3")
        self.content= M.QMediaContent(self.url)
        self.player = M.QMediaPlayer()
        self.player.setMedia(self.content)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        conn = sqlite3.connect('Youtube_MirrorV2.db')
        self.c = conn.cursor()
        self.c.execute('pragma foreign_keys = ON;')
        conn.commit()

        self.ui.tableWidgetVideos.setAlternatingRowColors(True)
        self.ui.tableWidgetChannels.setColumnCount(3)
        self.ui.tableWidgetChannels.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidgetChannels.setHorizontalHeaderLabels(('ID', 'Channel', 'No of Videos'))
        self.ui.tableWidgetChannels.verticalHeader().setVisible(False)
        self.ui.tableWidgetChannels.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidgetChannels.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidgetChannels.cellClicked.connect(self.cell_was_clicked)
        self.ui.tableWidgetChannels.setColumnHidden(0, True)
        self.ui.tableWidgetChannels.setColumnWidth(1, 170)

        self.ui.tableWidgetVideos.setColumnCount(6)
        self.ui.tableWidgetVideos.setHorizontalHeaderLabels(('ID', 'Video Name', 'Video ID', "Status", "Upload Date", "Download Date"))
        self.ui.tableWidgetVideos.verticalHeader().setVisible(False)
        self.ui.tableWidgetVideos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidgetVideos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidgetVideos.cellClicked.connect(self.videocell_was_clicked)
        self.ui.tableWidgetVideos.setColumnWidth(1, 300)
        self.ui.tableWidgetVideos.setColumnWidth(4, 150)
        self.ui.tableWidgetVideos.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidgetVideos.setColumnHidden(0, True)

        self.ui.btnResizeUp.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.ui.btnResizeDown.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.ui.toolButtonRefresh.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))

        self.ui.btnResizeUp.clicked.connect(self.btnResizeUp_pressed)
        self.ui.btnResizeDown.clicked.connect(self.btnResizeDown_pressed)
        self.ui.pushButtonAdd.clicked.connect(self.pushButtonAdd_pressed)
        #self.style().standardIcon(QStyle.SP_MediaSkipForward))btnResizeUp

    def load_initial_data(self):
        # where c is the cursor
        self.c.execute('''SELECT * FROM channel''')
        channel_rows = self.c.fetchall()

        for channel_row in channel_rows:
            inx = channel_rows.index(channel_row)
            self.ui.tableWidgetChannels.insertRow(inx)
            # add more if there is more columns in the database.
            self.c.execute('''SELECT count(id) FROM video WHERE channelId IS ''' + str(channel_row[0]))
            video_count = self.c.fetchall()[0][0]

            self.ui.tableWidgetChannels.setItem(inx, 0, QTableWidgetItem(str(channel_row[0])))
            self.ui.tableWidgetChannels.setItem(inx, 1, QTableWidgetItem(channel_row[1]))
            self.ui.tableWidgetChannels.setItem(inx, 2, QTableWidgetItem(str(video_count)

            ))

    def getSameRowCell(self, widget, columnName):
       row = widget.currentItem().row()

       #loop through headers and find column number for given column name
       headerCount = widget.columnCount()
       for x in range(0,headerCount,1):
           headerText = widget.horizontalHeaderItem(x).text()
           if columnName == headerText:
               matchCol = x
               break

       cell = widget.item(row,matchCol).text()   # get cell at row, col

       return cell

    @pyqtSlot()
    def pushButtonAdd_pressed(self):

        pass

    @pyqtSlot() # prevents executing following function twice
    def cell_was_clicked(self):
        self.ui.tableWidgetVideos.clearContents()
        self.ui.tableWidgetVideos.setRowCount(0)

        clickedChannelId = self.getSameRowCell(widget = self.ui.tableWidgetChannels, columnName="ID")
        self.c.execute('''SELECT * FROM video WHERE channelId IS ''' + str(clickedChannelId))
        video_rows = self.c.fetchall()

        #self.player.play()
        #self.player.stateChanged.connect(  self.player.stop() )

        for video_row in video_rows:
            inx = video_rows.index(video_row)
            self.ui.tableWidgetVideos.insertRow(inx)

            self.ui.tableWidgetVideos.setItem(inx, 0, QTableWidgetItem(str(video_row[0])))   # Video ID
            self.ui.tableWidgetVideos.setItem(inx, 1, QTableWidgetItem(video_row[4]))   # Video Name
            self.ui.tableWidgetVideos.setItem(inx, 2, QTableWidgetItem(video_row[2]))   # Video ID
            self.ui.tableWidgetVideos.setItem(inx, 3, QTableWidgetItem(video_row[3]))   # Status
            self.ui.tableWidgetVideos.setItem(inx, 4, QTableWidgetItem(datetime.datetime.fromtimestamp(
                                                                        int(video_row[6])
                                                                        ).strftime('%Y-%m-%d %H:%M:%S')))   # Upload Date
            self.ui.tableWidgetVideos.setItem(inx, 5, QTableWidgetItem(datetime.datetime.fromtimestamp(
                                                                        int(video_row[7])
                                                                        ).strftime('%Y-%m-%d %H:%M:%S')))   # Download Date

    @pyqtSlot() # prevents executing following function twice
    def videocell_was_clicked(self):
        clickedVideoId = self.getSameRowCell(widget = self.ui.tableWidgetVideos, columnName="ID")
        self.c.execute('''SELECT * FROM video WHERE id IS ''' + str(clickedVideoId))
        video_row = self.c.fetchall()[0]
        self.ui.txtName.setText(video_row[4])
        self.ui.txtDesc.setText(video_row[5])
        self.ui.txtLLocalLocation.setText(video_row[8])
        self.ui.txtUploadDate.setText(datetime.datetime.fromtimestamp(
                                                                        int(video_row[6])
                                                                        ).strftime('%Y-%m-%d %H:%M:%S'))
        self.ui.txtDownloadDate.setText(datetime.datetime.fromtimestamp(
                                                                        int(video_row[7])
                                                                        ).strftime('%Y-%m-%d %H:%M:%S'))

        player.playlist.clear()
        newfiles = [video_row[8]]
        player.addToPlaylist(newfiles)
        self.ui.mainVideoContainer.sizeConstrain = QLayout.SetMinimumSize

    @pyqtSlot()
    def btnResizeUp_pressed(self):
        if self.currentTableState == VideoTableStates.VIDLISTMIN:
            pass
        elif self.currentTableState == VideoTableStates.VIDLISTSMALL:
            self.ui.tableWidgetVideos.setMaximumHeight(100)
            self.ui.tableWidgetVideos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.currentTableState = VideoTableStates.VIDLISTMIN
        elif self.currentTableState == VideoTableStates.EQUAL:
            self.ui.tableWidgetVideos.setMaximumHeight(200)
            self.ui.tableWidgetVideos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.currentTableState = VideoTableStates.VIDLISTSMALL
        elif self.currentTableState == VideoTableStates.VIDDATASMALL:
            self.ui.groupBox.setMaximumHeight(10000)
            player.setMaximumHeight(10000)
            self.ui.tableWidgetVideos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.currentTableState = VideoTableStates.EQUAL

    @pyqtSlot()
    def btnResizeDown_pressed(self):
        if self.currentTableState == VideoTableStates.VIDLISTMIN:
            self.ui.tableWidgetVideos.setMaximumHeight(200)
            self.ui.tableWidgetVideos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.currentTableState = VideoTableStates.VIDLISTSMALL
        elif self.currentTableState == VideoTableStates.VIDLISTSMALL:
            self.ui.tableWidgetVideos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.ui.tableWidgetVideos.setMaximumHeight(10000)
            self.currentTableState = VideoTableStates.EQUAL
        elif self.currentTableState == VideoTableStates.EQUAL:
            self.ui.groupBox.setMaximumHeight(200)
            player.setMaximumHeight(200)
            self.ui.tableWidgetVideos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.currentTableState = VideoTableStates.VIDDATASMALL


class VideoWidget(QVideoWidget):

    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
        #self.setFixedHeight(200)
        #self.setFixedWidth(355)

        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
            event.accept()
        elif event.key() == Qt.Key_Enter and event.modifiers() & Qt.Key_Alt:
            self.setFullScreen(not self.isFullScreen())
            event.accept()
        else:
            super(VideoWidget, self).keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.setFullScreen(not self.isFullScreen())
        event.accept()

class PlayerControls(QWidget):

    play = pyqtSignal()
    pause = pyqtSignal()
    stop = pyqtSignal()
    next = pyqtSignal()
    previous = pyqtSignal()
    changeVolume = pyqtSignal(int)
    changeMuting = pyqtSignal(bool)
    changeRate = pyqtSignal(float)

    def __init__(self, parent=None):
        super(PlayerControls, self).__init__(parent)

        self.playerState = QMediaPlayer.StoppedState
        self.playerMuted = False
        self.playerMuted = False

        self.playButton = QToolButton(clicked=self.playClicked)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.stopButton = QToolButton(clicked=self.stop)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.setEnabled(False)

        self.nextButton = QToolButton(clicked=self.next)
        self.nextButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaSkipForward))

        self.previousButton = QToolButton(clicked=self.previous)
        self.previousButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaSkipBackward))

        self.muteButton = QToolButton(clicked=self.muteClicked)
        self.muteButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaVolume))

        self.volumeSlider = QSlider(Qt.Horizontal,
                sliderMoved=self.changeVolume)
        self.volumeSlider.setRange(0, 100)

        self.rateBox = QComboBox(activated=self.updateRate)
        self.rateBox.addItem("0.5x", 0.5)
        self.rateBox.addItem("1.0x", 1.0)
        self.rateBox.addItem("2.0x", 2.0)
        self.rateBox.setCurrentIndex(1)

        layout = QHBoxLayout()
        #layout.sizeConstraint = QLayout.SetMinimumSize #<<<<<<<<<<<<
        layout.setContentsMargins(0, 0, -10, 0)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.previousButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.muteButton)
        layout.addWidget(self.volumeSlider)
        layout.addWidget(self.rateBox)


        self.setLayout(layout)

    def state(self):
        return self.playerState

    def setState(self,state):
        if state != self.playerState:
            self.playerState = state

            if state == QMediaPlayer.StoppedState:
                self.stopButton.setEnabled(False)
                self.playButton.setIcon(
                        self.style().standardIcon(QStyle.SP_MediaPlay))
            elif state == QMediaPlayer.PlayingState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(
                        self.style().standardIcon(QStyle.SP_MediaPause))
            elif state == QMediaPlayer.PausedState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(
                        self.style().standardIcon(QStyle.SP_MediaPlay))

    def volume(self):
        return self.volumeSlider.value()

    def setVolume(self, volume):
        self.volumeSlider.setValue(volume)

    def isMuted(self):
        return self.playerMuted

    def setMuted(self, muted):
        if muted != self.playerMuted:
            self.playerMuted = muted

            self.muteButton.setIcon(
                    self.style().standardIcon(
                            QStyle.SP_MediaVolumeMuted if muted else QStyle.SP_MediaVolume))

    def playClicked(self):
        if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.play.emit()
        elif self.playerState == QMediaPlayer.PlayingState:
            self.pause.emit()

    def muteClicked(self):
        self.changeMuting.emit(not self.playerMuted)

    def playbackRate(self):
        return self.rateBox.itemData(self.rateBox.currentIndex())

    def setPlaybackRate(self, rate):
        for i in range(self.rateBox.count()):
            if qFuzzyCompare(rate, self.rateBox.itemData(i)):
                self.rateBox.setCurrentIndex(i)
                return

        self.rateBox.addItem("%dx" % rate, rate)
        self.rateBox.setCurrentIndex(self.rateBox.count() - 1)

    def updateRate(self):
        self.changeRate.emit(self.playbackRate())

class newSlider(QSlider):
    def __init__(self, QWidget, parent=None):
        super(QSlider, self).__init__(Qt.Horizontal)
    def mousePressEvent(self, QMouseEvent):
        print("fug :-D")

        if QMouseEvent.button() == Qt.LeftButton:
            time = self.minimum() + ((self.maximum()-self.minimum()) * QMouseEvent.x()) / self.width()
            self.parent().seek(time)
            self.setValue(time)

        QSlider.mousePressEvent(self, QMouseEvent)

class Player(QWidget):

    fullScreenChanged = pyqtSignal(bool)

    def __init__(self, playlist, parent=None):
        super(Player, self).__init__(parent)

        self.colorDialog = None
        self.trackInfo = ""
        self.statusInfo = ""
        self.duration = 0

        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.metaDataChanged.connect(self.metaDataChanged)
        self.playlist.currentIndexChanged.connect(self.playlistPositionChanged)
        self.player.mediaStatusChanged.connect(self.statusChanged)
        self.player.bufferStatusChanged.connect(self.bufferingProgress)
        self.player.videoAvailableChanged.connect(self.videoAvailableChanged)
        self.player.error.connect(self.displayErrorMessage)

        self.videoWidget = VideoWidget()
        self.player.setVideoOutput(self.videoWidget)

        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        self.playlistView = QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(
                self.playlistModel.index(self.playlist.currentIndex(), 0))

        self.playlistView.activated.connect(self.jump)

        self.slider = newSlider(Qt.Horizontal, parent=self)
        #self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.player.duration() / 1000)
        #self.slider.setFixedHeight(20)
        #self.slider.setContentsMargins(100, 100, 100, 100)

        self.labelDuration = QLabel()
        self.slider.sliderMoved.connect(self.seek)
        #self.slider.sliderChange
        #self.slider.mousePressEvent(QMouseEvent=QMouseEvent)


        #self.labelHistogram = QLabel()
        #self.labelHistogram.setText("Histogram:")
        #self.histogram = HistogramWidget()
        #histogramLayout = QHBoxLayout()
        #histogramLayout.addWidget(self.labelHistogram)
        #histogramLayout.addWidget(self.histogram, 1)

        self.probe = QVideoProbe()
        #self.probe.videoFrameProbed.connect(self.histogram.processFrame)
        self.probe.setSource(self.player)

        openButton = QPushButton("Open", clicked=self.open)

        controls = PlayerControls()
        controls.setState(self.player.state())
        controls.setVolume(self.player.volume())
        controls.setMuted(controls.isMuted())

        controls.play.connect(self.player.play)
        controls.pause.connect(self.player.pause)
        controls.stop.connect(self.player.stop)
        controls.next.connect(self.playlist.next)
        controls.previous.connect(self.previousClicked)
        controls.changeVolume.connect(self.player.setVolume)
        controls.changeMuting.connect(self.player.setMuted)
        controls.changeRate.connect(self.player.setPlaybackRate)
        controls.stop.connect(self.videoWidget.update)

        self.player.stateChanged.connect(controls.setState)
        self.player.volumeChanged.connect(controls.setVolume)
        self.player.mutedChanged.connect(controls.setMuted)

        self.fullScreenButton = QPushButton("FullScreen")
        self.fullScreenButton.setCheckable(True)

        self.colorButton = QPushButton("Color Options...")
        self.colorButton.setEnabled(False)
        self.colorButton.clicked.connect(self.showColorDialog)

        displayLayout = QHBoxLayout()
        displayLayout.addWidget(self.videoWidget, 1)
        #displayLayout.addWidget(self.playlistView)

        controlLayout = QHBoxLayout()

        controlLayout.setContentsMargins(0, 0, 0, 0)
        #controlLayout.addWidget(openButton)
        #controlLayout.addStretch(1)
        controlLayout.addWidget(controls)
        #controlLayout.addStretch(1)
        controlLayout.addWidget(self.fullScreenButton)
        controlLayout.addWidget(self.colorButton)

        layout = QVBoxLayout()


        hLayout = QVBoxLayout()
        hLayout.addWidget(self.slider)
        hLayout.addWidget(self.labelDuration)
        hLayout.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(displayLayout)
        layout.addLayout(hLayout)
        layout.addLayout(controlLayout)

        calculator.ui.gridLayout_8.addWidget(self)
        self.setLayout(layout)

        if not self.player.isAvailable():
            QMessageBox.warning(self, "Service not available",
                    "The QMediaPlayer object does not have a valid service.\n"
                    "Please check the media service plugins are installed.")

            controls.setEnabled(False)
            self.playlistView.setEnabled(False)
            openButton.setEnabled(False)
            self.colorButton.setEnabled(False)
            self.fullScreenButton.setEnabled(False)

        self.metaDataChanged()

        self.addToPlaylist(playlist)

    def ass(self):
        print("ass")
    def asss(self):
        print("asss")

    def open(self):
        fileNames, _ = QFileDialog.getOpenFileNames(self, "Open Files")
        self.addToPlaylist(fileNames)

    def addToPlaylist(self, fileNames):
        for name in fileNames:
            fileInfo = QFileInfo(name)
            if fileInfo.exists():
                url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())
                if fileInfo.suffix().lower() == 'm3u':
                    self.playlist.load(url)
                else:
                    self.playlist.addMedia(QMediaContent(url))
            else:
                url = QUrl(name)
                if url.isValid():
                    self.playlist.addMedia(QMediaContent(url))

    def durationChanged(self, duration):
        duration /= 1000

        self.duration = duration
        self.slider.setMaximum(duration)

    def positionChanged(self, progress):
        progress /= 1000

        if not self.slider.isSliderDown():
            self.slider.setValue(progress)

        self.updateDurationInfo(progress)

    def metaDataChanged(self):
        if self.player.isMetaDataAvailable():
            self.setTrackInfo("%s - %s" % (
                    self.player.metaData(QMediaMetaData.AlbumArtist),
                    self.player.metaData(QMediaMetaData.Title)))

    def previousClicked(self):
        # Go to the previous track if we are within the first 5 seconds of
        # playback.  Otherwise, seek to the beginning.
        if self.player.position() <= 5000:
            self.playlist.previous()
        else:
            self.player.setPosition(0)

    def jump(self, index):
        if index.isValid():
            self.playlist.setCurrentIndex(index.row())
            self.player.play()

    def playlistPositionChanged(self, position):
        self.playlistView.setCurrentIndex(
                self.playlistModel.index(position, 0))

    def seek(self, seconds):
        self.player.setPosition(seconds * 1000)

    def statusChanged(self, status):
        self.handleCursor(status)

        if status == QMediaPlayer.LoadingMedia:
            self.setStatusInfo("Loading...")
        elif status == QMediaPlayer.StalledMedia:
            self.setStatusInfo("Media Stalled")
        elif status == QMediaPlayer.EndOfMedia:
            QApplication.alert(self)
        elif status == QMediaPlayer.InvalidMedia:
            self.displayErrorMessage()
        else:
            self.setStatusInfo("")

    def handleCursor(self, status):
        if status in (QMediaPlayer.LoadingMedia, QMediaPlayer.BufferingMedia, QMediaPlayer.StalledMedia):
            self.setCursor(Qt.BusyCursor)
        else:
            self.unsetCursor()

    def bufferingProgress(self, progress):
        self.setStatusInfo("Buffering %d%" % progress)

    def videoAvailableChanged(self, available):
        if available:
            self.fullScreenButton.clicked.connect(
                    self.videoWidget.setFullScreen)
            self.videoWidget.fullScreenChanged.connect(
                    self.fullScreenButton.setChecked)

            if self.fullScreenButton.isChecked():
                self.videoWidget.setFullScreen(True)
        else:
            self.fullScreenButton.clicked.disconnect(
                    self.videoWidget.setFullScreen)
            self.videoWidget.fullScreenChanged.disconnect(
                    self.fullScreenButton.setChecked)

            self.videoWidget.setFullScreen(False)

        self.colorButton.setEnabled(available)

    def setTrackInfo(self, info):
        self.trackInfo = info

        if self.statusInfo != "":
            self.setWindowTitle("%s | %s" % (self.trackInfo, self.statusInfo))
        else:
            self.setWindowTitle(self.trackInfo)

    def setStatusInfo(self, info):
        self.statusInfo = info

        if self.statusInfo != "":
            self.setWindowTitle("%s | %s" % (self.trackInfo, self.statusInfo))
        else:
            self.setWindowTitle(self.trackInfo)

    def displayErrorMessage(self):
        self.setStatusInfo(self.player.errorString())

    def updateDurationInfo(self, currentInfo):
        duration = self.duration
        if currentInfo or duration:
            currentTime = QTime((currentInfo/3600)%60, (currentInfo/60)%60,
                    currentInfo%60, (currentInfo*1000)%1000)
            totalTime = QTime((duration/3600)%60, (duration/60)%60,
                    duration%60, (duration*1000)%1000);

            format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
            tStr = currentTime.toString(format) + " / " + totalTime.toString(format)
        else:
            tStr = ""

        self.labelDuration.setText(tStr)

    def showColorDialog(self):
        if self.colorDialog is None:
            brightnessSlider = QSlider(Qt.Horizontal)
            brightnessSlider.setRange(-100, 100)
            brightnessSlider.setValue(self.videoWidget.brightness())
            brightnessSlider.sliderMoved.connect(
                    self.videoWidget.setBrightness)
            self.videoWidget.brightnessChanged.connect(
                    brightnessSlider.setValue)

            contrastSlider = QSlider(Qt.Horizontal)
            contrastSlider.setRange(-100, 100)
            contrastSlider.setValue(self.videoWidget.contrast())
            contrastSlider.sliderMoved.connect(self.videoWidget.setContrast)
            self.videoWidget.contrastChanged.connect(contrastSlider.setValue)

            hueSlider = QSlider(Qt.Horizontal)
            hueSlider.setRange(-100, 100)
            hueSlider.setValue(self.videoWidget.hue())
            hueSlider.sliderMoved.connect(self.videoWidget.setHue)
            self.videoWidget.hueChanged.connect(hueSlider.setValue)

            saturationSlider = QSlider(Qt.Horizontal)
            saturationSlider.setRange(-100, 100)
            saturationSlider.setValue(self.videoWidget.saturation())
            saturationSlider.sliderMoved.connect(
                    self.videoWidget.setSaturation)
            self.videoWidget.saturationChanged.connect(
                    saturationSlider.setValue)

            layout = QFormLayout()
            layout.addRow("Brightness", brightnessSlider)
            layout.addRow("Contrast", contrastSlider)
            layout.addRow("Hue", hueSlider)
            layout.addRow("Saturation", saturationSlider)

            button = QPushButton("Close")
            layout.addRow(button)

            self.colorDialog = QDialog(self)
            self.colorDialog.setWindowTitle("Color Options")
            self.colorDialog.setLayout(layout)

            button.clicked.connect(self.colorDialog.close)

        self.colorDialog.show()

class PlaylistModel(QAbstractItemModel):

    Title, ColumnCount = range(2)

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)

        self.m_playlist = None

    def rowCount(self, parent=QModelIndex()):
        return self.m_playlist.mediaCount() if self.m_playlist is not None and not parent.isValid() else 0

    def columnCount(self, parent=QModelIndex()):
        return self.ColumnCount if not parent.isValid() else 0

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column) if self.m_playlist is not None and not parent.isValid() and row >= 0 and row < self.m_playlist.mediaCount() and column >= 0 and column < self.ColumnCount else QModelIndex()

    def parent(self, child):
        return QModelIndex()

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            if index.column() == self.Title:
                location = self.m_playlist.media(index.row()).canonicalUrl()
                return QFileInfo(location.path()).fileName()

            return self.m_data[index]

        return None

    def playlist(self):
        return self.m_playlist

    def setPlaylist(self, playlist):
        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.disconnect(
                    self.beginInsertItems)
            self.m_playlist.mediaInserted.disconnect(self.endInsertItems)
            self.m_playlist.mediaAboutToBeRemoved.disconnect(
                    self.beginRemoveItems)
            self.m_playlist.mediaRemoved.disconnect(self.endRemoveItems)
            self.m_playlist.mediaChanged.disconnect(self.changeItems)

        self.beginResetModel()
        self.m_playlist = playlist

        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.connect(
                    self.beginInsertItems)
            self.m_playlist.mediaInserted.connect(self.endInsertItems)
            self.m_playlist.mediaAboutToBeRemoved.connect(
                    self.beginRemoveItems)
            self.m_playlist.mediaRemoved.connect(self.endRemoveItems)
            self.m_playlist.mediaChanged.connect(self.changeItems)

        self.endResetModel()

    def beginInsertItems(self, start, end):
        self.beginInsertRows(QModelIndex(), start, end)

    def endInsertItems(self):
        self.endInsertRows()

    def beginRemoveItems(self, start, end):
        self.beginRemoveRows(QModelIndex(), start, end)

    def endRemoveItems(self):
        self.endRemoveRows()

    def changeItems(self, start, end):
        self.dataChanged.emit(self.index(start, 0),
                self.index(end, self.ColumnCount))

if __name__ == '__main__':
    import sys
    import json

    app = QApplication(sys.argv)
    calculator = CalculatorForm()
    calculator.show()
    calculator.load_initial_data()

    player = Player(sys.argv[1:])
    player.show()

    sys.exit(app.exec_())
