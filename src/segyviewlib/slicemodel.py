import numpy as np


class SliceDirection(object):
    inline = {'name': "Inlines"}
    crossline = {'name': "Crosslines"}
    depth = {'name': "Depth"}


class SliceModel(object):
    def __init__(self, title, index_direction, x_index_direction, y_index_direction):
        super(SliceModel, self).__init__()
        self._index_direction = index_direction
        self._x_index_direction = x_index_direction
        self._y_index_direction = y_index_direction
        self._title = title
        self._indexes = None
        self._x_indexes = None
        self._y_indexes = None

        self._data = None
        self._data_x_indexes = None
        self._data_y_indexes = None

        self._index = 0
        self._x_index = 0
        self._y_index = 0

        self._min_value = None
        self._max_value = None

        self._visible = True
        self._dirty = False

    @property
    def title(self):
        """ :rtype: str """
        return self._title

    @property
    def indexes(self):
        """ :rtype: list[int] """
        return self._indexes

    @indexes.setter
    def indexes(self, indexes):
        """ :type indexes: list[int] """
        self._indexes = indexes
        self._index = len(indexes) // 2

    @property
    def x_indexes(self):
        """ @rtype: list[int] """
        return self._x_indexes or self._data_x_indexes

    @x_indexes.setter
    def x_indexes(self, indexes):
        """ :type indexes: list[int] """
        self._assert_shape(self._data, indexes, self._y_indexes)
        self._x_indexes = indexes
        self.x_index = len(indexes) / 2

    @property
    def y_indexes(self):
        """ @rtype: list[int] """
        return self._y_indexes or self._data_y_indexes

    @y_indexes.setter
    def y_indexes(self, indexes):
        """ :type indexes: list[int] """
        self._assert_shape(self._data, self._x_indexes, indexes)
        self._y_indexes = indexes
        self.y_index = len(indexes) / 2

    @staticmethod
    def _assert_shape(data, x_indexes, y_indexes):
        if data is not None:
            if x_indexes and len(x_indexes) != data.shape[1]:
                raise ValueError("X axis element count does not match data shape")

            if y_indexes and len(y_indexes) != data.shape[0]:
                raise ValueError("Y axis element count does not match data shape")

    @property
    def x_axis_name(self):
        """ @rtype: str """
        return self._x_index_direction['name']

    @property
    def y_axis_name(self):
        """ @rtype: str """
        return self._y_index_direction['name']

    @property
    def data(self):
        """ :rtype: numpy.ndarray """
        return self._data

    @data.setter
    def data(self, data):
        """ :type: numppy.ndarray """
        self._assert_shape(data, self._x_indexes, self._y_indexes)
        data[data == -np.inf] = 0.0
        data[data == np.inf] = 0.0
        self._data = data
        self._min_value = np.nanmin(self.data)
        self._max_value = np.nanmax(self.data)
        self._data_x_indexes = list(range(data.shape[0]))
        self._data_y_indexes = list(range(data.shape[1]))
        self._dirty = False

    @property
    def index(self):
        """ :rtype: int """
        return self._index

    @index.setter
    def index(self, index):
        """ :type index: int """
        if self._index != index:
            self._dirty = True
        self._index = index

    @property
    def min_x(self):
        """ :rtype: int """
        return min(self.x_indexes)

    @property
    def max_x(self):
        """ :rtype: int """
        return max(self.x_indexes)

    @property
    def min_y(self):
        """ :rtype: int """
        return min(self.y_indexes)

    @property
    def max_y(self):
        """ :rtype: int """
        return max(self.y_indexes)

    @property
    def min_value(self):
        """ :rtype: int """
        return self._min_value

    @property
    def max_value(self):
        """ :rtype: int """
        return self._max_value

    def x_axis_formatter(self, value, position):
        if 0 <= value < self.width:
            return self.x_indexes[int(value)]
        return ''

    def y_axis_formatter(self, value, position):
        if 0 <= value < self.height:
            return self.y_indexes[int(value)]
        return ''

    @property
    def x_index(self):
        """ :rtype: int """
        return self._x_index

    @x_index.setter
    def x_index(self, index):
        """ :type index: int """
        self._x_index = index

    @property
    def y_index(self):
        """ :rtype: int """
        return self._y_index

    @y_index.setter
    def y_index(self, index):
        """ :type index: int """
        self._y_index = index

    @property
    def width(self):
        """ :rtype: int """
        return len(self.x_indexes)

    @property
    def height(self):
        """ :rtype: int """
        return len(self.y_indexes)

    @property
    def visible(self):
        """ :rtype: bool """
        return self._visible

    @visible.setter
    def visible(self, visible):
        """ :type visible: bool """
        self._visible = visible

    @property
    def index_direction(self):
        """ :rtype: dict """
        return self._index_direction

    @property
    def x_index_direction(self):
        """ :rtype: dict """
        return self._x_index_direction

    @property
    def y_index_direction(self):
        """ :rtype: dict """
        return self._y_index_direction

    @property
    def dirty(self):
        """ :type: bool """
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        self._dirty = value

    def __len__(self):
        return len(self.indexes)

    def reset(self):
        self._indexes = None
        self._x_indexes = None
        self._y_indexes = None

        self._data = None
        self._data_x_indexes = None
        self._data_y_indexes = None

        self._index = 0
        self._x_index = 0
        self._y_index = 0

        self._min_value = None
        self._max_value = None
