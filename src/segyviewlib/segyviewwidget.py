from PyQt4.QtGui import QCheckBox, QWidget
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QToolButton, QToolBar, QVBoxLayout
from PyQt4.QtGui import QWidget

from segyviewlib import ColormapCombo
from segyviewlib import LayoutCombo
from segyviewlib import SliceDataSource, SliceModel, SliceDirection as SD, SliceViewWidget, resource_icon


class SegyViewWidget(QWidget):
    def __init__(self, filename, show_toolbar=True, color_maps=None, width=11.7, height=8.3, dpi=100, parent=None):
        QWidget.__init__(self, parent)

        inline = SliceModel("Inline", SD.inline, SD.crossline, SD.depth)
        xline = SliceModel("Crossline", SD.crossline, SD.inline, SD.depth)
        depth = SliceModel("Depth", SD.depth, SD.inline, SD.crossline)

        slice_models = [inline, xline, depth]
        slice_data_source = SliceDataSource(filename)
        self._slice_data_source = slice_data_source

        self._slice_view_widget = SliceViewWidget(slice_models, slice_data_source, 'seismic', width, height, dpi, self)

        layout = QVBoxLayout()

        self._toolbar = self._create_toolbar(color_maps)
        self._toolbar.setVisible(show_toolbar)

        layout.addWidget(self._toolbar)
        layout.addWidget(self._slice_view_widget)

        self.setLayout(layout)

    def toolbar(self):
        """ :rtype: QToolBar """
        return self._toolbar

    def _create_toolbar(self, color_maps):
        toolbar = QToolBar()
        toolbar.setFloatable(False)
        toolbar.setMovable(False)

        layout_combo = LayoutCombo()
        toolbar.addWidget(layout_combo)
        layout_combo.layout_changed.connect(self._slice_view_widget.set_plot_layout)

        # self._colormap_combo = ColormapCombo(['seismic', 'spectral', 'RdGy', 'hot', 'jet', 'gray'])
        self._colormap_combo = ColormapCombo(color_maps)
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

        return toolbar

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

    def set_source_filename(self, filename):
        self._slice_data_source.set_source_filename(filename)
        self._slice_view_widget.slice_data_source_changed()
