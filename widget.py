# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widget.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *


class Ui_Widget(object):
    def setupUi(self, Widget):
        if Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(901, 647)
        self.horizontalLayoutWidget = QWidget(Widget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(19, 29, 861, 601))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.graphicsView = QGraphicsView(self.horizontalLayoutWidget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.horizontalLayout.addWidget(self.graphicsView)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.restButton = QPushButton(self.horizontalLayoutWidget)
        self.restButton.setObjectName(u"restButton")

        self.verticalLayout.addWidget(self.restButton)

        self.unknownButton = QPushButton(self.horizontalLayoutWidget)
        self.unknownButton.setObjectName(u"unknownButton")

        self.verticalLayout.addWidget(self.unknownButton)

        self.transaprentBagButton = QPushButton(self.horizontalLayoutWidget)
        self.transaprentBagButton.setObjectName(u"transaprentBagButton")

        self.verticalLayout.addWidget(self.transaprentBagButton)

        self.flatButton = QPushButton(self.horizontalLayoutWidget)
        self.flatButton.setObjectName(u"flatButton")

        self.verticalLayout.addWidget(self.flatButton)

        self.bundleButton = QPushButton(self.horizontalLayoutWidget)
        self.bundleButton.setObjectName(u"bundleButton")

        self.verticalLayout.addWidget(self.bundleButton)

        self.bagButton = QPushButton(self.horizontalLayoutWidget)
        self.bagButton.setObjectName(u"bagButton")

        self.verticalLayout.addWidget(self.bagButton)

        self.boxButton = QPushButton(self.horizontalLayoutWidget)
        self.boxButton.setObjectName(u"boxButton")

        self.verticalLayout.addWidget(self.boxButton)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.restButton.setText(QCoreApplication.translate("Widget", u"Rest", None))
        self.unknownButton.setText(QCoreApplication.translate("Widget", u"Unkown", None))
        self.transaprentBagButton.setText(QCoreApplication.translate("Widget", u"transparent bag", None))
        self.flatButton.setText(QCoreApplication.translate("Widget", u"Flat", None))
        self.bundleButton.setText(QCoreApplication.translate("Widget", u"Bundle", None))
        self.bagButton.setText(QCoreApplication.translate("Widget", u"Bag", None))
        self.boxButton.setText(QCoreApplication.translate("Widget", u"Box", None))
    # retranslateUi

