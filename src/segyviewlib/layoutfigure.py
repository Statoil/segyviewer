from matplotlib import gridspec
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class LayoutFigure(Figure):
    def __init__(self, width=11.7, height=8.3, dpi=100, tight_layout=True, **kwargs):
        super(LayoutFigure, self).__init__(figsize=(width, height), dpi=dpi, tight_layout=tight_layout, **kwargs)

        self._current_layout = None

        self._axes = []
        """ :type: list[Axes] """

        self._colormap_axes = None
        """ :type: Axes """

    def set_plot_layout(self, layout_spec):
        rows, columns = layout_spec['dims']
        width = 0.025
        ratios = [(1.0 - width) / float(columns)] * columns
        ratios.append(width)

        grid_spec = gridspec.GridSpec(rows, columns + 1, width_ratios=ratios)

        for axes in self._axes:
            self.delaxes(axes)
        self._axes = [self.add_subplot(grid_spec[sub_spec]) for sub_spec in layout_spec['grid']]

        if self._colormap_axes is not None:
            self.delaxes(self._colormap_axes)
        self._colormap_axes = self.add_subplot(grid_spec[:, columns])

        self._current_layout = layout_spec

    def index(self, axes):
        """
        :param axes: The Axes instance to find the index of.
        :type axes: Axes
        :rtype: int
        """
        return None if axes is self._colormap_axes else self._axes.index(axes)

    def colormap_axes(self):
        """
        :rtype: Axes
        """
        return self._colormap_axes

    def layout_axes(self):
        """ :rtype: list[Axes] """
        return list(self._axes)

    def current_layout(self):
        return self._current_layout
