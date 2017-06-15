#!/usr/bin/env python
import sys
import argparse

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QApplication, QToolButton, QFileDialog, QIcon

from segyviewlib import resource_icon, SegyViewWidget


class SegyViewer(QMainWindow):
    def __init__(self, filename=None, il = None, xl = None):
        QMainWindow.__init__(self)

        self.segyioargs = { k: v for k, v in [('iline', il), ('xline', xl)]
                                          if v is not None }

        self.setAttribute(Qt.WA_DeleteOnClose)

        title = filename if filename is not None else "SEG-Y Viewer"
        self.setWindowTitle(title)

        self._segy_view_widget = SegyViewWidget(filename, show_toolbar=True,
                                                          segyioargs = self.segyioargs,
                                                          parent = self)

        self.setCentralWidget(self._segy_view_widget)
        self.setWindowIcon(resource_icon("350px-SEGYIO.png"))

        toolbar = self._segy_view_widget.toolbar()
        open_button = QToolButton()
        open_button.setToolTip("Open a SEG-Y file")
        open_button.setIcon(resource_icon("folder.png"))
        open_button.clicked.connect(self._open_file)

        first_action = toolbar.actions()[0]
        toolbar.insertWidget(first_action, open_button)
        toolbar.insertSeparator(first_action)

    def _open_file(self):
        input_file = QFileDialog.getOpenFileName(self, "Open SEG-Y file", "", "Segy File  (*.seg *.segy *.sgy)")
        input_file = str(input_file).strip()

        if input_file:
            self._segy_view_widget.set_source_filename(input_file, **self.segyioargs)
            self._segy_view_widget.set_default_layout()
            self.setWindowTitle(input_file)


def run(filename, il, xl):
    segy_viewer = SegyViewer(filename, il, xl)
    segy_viewer.show()
    segy_viewer.raise_()
    sys.exit(q_app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Simple SEG-Y visualization')
    parser.add_argument('filename',   type = str, help = 'File to open')
    parser.add_argument('-i', '--il', type = int,
                                      help = 'inline identifer')
    parser.add_argument('-x', '--xl', type = int,
                                      help = 'crossline identifer')

    args = parser.parse_args()

    q_app = QApplication(sys.argv)

    # import cProfile
    # cProfile.run('run(%s)' % filename, filename=None, sort='cumulative')
    run(args.filename, args.il, args.xl)
