from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal

from segyviewlib import SliceModel, SliceDataSource, SliceDirection


class ViewLimit(object):
    def __init__(self, model):
        self._min_xlim = 0
        self._max_xlim = model.width
        self._min_ylim = 0
        self._max_ylim = model.height

    @property
    def max_xlim(self):
        return self._max_xlim

    @max_xlim.setter
    def max_xlim(self, value):
        self._max_xlim = value + 1  # setting the constraint to the index above to the max

    @property
    def min_xlim(self):
        return self._min_xlim

    @min_xlim.setter
    def min_xlim(self, value):
        self._min_xlim = value

    @property
    def min_ylim(self):
        return self._min_ylim

    @min_ylim.setter
    def min_ylim(self, value):
        self._min_ylim = value

    @property
    def max_ylim(self):
        return self._max_ylim

    @max_ylim.setter
    def max_ylim(self, value):
        self._max_ylim = value + 1  # setting the constraint to the index above to the max


class SliceViewContext(QObject):
    context_changed = pyqtSignal()
    data_changed = pyqtSignal()
    data_source_changed = pyqtSignal()

    def __init__(self, slice_models=[], slice_data_source=None, colormap='seismic', interpolation='nearest',
                 image_size=None, has_data=True):
        QObject.__init__(self)

        self._available_slice_models = slice_models
        """ :type: list[SliceModel] """
        self._slice_data_source = slice_data_source
        """ :type: SliceDataSource """

        self._colormap_name = colormap
        self._show_indicators = False
        self._global_min = None
        self._global_max = None
        self._user_min_value = None
        self._user_max_value = None
        self._samples_unit = "Time (ms)"

        self._interpolation = interpolation
        self._symmetric_scale = True
        self._image_size = image_size

        self._view_limits = {}

        self._has_data = has_data

        if self._slice_data_source is not None:
            self._slice_data_source.slice_data_source_changed.connect(self._reset)

        if self._has_data:
            self._assign_indexes()

            for model in self._available_slice_models:
                self._view_limits[model.index_direction['name']] = ViewLimit(model)

    @property
    def models(self):
        """ :rtype: list[SliceModel]"""
        return self._available_slice_models

    @property
    def colormap(self):
        """ :rtype: str """
        return self._colormap_name

    @property
    def indicators(self):
        """ :rtype: bool """
        return self._show_indicators

    @property
    def interpolation(self):
        """ :rtype: str """
        return self._interpolation

    @property
    def global_minimum(self):
        """ :rtype: float """
        return self._global_min

    @property
    def global_maximum(self):
        """ :rtype: float """
        return self._global_max

    @property
    def symmetric_scale(self):
        """ :rtype: bool """
        return self._symmetric_scale

    @property
    def samples_unit(self):
        return self._samples_unit

    @samples_unit.setter
    def samples_unit(self, val):
        self._samples_unit = val
        self.context_changed.emit()

    @property
    def image_size(self):
        """ :rtype: None | Tuple(float, float, int) """
        return self._image_size

    @property
    def test_var(self):
        return self._has_data

    @test_var.setter
    def test_var(self, value):
        self._has_data = value

    def set_colormap(self, colormap):
        self._colormap_name = colormap
        self.context_changed.emit()

    def show_indicators(self, visible):
        self._show_indicators = visible
        self.context_changed.emit()

    def set_symmetric_scale(self, symmetric):
        self._symmetric_scale = symmetric
        self.context_changed.emit()

    def set_interpolation(self, interpolation_name):
        self._interpolation = str(interpolation_name)
        self.context_changed.emit()

    def set_x_view_limits(self, index_direction, min_x, max_x):

        slice_view_dir_ctxt = self._view_limits[index_direction['name']]

        if max_x is not None:
            slice_view_dir_ctxt.max_xlim = max_x

        if min_x is not None:
            slice_view_dir_ctxt.min_xlim = min_x

        self.context_changed.emit()

    def set_y_view_limits(self, index_direction, min_y, max_y):
        view_limit = self._view_limits[index_direction['name']]

        if max_y is not None:
            view_limit.max_ylim = max_y

        if min_y is not None:
            view_limit.min_ylim = min_y

        self.context_changed.emit()

    def set_user_values(self, min_value, max_value):
        dirty = False
        if self._user_min_value != min_value:
            self._user_min_value = min_value
            dirty = True

        if self._user_max_value != max_value:
            self._user_max_value = max_value
            dirty = True

        if dirty:
            self.context_changed.emit()

    def set_image_size(self, width, height=None, dpi=None):
        if width is None:
            self._image_size = None
            return

        if height is None or dpi is None:
            raise ValueError("Internal error: expects width, height, dpi")

        self._image_size = (width, height, dpi)

    def create_context(self, assigned_slice_models):
        view_min = None
        view_max = None

        for model in assigned_slice_models:
            view_min = model.min_value if view_min is None else min(model.min_value, view_min)
            view_max = model.max_value if view_max is None else max(model.max_value, view_max)
            self._global_min = view_min if self._global_min is None else min(self._global_min, view_min)
            self._global_max = view_max if self._global_max is None else max(self._global_max, view_max)

        vmin = self._global_min if self._user_min_value is None else self._user_min_value
        vmax = self._global_max if self._user_max_value is None else self._user_max_value
        if self._symmetric_scale and vmin <= 0.0 <= vmax:
            vmax = max(abs(vmin), vmax)
            vmin = -vmax

        if vmax < vmin:
            vmax = vmin

        return {
            "colormap": self.colormap,
            "show_indicators": self.indicators,
            "global_min": self._global_min,
            "global_max": self._global_max,
            "view_min": view_min,
            "view_max": view_max,
            "min": vmin,
            "max": vmax,
            "interpolation": self.interpolation,
            "view_limits": self._view_limits,
            "samples_unit": self.samples_unit,
        }

    def _assign_indexes(self):
        for m in self._available_slice_models:
            m.indexes = list(self._slice_data_source.indexes_for_direction(m.index_direction))
            m.x_indexes = list(self._slice_data_source.indexes_for_direction(m.x_index_direction))
            m.y_indexes = list(self._slice_data_source.indexes_for_direction(m.y_index_direction))
            data = self._slice_data_source.read_slice(m.index_direction, m.index)
            m.data = data

    def update_index_for_direction(self, index_direction, index):
        """
        :type index_direction: SliceDirection
        :type index: int
        """
        indexes = self._slice_data_source.indexes_for_direction(index_direction)

        if index < 0:
            index = 0
        elif index >= len(indexes):
            index = len(indexes) - 1

        for m in self._available_slice_models:
            if m.index_direction == index_direction:
                m.index = index

            if m.x_index_direction == index_direction:
                m.x_index = index

            if m.y_index_direction == index_direction:
                m.y_index = index

        self.load_data()

    def load_data(self):
        if self._has_data:
            for m in [sm for sm in self._available_slice_models if sm.dirty and sm.visible]:
                #print("loading data for %s" % m.title)
                m.data = self._slice_data_source.read_slice(m.index_direction, m.index)
        self.data_changed.emit()

    def _reset(self):
        self._global_max = None
        self._global_min = None

        for model in self._available_slice_models:
            model.reset()

        self._assign_indexes()
        self.data_source_changed.emit()

    def slice_data_source(self):
        """ :rtype: SliceDataSource"""
        return self._slice_data_source

    def model_for_direction(self, direction):
        for m in self._available_slice_models:
            if m.index_direction == direction:
                return m
        return None

    def index_for_direction(self, direction):
        for m in self._available_slice_models:
            if m.index_direction == direction:
                return m.index
        return -1
