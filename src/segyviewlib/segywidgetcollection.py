from PyQt4.QtGui import QFileDialog, QToolButton, QToolBar, QVBoxLayout, QWidget, QTabWidget

from segyviewlib import ColormapCombo, LayoutCombo, SettingsWindow, SliceViewContext
from segyviewlib import SliceDataSource, SliceModel, SliceDirection as SD, SliceViewWidget, resource_icon
from itertools import chain

class SegyTabWidget(QWidget):
    def __init__(self, segywidgets, show_toolbar=True, color_maps=None,
                 width=11.7, height=8.3, dpi=100, parent=None):
        QWidget.__init__(self, parent)

        self._segywidgets = segywidgets
        """ :type: list[SegyViewWidget] """

        self._tab_widget = QTabWidget()
        layout = QVBoxLayout()

        for i, segywidget in enumerate(self._segywidgets):
            segywidget.show_toolbar(False)
            self._tab_widget.insertTab(i, segywidget, 'File: '+str(i+1))

        self._tab_widget.currentChanged.connect(self.update_views)

        slice_data_source = self.setup_datasource()

        inline = SliceModel("Inline", SD.inline, SD.crossline, SD.depth)
        xline = SliceModel("Crossline", SD.crossline, SD.inline, SD.depth)
        depth = SliceModel("Depth", SD.depth, SD.inline, SD.crossline)
        slice_models = [inline, xline, depth]

        self._context = SliceViewContext(slice_models, slice_data_source, has_data=False)
        self._context.data_changed.connect(self.data_changed)

        self._settings_window = SettingsWindow(self._context, self)
        self._toolbar = self._create_toolbar(color_maps)

        layout.addWidget(self._toolbar)
        layout.addWidget(self._tab_widget)

        self.setLayout(layout)

    def data_changed(self):
        dirty_models = [m for m in self._context.models if m.dirty]
        ctxs = [self._tab_widget.widget(index).context for index in range(0, self._tab_widget.count())]
        local_models = list(chain.from_iterable([ctx.models for ctx in ctxs]))

        for m in dirty_models:
            for local_m in local_models:
                if local_m.index_direction == m.index_direction:
                    local_m.index = m.index
                if local_m.x_index_direction == m.index_direction:
                    local_m.x_index = m.index
                if local_m.y_index_direction == m.index_direction:
                    local_m.y_index = m.index
                local_m.dirty = True
            m.dirty = False
        self.update_views()

    def update_views(self):
        self._tab_widget.currentWidget().context.load_data()

    def setup_datasource(self):
        slice_data_source = SliceDataSource(False)
        directions = [SD.inline, SD.crossline, SD.depth]
        for direction in directions:
            slice_data_source.set_indexes(direction,
                                          self._segywidgets[0].slice_data_source.indexes_for_direction(direction))
        return slice_data_source

    def _create_toolbar(self, color_maps):
        toolbar = QToolBar()
        toolbar.setFloatable(False)
        toolbar.setMovable(False)

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

        return toolbar

    def _show_settings(self, toggled):
        self._settings_window.setVisible(toggled)
        if self._settings_window.isMinimized():
            self._settings_window.showNormal()
