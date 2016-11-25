#!/usr/bin/env python
import sys

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QApplication, QCheckBox, QToolButton, QFileDialog, QToolBar

import segyio

from segyviewlib import SliceViewWidget, ColormapCombo, SliceModel, SliceDirection as SD, SliceDataSource, LayoutCombo, \
    resource_icon


class SegyViewer(QMainWindow):
    def __init__(self, filename=None):
        QMainWindow.__init__(self)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("SEG-Y Viewer")

        inline = SliceModel("Inline", SD.inline, SD.crossline, SD.depth)
        xline = SliceModel("Crossline", SD.crossline, SD.inline, SD.depth)
        depth = SliceModel("Depth", SD.depth, SD.inline, SD.crossline)

        slice_models = [inline, xline, depth]
        self._slice_data_source = SliceDataSource(filename)
        self._slice_view_widget = SliceViewWidget(slice_models, self._slice_data_source)

        toolbar = self.addToolBar("Stuff")
        """:type: QToolBar"""
        toolbar.setFloatable(False)
        toolbar.setMovable(False)

        open_button = QToolButton()
        open_button.setToolTip("Open a SEG-Y file")
        open_button.setIcon(resource_icon("folder.png"))
        open_button.clicked.connect(self._open_file)
        toolbar.addWidget(open_button)

        toolbar.addSeparator()

        layout_combo = LayoutCombo()
        toolbar.addWidget(layout_combo)
        layout_combo.layout_changed.connect(self._slice_view_widget.set_plot_layout)

        # self._colormap_combo = ColormapCombo(['seismic', 'spectral', 'RdGy', 'hot', 'jet', 'gray'])
        self._colormap_combo = ColormapCombo()
        self._colormap_combo.currentIndexChanged[int].connect(self._colormap_changed)
        toolbar.addWidget(self._colormap_combo)

        indicator_visibility = QCheckBox("Indicators")
        indicator_visibility.toggled.connect(self._slice_view_widget.show_indicators)
        toolbar.addWidget(indicator_visibility)

        save_button = QToolButton()
        save_button.setToolTip("Save as image")
        save_button.setIcon(resource_icon("table_export.png"))
        save_button.clicked.connect(self._save_figure)
        toolbar.addWidget(save_button)

        indicator_visibility.setChecked(True)
        self._colormap_combo.setCurrentIndex(45)
        layout_combo.setCurrentIndex(2)

        self.setCentralWidget(self._slice_view_widget)

    def _colormap_changed(self, index):
        colormap = str(self._colormap_combo.itemText(index))
        self._slice_view_widget.set_colormap(colormap)

    def _save_figure(self):
        formats = "Portable Network Graphic (*.png);;Adobe Acrobat (*.pdf);;Scalable Vector Graphics (*.svg)"
        output_file = QFileDialog.getSaveFileName(self, "Save as image", "untitled.png", formats)

        output_file = str(output_file).strip()

        if len(output_file) > 0:
            layout_figure = self._slice_view_widget.layout_figure()
            layout_figure.savefig(output_file)

    def _open_file(self):
        input_file = QFileDialog.getOpenFileName(self, "Open SEG-Y file", "", "Segy File  (*.seg *.segy *.sgy)")
        input_file = str(input_file).strip()

        if input_file:
            self._slice_data_source.set_source_filename(input_file)
            self._slice_view_widget.slice_data_source_changed()


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
