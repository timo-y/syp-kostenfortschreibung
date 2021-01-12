"""
#
#   CUSTOMQT
#   This module is for custom PyQt5 objects.
#
"""

from PyQt5 import QtCore, QtGui, QtWidgets

"""
#
#   TABBAR
#   To have the tab-title horizontal when on the west-side
#   src: https://stackoverflow.com/questions/51230544/pyqt5-how-to-set-tabwidget-west-but-keep-the-text-horizontal
#   usage:  QTabWidget.setTabBar(TabBar(self))
#           QTabWidget.setTabPosition(QtWidgets.QTabWidget.West)
"""
class TabBar(QtWidgets.QTabBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt);
            painter.restore()

class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QtWidgets.QTabWidget.West)

class PushButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation = QtCore.QVariantAnimation(
            startValue=QtGui.QColor("#4CAF50"),
            endValue=QtGui.QColor("white"),
            valueChanged=self._on_value_changed,
            duration=400,
        )
        self._update_stylesheet(QtGui.QColor("white"), QtGui.QColor("black"))
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def _on_value_changed(self, color):
        foreground = (
            QtGui.QColor("black")
            if self._animation.direction() == QtCore.QAbstractAnimation.Forward
            else QtGui.QColor("white")
        )
        self._update_stylesheet(color, foreground)

    def _update_stylesheet(self, background, foreground):

        self.setStyleSheet(
            """
        QPushButton{
            background-color: %s;
            border: none;
            color: %s;
            padding: 16px 32px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            margin: 4px 2px;
            border: 2px solid #4CAF50;
        }
        """
            % (background.name(), foreground.name())
        )

    def enterEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)
        self._animation.start()
        super().leaveEvent(event)

class DateTableWidgetItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, sorting_key,**kwargs):
        #call custom constructor with UserType item type
        super().__init__(*args, **kwargs)
        self.sorting_key = sorting_key
    #Qt uses a simple < check for sorting items, override this to use the sortKey
    def __lt__(self, other):
        return self.sorting_key < other.sorting_key

"""
#
#   COLLAPSABLE WIDGET
#   src: https://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
#
"""
class Spoiler(QtWidgets.QWidget):
    def __init__(self, parent=None, title='', animationDuration=300):
        """
        References:
            # Adapted from c++ version
            http://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
        """
        super(Spoiler, self).__init__(parent=parent)

        self.animationDuration = animationDuration
        self.toggleAnimation = QtCore.QParallelAnimationGroup()
        self.contentArea = QtGui.QScrollArea()
        self.headerLine = QtGui.QFrame()
        self.toggleButton = QtGui.QToolButton()
        self.mainLayout = QtGui.QGridLayout()

        toggleButton = self.toggleButton
        toggleButton.setStyleSheet("QToolButton { border: none; }")
        toggleButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        toggleButton.setArrowType(QtCore.Qt.RightArrow)
        toggleButton.setText(str(title))
        toggleButton.setCheckable(True)
        toggleButton.setChecked(False)

        headerLine = self.headerLine
        headerLine.setFrameShape(QtGui.QFrame.HLine)
        headerLine.setFrameShadow(QtGui.QFrame.Sunken)
        headerLine.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)

        self.contentArea.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        self.contentArea.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)
        # let the entire widget grow and shrink with its content
        toggleAnimation = self.toggleAnimation
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, b"minimumHeight"))
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self, b"maximumHeight"))
        toggleAnimation.addAnimation(QtCore.QPropertyAnimation(self.contentArea, b"maximumHeight"))
        # don't waste space
        mainLayout = self.mainLayout
        mainLayout.setVerticalSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        row = 0
        mainLayout.addWidget(self.toggleButton, row, 0, 1, 1, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(self.headerLine, row, 2, 1, 1)
        row += 1
        mainLayout.addWidget(self.contentArea, row, 0, 1, 3)
        self.setLayout(self.mainLayout)

        def start_animation(checked):
            arrow_type = QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow
            direction = QtCore.QAbstractAnimation.Forward if checked else QtCore.QAbstractAnimation.Backward
            toggleButton.setArrowType(arrow_type)
            self.toggleAnimation.setDirection(direction)
            self.toggleAnimation.start()

        self.toggleButton.clicked.connect(start_animation)

    def setContentLayout(self, contentLayout):
        # Not sure if this is equivalent to self.contentArea.destroy()
        self.contentArea.destroy()
        self.contentArea.setLayout(contentLayout)
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = contentLayout.sizeHint().height()
        for i in range(self.toggleAnimation.animationCount()-1):
            spoilerAnimation = self.toggleAnimation.animationAt(i)
            spoilerAnimation.setDuration(self.animationDuration)
            spoilerAnimation.setStartValue(collapsedHeight)
            spoilerAnimation.setEndValue(collapsedHeight + contentHeight)
        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)
