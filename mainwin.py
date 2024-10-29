# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwin.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLayout, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QWidget)

from qfluentwidgets import (CaptionLabel, CardWidget, ComboBox, LargeTitleLabel,
    LineEdit, PushButton, ToolButton)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(494, 461)
        font = QFont()
        font.setFamilies([u"Microsoft YaHei"])
        MainWindow.setFont(font)
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.actionOpen_Audio_File = QAction(MainWindow)
        self.actionOpen_Audio_File.setObjectName(u"actionOpen_Audio_File")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        self.actionOpen_Audio_File.setIcon(icon)
        self.actionReadGenConfig = QAction(MainWindow)
        self.actionReadGenConfig.setObjectName(u"actionReadGenConfig")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew))
        self.actionReadGenConfig.setIcon(icon1)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit))
        self.actionExit.setIcon(icon2)
        self.actionOpen_config_file = QAction(MainWindow)
        self.actionOpen_config_file.setObjectName(u"actionOpen_config_file")
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        self.actionOpen_config_file.setIcon(icon3)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        self.actionAbout.setIcon(icon4)
        self.actionLicense = QAction(MainWindow)
        self.actionLicense.setObjectName(u"actionLicense")
        icon5 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpFaq))
        self.actionLicense.setIcon(icon5)
        self.actionRelease_Page = QAction(MainWindow)
        self.actionRelease_Page.setObjectName(u"actionRelease_Page")
        icon6 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoHome))
        self.actionRelease_Page.setIcon(icon6)
        self.actionOpenDir = QAction(MainWindow)
        self.actionOpenDir.setObjectName(u"actionOpenDir")
        icon7 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FolderOpen))
        self.actionOpenDir.setIcon(icon7)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.frame_2 = CardWidget(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.reqpar_Label = LargeTitleLabel(self.frame_2)
        self.reqpar_Label.setObjectName(u"reqpar_Label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reqpar_Label.sizePolicy().hasHeightForWidth())
        self.reqpar_Label.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setFamilies([u"Microsoft YaHei"])
        font1.setPointSize(12)
        self.reqpar_Label.setFont(font1)

        self.gridLayout.addWidget(self.reqpar_Label, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.artist_Label = CaptionLabel(self.frame_2)
        self.artist_Label.setObjectName(u"artist_Label")
        font2 = QFont()
        font2.setFamilies([u"Microsoft YaHei"])
        font2.setPointSize(10)
        self.artist_Label.setFont(font2)

        self.horizontalLayout.addWidget(self.artist_Label)

        self.artist_LineEdit = LineEdit(self.frame_2)
        self.artist_LineEdit.setObjectName(u"artist_LineEdit")

        self.horizontalLayout.addWidget(self.artist_LineEdit)

        self.title_Label = CaptionLabel(self.frame_2)
        self.title_Label.setObjectName(u"title_Label")
        self.title_Label.setFont(font2)

        self.horizontalLayout.addWidget(self.title_Label)

        self.title_LineEdit = LineEdit(self.frame_2)
        self.title_LineEdit.setObjectName(u"title_LineEdit")

        self.horizontalLayout.addWidget(self.title_LineEdit)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_2, 0, 0, 1, 1)

        self.frame = CardWidget(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setLineWidth(2)
        self.gridLayout_3 = QGridLayout(self.frame)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.optpar_Label = LargeTitleLabel(self.frame)
        self.optpar_Label.setObjectName(u"optpar_Label")
        sizePolicy.setHeightForWidth(self.optpar_Label.sizePolicy().hasHeightForWidth())
        self.optpar_Label.setSizePolicy(sizePolicy)
        self.optpar_Label.setFont(font1)

        self.gridLayout_3.addWidget(self.optpar_Label, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.album_Label = CaptionLabel(self.frame)
        self.album_Label.setObjectName(u"album_Label")
        self.album_Label.setFont(font2)

        self.horizontalLayout_2.addWidget(self.album_Label)

        self.album_LineEdit = LineEdit(self.frame)
        self.album_LineEdit.setObjectName(u"album_LineEdit")

        self.horizontalLayout_2.addWidget(self.album_LineEdit)

        self.slpdur_Label = CaptionLabel(self.frame)
        self.slpdur_Label.setObjectName(u"slpdur_Label")
        self.slpdur_Label.setFont(font2)

        self.horizontalLayout_2.addWidget(self.slpdur_Label)

        self.slpdur_LineEdit = LineEdit(self.frame)
        self.slpdur_LineEdit.setObjectName(u"slpdur_LineEdit")

        self.horizontalLayout_2.addWidget(self.slpdur_LineEdit)


        self.gridLayout_3.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.token_Label = CaptionLabel(self.frame)
        self.token_Label.setObjectName(u"token_Label")
        self.token_Label.setFont(font2)

        self.horizontalLayout_3.addWidget(self.token_Label)

        self.token_LineEdit = LineEdit(self.frame)
        self.token_LineEdit.setObjectName(u"token_LineEdit")

        self.horizontalLayout_3.addWidget(self.token_LineEdit)

        self.refresh_pushButton = ToolButton(self.frame)
        self.refresh_pushButton.setObjectName(u"refresh_pushButton")
        icon8 = QIcon(QIcon.fromTheme(u"sync-synchronizing"))
        self.refresh_pushButton.setIcon(icon8)

        self.horizontalLayout_3.addWidget(self.refresh_pushButton)


        self.gridLayout_3.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.lrctype_Label = CaptionLabel(self.frame)
        self.lrctype_Label.setObjectName(u"lrctype_Label")
        self.lrctype_Label.setFont(font2)

        self.horizontalLayout_4.addWidget(self.lrctype_Label)

        self.lrctype_comboBox = ComboBox(self.frame)
        self.lrctype_comboBox.addItem("")
        self.lrctype_comboBox.addItem("")
        self.lrctype_comboBox.setObjectName(u"lrctype_comboBox")

        self.horizontalLayout_4.addWidget(self.lrctype_comboBox)


        self.gridLayout_3.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame, 1, 0, 1, 1)

        self.pushButton = PushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout_2.addWidget(self.pushButton, 2, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 494, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen_Audio_File)
        self.menuFile.addAction(self.actionOpenDir)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionReadGenConfig)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionOpen_config_file)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionLicense)
        self.menuHelp.addAction(self.actionRelease_Page)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"RMxLRC - By ElliotCHEN37", None))
        self.actionOpen_Audio_File.setText(QCoreApplication.translate("MainWindow", u"Open audio file", None))
#if QT_CONFIG(shortcut)
        self.actionOpen_Audio_File.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionReadGenConfig.setText(QCoreApplication.translate("MainWindow", u"Read/Generate config file", None))
#if QT_CONFIG(shortcut)
        self.actionReadGenConfig.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+R", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+F4", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen_config_file.setText(QCoreApplication.translate("MainWindow", u"Open config file", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
#if QT_CONFIG(shortcut)
        self.actionAbout.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+A", None))
#endif // QT_CONFIG(shortcut)
        self.actionLicense.setText(QCoreApplication.translate("MainWindow", u"License", None))
#if QT_CONFIG(shortcut)
        self.actionLicense.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+L", None))
#endif // QT_CONFIG(shortcut)
        self.actionRelease_Page.setText(QCoreApplication.translate("MainWindow", u"Release Page", None))
#if QT_CONFIG(shortcut)
        self.actionRelease_Page.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+R", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpenDir.setText(QCoreApplication.translate("MainWindow", u"Open Directory", None))
#if QT_CONFIG(shortcut)
        self.actionOpenDir.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.reqpar_Label.setText(QCoreApplication.translate("MainWindow", u"Required parameters", None))
        self.artist_Label.setText(QCoreApplication.translate("MainWindow", u"Artist:", None))
#if QT_CONFIG(tooltip)
        self.artist_LineEdit.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Artist of the song</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.artist_LineEdit.setText("")
        self.title_Label.setText(QCoreApplication.translate("MainWindow", u"Title:", None))
#if QT_CONFIG(tooltip)
        self.title_LineEdit.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Name of the song</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.optpar_Label.setText(QCoreApplication.translate("MainWindow", u"Optional parameters", None))
        self.album_Label.setText(QCoreApplication.translate("MainWindow", u"Album:", None))
#if QT_CONFIG(tooltip)
        self.album_LineEdit.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Album of the song</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.slpdur_Label.setText(QCoreApplication.translate("MainWindow", u"Sleep:", None))
#if QT_CONFIG(tooltip)
        self.slpdur_LineEdit.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Sleep time in second during downloading multiple lyrics to avoid temporary ban from Musixmatch (Only effect Directory Mode)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.slpdur_LineEdit.setText(QCoreApplication.translate("MainWindow", u"30", None))
        self.token_Label.setText(QCoreApplication.translate("MainWindow", u"Token:", None))
#if QT_CONFIG(tooltip)
        self.token_LineEdit.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Your Musixmatch user token for Windows (If you don't have one, RMxLRC will generate a new one for you)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.refresh_pushButton.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Generate new user token</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.refresh_pushButton.setText("")
        self.lrctype_Label.setText(QCoreApplication.translate("MainWindow", u"Lyric Type:", None))
        self.lrctype_comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Synced", None))
        self.lrctype_comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Unsynced", None))

#if QT_CONFIG(tooltip)
        self.pushButton.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Download lyric from Musixmatch</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Download", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

