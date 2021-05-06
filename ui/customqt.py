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
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)
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
    def __init__(self, *args, sorting_key, **kwargs):
        # call custom constructor with UserType item type
        super().__init__(*args, **kwargs)
        self.sorting_key = sorting_key

    # Qt uses a simple < check for sorting items, override this to use the sortKey
    def __lt__(self, other):
        return self.sorting_key < other.sorting_key


class AmountTableWidgetItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, sorting_key, **kwargs):
        # call custom constructor with UserType item type
        super().__init__(*args, **kwargs)
        self.sorting_key = sorting_key

    # Qt uses a simple < check for sorting items, override this to use the sortKey
    def __lt__(self, other):
        return self.sorting_key < other.sorting_key


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTreeWidgetItem.__init__(self, *args, **kwargs)

    def __lt__(self, otherItem):
        """
        #
        #   COMPANRE WHEN SORTING THE COLUMN
        #       The columns containing money amounts (of the type "12.345,67 €") can't be sorted correctly.
        #       This "hacky" and unclean approach solves this for now.
        #
        #
        """
        column = self.treeWidget().sortColumn()
        text = self.text(column)
        amount_str = text.split(" ")[0].replace(".", "").replace(",", ".")
        if amount_str.replace(".", "").isnumeric() or amount_str == "-":
            amount = float(amount_str) if amount_str != "-" else 0
            other_amount_str = (
                otherItem.text(column).split(" ")[0].replace(".", "").replace(",", ".")
            )
            if other_amount_str.replace(".", "").isnumeric() or other_amount_str == "-":
                other_amount = float(other_amount_str) if other_amount_str != "-" else 0
                return amount < other_amount
        return text < otherItem.text(column)
