from PyQt4.QtCore import QObject, pyqtSignal

from .slicemodel import SliceDirection
import numpy as np
import segyio


class EmptyDataSource(object):
    def __init__(self):
        super(EmptyDataSource, self).__init__()
        self._data = np.zeros((2, 2), dtype=np.single)
        self._data[0, 0] = -1.0
        self._data[1, 1] = 1.0

    @property
    def ilines(self):
        return [0, 1]

    @property
    def xlines(self):
        return [0, 1]

    @property
    def samples(self):
        return 2

    @property
    def iline(self):
        return [self._data, self._data]

    @property
    def xline(self):
        return [self._data, self._data]

    @property
    def iline(self):
        return [self._data, self._data]

    @property
    def depth_slice(self):
        return [self._data, self._data]

    @property
    def sorting(self):
        return segyio.TraceSortingFormat.CROSSLINE_SORTING


class SliceDataSource(QObject):
    slice_data_source_changed = pyqtSignal()

    def __init__(self, filename, **kwargs):
        QObject.__init__(self)

        self._source = None
        """ :type: segyio.SegyFile """
        self.set_source_filename(filename, **kwargs)

    def _close_current_file(self):
        if isinstance(self._source, segyio.SegyFile):
            self._source.close()

        self._source = None

    def set_source_filename(self, filename, **kwargs):
        if filename:
            try:
                source = segyio.open(filename, "r", **kwargs)
            except:
                raise
            else:
                self._close_current_file()
                self._source = source
                self._source.mmap()
        else:
            self._close_current_file()
            self._source = EmptyDataSource()

        self.slice_data_source_changed.emit()

    def read_slice(self, direction, index):
        if direction == SliceDirection.inline:
            iline_index = self._source.ilines[index]
            return self._source.iline[iline_index].T
        elif direction == SliceDirection.crossline:
            xline_index = self._source.xlines[index]
            return self._source.xline[xline_index].T
        elif direction == SliceDirection.depth:
            data = self._source.depth_slice[index]
            if self._source.sorting == segyio.TraceSortingFormat.CROSSLINE_SORTING:
                return data
            else:
                return data.T
        else:
            raise ValueError("Unknown direction: %s" % direction)

    def indexes_for_direction(self, direction):
        if direction == SliceDirection.inline:
            return self._source.ilines
        elif direction == SliceDirection.crossline:
            return self._source.xlines
        elif direction == SliceDirection.depth:
            return np.fromiter(range(self._source.samples), dtype=np.uintc)  # add t0?
        else:
            raise ValueError("Unknown direction: %s" % direction)

    def __del__(self):
        self._close_current_file()

    def dims(self):
        iline_count = len(self._source.ilines)
        xline_count = len(self._source.xlines)
        offset_count = 1
        sample_count = self._source.samples
        return iline_count, xline_count, offset_count, sample_count
