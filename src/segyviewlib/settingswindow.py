from __future__ import division
from PyQt4.QtGui import QCheckBox, QWidget, QFormLayout, QComboBox, QLabel
from PyQt4.QtGui import QPushButton, QHBoxLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt4.QtCore import Qt, QObject

from segyviewlib import SliceDirection, SampleScaleController, IndexController, PlotExportSettingsWidget


class SettingsWindow(QWidget):
    def __init__(self, context, parent=None):
        """
        :type context: segyviewlib.SliceViewContext
        :type parent: QObject
        """
        QWidget.__init__(self, parent, Qt.WindowStaysOnTopHint | Qt.Window)
        self.setVisible(False)

        self._context = context
        self._context.context_changed.connect(self._settings_changed)
        self._context.data_changed.connect(self._settings_changed)
        self._context.data_source_changed.connect(self._settings_changed)

        f_layout = QFormLayout()

        self._iline_count = QLabel("")
        self._xline_count = QLabel("")
        self._offset_count = QLabel("")
        self._sample_count = QLabel("")
        self._minimum_value = QLabel("")
        self._maximum_value = QLabel("")

        f_layout.addRow("Inline Count:", self._iline_count)
        f_layout.addRow("Crossline Count:", self._xline_count)
        f_layout.addRow("Offset Count:", self._offset_count)
        f_layout.addRow("Sample Count:", self._sample_count)
        f_layout.addRow("Minimum Value:", self._minimum_value)
        f_layout.addRow("Maximum Value:", self._maximum_value)

        # iline
        self._il_ctrl = IndexController(parent=self,
                                        context=self._context,
                                        slice_direction_index_source=SliceDirection.inline)
        self._il_ctrl.index_changed.connect(self._index_changed_fn(SliceDirection.inline))
        self._il_ctrl.min_max_changed.connect(self.iline_limits_changed)

        # xline
        self._xl_ctrl = IndexController(parent=self,
                                        context=self._context,
                                        slice_direction_index_source=SliceDirection.crossline)
        self._xl_ctrl.index_changed.connect(self._index_changed_fn(SliceDirection.crossline))
        self._xl_ctrl.min_max_changed.connect(self.xline_limits_changed)

        # depth
        self._depth_ctrl = IndexController(parent=self,
                                           context=self._context,
                                           slice_direction_index_source=SliceDirection.depth)
        self._depth_ctrl.index_changed.connect(self._index_changed_fn(SliceDirection.depth))
        self._depth_ctrl.min_max_changed.connect(self.depth_limits_changed)

        # sample
        self._sample_ctrl = SampleScaleController(self)
        self._sample_ctrl.min_max_changed.connect(self.sample_limits_changed)

        self._symmetric_scale = QCheckBox()
        self._symmetric_scale.toggled.connect(self._context.set_symmetric_scale)

        self._samples_unit = QComboBox()
        self._samples_unit.addItems(['Time (ms)', 'Depth (m)'])
        self._samples_unit.currentIndexChanged[str].connect(self.samples_unit)

        # view
        self._view_label = QLabel("")
        self._view_label.setDisabled(True)
        self._indicator_visibility = QCheckBox()
        self._indicator_visibility.toggled.connect(self._context.show_indicators)
        self._indicator_visibility.toggled.connect(lambda: self._set_view_label(self._indicator_visibility.isChecked()))

        self._interpolation_combo = QComboBox()
        self._interpolations_names = ['nearest', 'catrom', 'sinc']
        self._interpolation_combo.addItems(self._interpolations_names)
        self._interpolation_combo.currentIndexChanged.connect(self._interpolation_changed)

        # plot export settings
        if self._context._has_data:
            self._plt_settings_wdgt = PlotExportSettingsWidget(self, parent._slice_view_widget, self._context)

        # define tree layout
        tree_def = {"": [
            {"Inline": [{"set_expanded": True},
                        {"": self._align(self._il_ctrl.current_index_label)},
                        {"Inline:": self._align(self._il_ctrl.index_widget)},
                        {"Minimum:": self._align(self._il_ctrl.min_spinbox, self._il_ctrl.min_checkbox)},
                        {"Maximum:": self._align(self._il_ctrl.max_spinbox, self._il_ctrl.max_checkbox)}
                        ]
             },
            {"Crossline": [{"set_expanded": True},
                           {"": self._align(self._xl_ctrl.current_index_label)},
                           {"Crossline:": self._align(self._xl_ctrl.index_widget)},
                           {"Minimum:": self._align(self._xl_ctrl.min_spinbox, self._xl_ctrl.min_checkbox)},
                           {"Maximum:": self._align(self._xl_ctrl.max_spinbox, self._xl_ctrl.max_checkbox)}
                           ]
             },
            {"Depth": [{"set_expanded": True},
                       {"": self._align(self._depth_ctrl.current_index_label)},
                       {"Depth:": self._align(self._depth_ctrl.index_widget)},
                       {"Minimum:": self._align(self._depth_ctrl.min_spinbox, self._depth_ctrl.min_checkbox)},
                       {"Maximum:": self._align(self._depth_ctrl.max_spinbox, self._depth_ctrl.max_checkbox)},
                       {"Type": self._align(self._samples_unit)}
                       ]
             },
            {"Color Scale": [
                {"Custom min.:": self._align(self._sample_ctrl.min_spinbox, self._sample_ctrl.min_checkbox)},
                {"Custom max.:": self._align(self._sample_ctrl.max_spinbox, self._sample_ctrl.max_checkbox)},
                {"Symmetric scale:": self._align(self._symmetric_scale)}
            ]
            },
            {"View": [{"": self._align(self._view_label)},
                      {"Show Indicators:": self._align(self._indicator_visibility)},
                      {"Interpolation Type:": self._align(self._interpolation_combo)}
                      ]
             },
        ]}

        if self._context._has_data:
            tree_def[''].append({"Plot export dimensions": [
                {"": self._align(self._plt_settings_wdgt.label)},
                {"Fixed size": self._align(self._plt_settings_wdgt.checkbox)},
                {"Width:": self._align(self._plt_settings_wdgt.width_spinbox)},
                {"Height:": self._align(self._plt_settings_wdgt.height_spinbox)},
                {"Units:": self._align(self._plt_settings_wdgt.units_combobox)}
            ]
            })

        # setup the menu/navigation tree widget
        tre = QTreeWidget(self)
        tre.setHeaderHidden(True)
        tre.setColumnCount(2)
        tre.setColumnWidth(0, 140)
        tre.setColumnWidth(1, 180)

        self._build_tree(tre, tree_def, tre.invisibleRootItem())

        # layout
        vertical_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        vertical_layout.addLayout(f_layout, 0)
        vertical_layout.addStretch()
        vertical_layout.addWidget(tre, 1)
        vertical_layout.addStretch()
        vertical_layout.addLayout(button_layout, 0)

        self.setLayout(vertical_layout)
        self.setMinimumSize(390, 740)

    @staticmethod
    def _align(widget, checkbox=None):

        l = QHBoxLayout()

        if checkbox is not None:
            checkbox.setMaximumWidth(23)
            l.addWidget(checkbox, 0)
        else:
            l.addSpacing(25)

        l.addStretch(0.5)
        if widget is not None:
            widget.setMinimumWidth(180)
            widget.setMaximumWidth(180)
            l.addWidget(widget)
        else:
            l.addSpacing(180)

        l.setContentsMargins(0, 0, 0, 0)
        l.addStretch(1)

        w = QWidget()
        w.setContentsMargins(0, 2, 0, 2)
        w.setLayout(l)
        return w

    def samples_unit(self, val):
        self._context.samples_unit = val

    def _create_user_value(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

    def _build_tree(self, tree_wdgt, tree_def, root):
        parent, children = tree_def.items()[0]

        # empty label /parent is a special case: either inline with the previous, or skip
        if parent == "":
            if isinstance(children, QWidget):
                item = root
                tree_wdgt.setItemWidget(item, 1, children)

            elif isinstance(children, list):
                for c in children:
                    self._build_tree(tree_wdgt, c, root)

        elif parent == "set_expanded":  # a configuration item for the current root
            root.setExpanded(children)
        else:
            item = QTreeWidgetItem(root)
            item.setText(0, parent)

            if isinstance(children, list):
                for c in children:
                    self._build_tree(tree_wdgt, c, item)
            else:
                tree_wdgt.setItemWidget(item, 1, children)

    def add_empty_row(self, layout, legend=""):
        layout.addRow(legend, QLabel())

    def _settings_changed(self):
        ctx = self._context
        self._indicator_visibility.setChecked(ctx.indicators)

        index = self._interpolations_names.index(ctx.interpolation)
        self._interpolation_combo.setCurrentIndex(index)

        self._symmetric_scale.setChecked(ctx.symmetric_scale)

        ilines, xlines, offsets, samples = ctx.slice_data_source().dims()
        self._iline_count.setText("%d" % ilines)
        self._xline_count.setText("%d" % xlines)
        self._offset_count.setText("%d" % offsets)
        self._sample_count.setText("%d" % samples)

        if ctx._has_data:
            self._minimum_value.setText("%f" % ctx.global_minimum)
            self._maximum_value.setText("%f" % ctx.global_maximum)

            indexes = ctx.slice_data_source().indexes_for_direction(SliceDirection.inline).tolist()
            index = ctx.index_for_direction(SliceDirection.inline)
            self._il_ctrl.update_view(indexes, index)

            indexes = ctx.slice_data_source().indexes_for_direction(SliceDirection.crossline).tolist()
            index = ctx.index_for_direction(SliceDirection.crossline)
            self._xl_ctrl.update_view(indexes, index)

            indexes = ctx.slice_data_source().indexes_for_direction(SliceDirection.depth).tolist()
            index = ctx.index_for_direction(SliceDirection.depth)
            self._depth_ctrl.update_view(indexes, index)

            index = self._samples_unit.findText(ctx.samples_unit)
            if index != -1:
                self._samples_unit.setCurrentIndex(index)

    def _set_view_label(self, indicator_on):
        self._view_label.setText("indicators {0}".format("on" if indicator_on else "off"))

    def _interpolation_changed(self, index):
        interpolation_name = str(self._interpolation_combo.itemText(index))
        self._context.set_interpolation(interpolation_name)

    def _index_changed_fn(self, direction):
        def fn(value):
            self._context.update_index_for_direction(direction, value)

        return fn

    def sample_limits_changed(self, values):
        self._context.set_user_values(*values)

    def depth_limits_changed(self, values):
        min, max = values
        self._context.set_y_view_limits(SliceDirection.crossline, min, max)
        self._context.set_y_view_limits(SliceDirection.inline, min, max)

    def iline_limits_changed(self, values):
        min, max = values
        self._context.set_x_view_limits(SliceDirection.crossline, min, max)
        self._context.set_x_view_limits(SliceDirection.depth, min, max)

    def xline_limits_changed(self, values):
        min, max = values
        self._context.set_x_view_limits(SliceDirection.inline, min, max)
        self._context.set_y_view_limits(SliceDirection.depth, min, max)
