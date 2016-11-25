from segyviewlib import SliceModel, SliceDirection, SliceDataSource


class SliceModelController(object):
    def __init__(self, models, slice_data_source):
        super(SliceModelController, self).__init__()

        self._models = models
        """ :type: list[SliceModel] """
        self._slice_data_source = slice_data_source
        """ :type: SliceDataSource """

        self._assign_indexes()

    def _assign_indexes(self):
        for m in self._models:
            m.indexes = list(self._slice_data_source.indexes_for_direction(m.index_direction))
            m.x_indexes = list(self._slice_data_source.indexes_for_direction(m.x_index_direction))
            m.y_indexes = list(self._slice_data_source.indexes_for_direction(m.y_index_direction))
            data = self._slice_data_source.read_slice(m.index_direction, m.index)
            m.data = data

    def model_index_changed(self, model, index):
        """
        :type model: SliceModel
        :type index: int
        """
        if index < 0:
            index = 0
        elif index >= len(model):
            index = len(model) - 1

        if model.index == index:
            return

        model.index = index
        for m in [sm for sm in self._models if sm != model]:
            if m.index_direction == model.index_direction:
                m.index = index

            if m.x_index_direction == model.index_direction:
                m.x_index = index

            if m.y_index_direction == model.index_direction:
                m.y_index = index

        self.load_data()

    def model_xy_indexes_changed(self, model, x, y):
        """
        :type model: SliceModel
        :type x: int
        :type y: int
        """
        model.x_index = x
        model.y_index = y
        for m in [sm for sm in self._models if sm != model]:
            if m.index_direction == model.x_index_direction:
                m.index = x

            if m.x_index_direction == model.x_index_direction:
                m.x_index = x

            if m.y_index_direction == model.x_index_direction:
                m.y_index = x

            if m.index_direction == model.y_index_direction:
                m.index = y

            if m.x_index_direction == model.y_index_direction:
                m.x_index = y

            if m.y_index_direction == model.y_index_direction:
                m.y_index = y

        self.load_data()

    def load_data(self):
        for m in [sm for sm in self._models if sm.dirty and sm.visible]:
            # print("loading data for %s" % m.title)
            m.data = self._slice_data_source.read_slice(m.index_direction, m.index)

    def reset(self):
        for model in self._models:
            model.reset()
        self._assign_indexes()
