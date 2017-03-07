from PyQt4.QtGui import QFileDialog, QToolButton, QToolBar, QVBoxLayout, QWidget

from segyviewlib import ColormapCombo, LayoutCombo, SettingsWindow, SliceViewContext
from segyviewlib import SliceDataSource, SliceModel, SliceDirection as SD, SliceViewWidget, resource_icon


class SegyViewWidget(QWidget):
    def __init__(self, filename, show_toolbar=True, color_maps=None,
                                 width=11.7, height=8.3, dpi=100,
                                 segyioargs = {}, parent=None):
        QWidget.__init__(self, parent)

        inline = SliceModel("Inline", SD.inline, SD.crossline, SD.depth)
        xline = SliceModel("Crossline", SD.crossline, SD.inline, SD.depth)
        depth = SliceModel("Depth", SD.depth, SD.inline, SD.crossline)

        slice_models = [inline, xline, depth]
        slice_data_source = SliceDataSource(filename, **segyioargs)
        self._slice_data_source = slice_data_source

        self._context = SliceViewContext(slice_models, slice_data_source)
        self._context.show_indicators(True)

        self._slice_view_widget = SliceViewWidget(self._context, width, height, dpi, self)

        layout = QVBoxLayout()

        self._settings_window = SettingsWindow(self._context, self)

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

        save_button = QToolButton()
        save_button.setToolTip("Save as image")
        save_button.setIcon(resource_icon("table_export.png"))
        save_button.clicked.connect(self._save_figure)
        toolbar.addWidget(save_button)

        self._settings_button = QToolButton()
        self._settings_button.setToolTip("Toggle settings visibility")
        self._settings_button.setIcon(resource_icon("cog.png"))
        self._settings_button.setCheckable(True)
        self._settings_button.toggled.connect(self._show_settings)
        toolbar.addWidget(self._settings_button)

        def toggle_on_close(event):
            self._settings_button.setChecked(False)
            event.accept()

        self._settings_window.closeEvent = toggle_on_close

        self._colormap_combo.setCurrentIndex(45)
        layout_combo.setCurrentIndex(4)

        return toolbar

    def _colormap_changed(self, index):
        colormap = str(self._colormap_combo.itemText(index))
        self._context.set_colormap(colormap)

    def _interpolation_changed(self, index):
        interpolation_name = str(self._interpolation_combo.itemText(index))
        self._context.set_interpolation(interpolation_name)

    def _save_figure(self):
        formats = "Portable Network Graphic (*.png);;Adobe Acrobat (*.pdf);;Scalable Vector Graphics (*.svg)"
        output_file = QFileDialog.getSaveFileName(self, "Save as image", "untitled.png", formats)

        output_file = str(output_file).strip()

        if len(output_file) == 0:
            return

        image_size = self._context.image_size
        if not image_size:
            fig = self._slice_view_widget
        else:
            w, h, dpi = image_size
            fig = SliceViewWidget(self._context, width = w, height = h, dpi = dpi)
            fig.set_plot_layout(self._slice_view_widget.layout_figure().current_layout())

        fig.layout_figure().savefig(output_file)

    def set_source_filename(self, filename):
        self._slice_data_source.set_source_filename(filename)

    def _show_settings(self, toggled):
        self._settings_window.setVisible(toggled)
        if self._settings_window.isMinimized():
            self._settings_window.showNormal()

