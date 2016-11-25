#!/usr/bin/env python
import sys

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QApplication, QToolButton, QFileDialog

from segyviewlib import resource_icon, SegyViewWidget


class SegyViewer(QMainWindow):
    def __init__(self, filename=None):
        QMainWindow.__init__(self)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("SEG-Y Viewer")

        self._segy_view_widget = SegyViewWidget(filename, show_toolbar=True)

        self.setCentralWidget(self._segy_view_widget)

        toolbar = self._segy_view_widget.toolbar()
        open_button = QToolButton()
        open_button.setToolTip("Open a SEG-Y file")
        open_button.setIcon(resource_icon("folder.png"))
        open_button.clicked.connect(self._open_file)

        first_action = toolbar.actions()[0]
        toolbar.insertWidget(first_action, open_button)
        toolbar.insertSeparator(first_action)

        self._segy_view_widget.show_advanced_features(True)

    def _open_file(self):
        input_file = QFileDialog.getOpenFileName(self, "Open SEG-Y file", "", "Segy File  (*.seg *.segy *.sgy)")
        input_file = str(input_file).strip()

        if input_file:
            self._segy_view_widget.set_source_filename(input_file)


def run(filename):
    segy_viewer = SegyViewer(filename)
    segy_viewer.show()
    segy_viewer.raise_()
    sys.exit(q_app.exec_())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("Usage: segyviewer.py [file]")

    filename = sys.argv[1]

    q_app = QApplication(sys.argv)

    # import cProfile
    # cProfile.run('run(%s)' % filename, filename=None, sort='cumulative')
    run(filename)
