from __future__ import division
import sys
from PyQt4.QtGui import QCheckBox, QWidget, QFormLayout, QComboBox, QLabel, QSpinBox, QValidator
from PyQt4.QtGui import QPushButton, QDoubleSpinBox, QHBoxLayout, QVBoxLayout
from PyQt4.QtCore import Qt

from segyviewlib import SliceDirection


class ArraySpinBox(QSpinBox):
    def __init__(self, values, parent=None):
        QSpinBox.__init__(self, parent)
        self._values = []
        """ :type: list[int]"""
        self.set_index_values(values)
        self.setMinimum(0)

    def update_view(self, indexes, index):
        self.blockSignals(True)
        self.set_index_values(indexes)
        self.setValue(index)
        self.blockSignals(False)

    def set_index_values(self, values):
        self._values = values
        if self.maximum() != len(values) - 1:
            self.setMaximum(len(values) - 1)

    def setValue(self, value):
        if value != self.value():
            QSpinBox.setValue(self, value)

    def valueFromText(self, text):
        text = str(text)
        if text.strip() == "":
            index = 0
        else:
            value = int(text)
            index = self._values.index(value)
        return index

    def textFromValue(self, index):
        return str(self._values[index])

    def validate(self, text, pos):
        text = str(text)
        if text.strip() == "":
            return QValidator.Acceptable, pos

        try:
            value = int(text)
        except ValueError:
            return QValidator.Invalid, pos

        try:
            index = self._values.index(value)
        except ValueError:
            for value in self._values:
                if str(value).startswith(text):
                    return QValidator.Intermediate, pos

            return QValidator.Invalid, pos

        return QValidator.Acceptable, pos


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

        layout = QFormLayout()

        self._iline_count = QLabel("")
        self._xline_count = QLabel("")
        self._offset_count = QLabel("")
        self._sample_count = QLabel("")
        self._minimum_value = QLabel("")
        self._maximum_value = QLabel("")

        layout.addRow("Inline Count:", self._iline_count)
        layout.addRow("Crossline Count:", self._xline_count)
        layout.addRow("Offset Count:", self._offset_count)
        layout.addRow("Sample Count:", self._sample_count)
        layout.addRow("Minimum Value:", self._minimum_value)
        layout.addRow("Maximum Value:", self._maximum_value)

        self.add_empty_row(layout)

        self._iline = ArraySpinBox([0])
        self._iline.valueChanged[int].connect(self._index_changed_fn(SliceDirection.inline))
        layout.addRow("Inline:", self._iline)

        self._xline = ArraySpinBox([0])
        self._xline.valueChanged[int].connect(self._index_changed_fn(SliceDirection.crossline))
        layout.addRow("Crossline:", self._xline)

        # self._offset = ArraySpinBox([1])
        # layout.addRow("Offset", self._offset)

        self._sample = ArraySpinBox([0])
        self._sample.valueChanged[int].connect(self._index_changed_fn(SliceDirection.depth))
        layout.addRow("Depth", self._sample)

        self.add_empty_row(layout)

        self._user_minimum_active, self._user_minimum_value, min_val_layout = self._create_user_value()
        self._user_minimum_active.toggled.connect(self._user_value_changed)
        self._user_minimum_value.valueChanged.connect(self._user_value_changed)
        layout.addRow("Custom Minimum:", min_val_layout)

        self._user_maximum_active, self._user_maximum_value, max_val_layout = self._create_user_value()
        self._user_maximum_active.toggled.connect(self._user_value_changed)
        self._user_maximum_value.valueChanged.connect(self._user_value_changed)
        layout.addRow("Custom Maximum:", max_val_layout)

        self._user_minimum_value.setMaximum(self._user_maximum_value.value())
        self._user_maximum_value.setMinimum(self._user_minimum_value.value())

        self._symmetric_scale = QCheckBox()
        self._symmetric_scale.toggled.connect(self._context.set_symmetric_scale)
        layout.addRow("Symmetric scale:", self._symmetric_scale)

        self.add_empty_row(layout)

        self._indicator_visibility = QCheckBox()
        self._indicator_visibility.toggled.connect(self._context.show_indicators)
        layout.addRow("Show Indicators:", self._indicator_visibility)

        self._interpolation_combo = QComboBox()
        self._interpolations_names = ['nearest', 'catrom', 'sinc']
        self._interpolation_combo.addItems(self._interpolations_names)
        self._interpolation_combo.currentIndexChanged.connect(self._interpolation_changed)
        layout.addRow("Interpolation Type:", self._interpolation_combo)

        self.add_empty_row(layout)

        self._dpi_units  = ["in", "cm", "px"]
        self._fix_size   = QCheckBox()
        self._fix_width  = QDoubleSpinBox()
        self._fix_height = QDoubleSpinBox()
        self._fix_dpi_units    = QComboBox()

        if parent is None:
            w, h, dpi = 11.7, 8.3, 100
        else:
            fig = parent._slice_view_widget.layout_figure()
            w, h = fig.get_size_inches()
            dpi = fig.dpi

        self._fix_width.setMinimum(1)
        self._fix_width.setMaximum(32000)
        self._fix_width.setValue(w)

        self._fix_height.setMinimum(1)
        self._fix_height.setMaximum(32000)
        self._fix_height.setValue(h)

        self._fix_width.valueChanged.connect(self._fixed_image)
        self._fix_height.valueChanged.connect(self._fixed_image)

        self._fix_dpi_units.addItems(self._dpi_units)
        self._fix_dpi_units.activated.connect(self._fixed_image)
        self._fix_size.toggled.connect(self._fixed_image)

        wxh_layout = QHBoxLayout()
        wxh_layout.addWidget(self._fix_width)
        wxh_layout.addWidget(self._fix_height)

        layout.addRow("Fix export size:", self._fix_size)
        layout.addRow("Width x Height:", wxh_layout)
        layout.addRow("Unit:", self._fix_dpi_units)

        vertical_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        vertical_layout.addLayout(layout)
        vertical_layout.addLayout(button_layout)

        self.setLayout(vertical_layout)

    @staticmethod
    def to_inches(width, height, dpi, scale):
        if scale == "in":
            return (width, height, dpi)
        elif scale == "cm":
            return (width / 2.54, height / 2.54, dpi)
        elif scale == "px":
            return (int(width) / dpi, int(height) / dpi, dpi)
        else:
            raise NotImplementedError

    def _fixed_image(self):
        ctx = self._context
        if not self._fix_size.isChecked():
            ctx.set_image_size(None)
            return

        w = self._fix_width.value()
        h = self._fix_height.value()
        dpi = 100
        scale = self._fix_dpi_units.currentText()

        ctx.set_image_size(*self.to_inches(w, h, dpi, scale))

    def _create_user_value(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        check_box = QCheckBox()
        spin_box = QDoubleSpinBox()
        spin_box.setDecimals(5)
        spin_box.setSingleStep(0.01)
        spin_box.setMinimum(-sys.float_info.max)
        spin_box.setMaximum(sys.float_info.max)
        spin_box.setDisabled(True)
        check_box.toggled.connect(spin_box.setEnabled)

        layout.addWidget(check_box)
        layout.addWidget(spin_box)

        return check_box, spin_box, layout

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

        self._minimum_value.setText("%f" % ctx.global_minimum)
        self._maximum_value.setText("%f" % ctx.global_maximum)

        indexes = ctx.slice_data_source().indexes_for_direction(SliceDirection.inline).tolist()
        index = ctx.index_for_direction(SliceDirection.inline)
        self._iline.update_view(indexes, index)

        indexes = ctx.slice_data_source().indexes_for_direction(SliceDirection.crossline).tolist()
        index = ctx.index_for_direction(SliceDirection.crossline)
        self._xline.update_view(indexes, index)

        indexes = ctx.slice_data_source().indexes_for_direction(SliceDirection.depth).tolist()
        index = ctx.index_for_direction(SliceDirection.depth)
        self._sample.update_view(indexes, index)

    def _interpolation_changed(self, index):
        interpolation_name = str(self._interpolation_combo.itemText(index))
        self._context.set_interpolation(interpolation_name)

    def _index_changed_fn(self, direction):
        def fn(value):
            self._context.update_index_for_direction(direction, value)
        return fn

    def _user_value_changed(self):
        min_value = None
        max_value = None
        if self._user_minimum_active.isChecked():
            min_value = self._user_minimum_value.value()
            self._user_maximum_value.setMinimum(min_value)
        else:
            self._user_maximum_value.setMinimum(-sys.float_info.max)

        if self._user_maximum_active.isChecked():
            max_value = self._user_maximum_value.value()
            self._user_minimum_value.setMaximum(max_value)
        else:
            self._user_minimum_value.setMaximum(sys.float_info.max)

        self._context.set_user_values(min_value, max_value)

