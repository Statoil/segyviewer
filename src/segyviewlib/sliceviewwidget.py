from PyQt4.QtCore import QPoint
from PyQt4.QtGui import QMenu, QAction
from math import copysign

from segyviewlib import SliceView, LayoutCanvas, SliceModel, SliceModelController, SliceDataSource
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize


class SliceViewWidget(LayoutCanvas):
    def __init__(self, models, data_source, colormap='seismic', width=11.7, height=8.3, dpi=100, parent=None):
        super(SliceViewWidget, self).__init__(width, height, dpi, parent)

        self._available_slice_models = list(models)
        """ :type: list[SliceModel] """
        self._assigned_slice_models = list(models)
        """ :type: list[SliceModel] """
        self._slice_views = {}
        """ :type: dict[matplotlib.axes.Axes,SliceView] """

        self._slice_model_controller = SliceModelController(self._available_slice_models, data_source)

        self._colormap_name = colormap
        self._colormappable = ScalarMappable(cmap=colormap)
        self._colormappable.set_array([])

        self._show_indicators = False

        self.layout_changed.connect(self._layout_changed)
        self.subplot_pressed.connect(self._subplot_clicked)
        self.subplot_scrolled.connect(self._subplot_scrolled)
        self.subplot_motion.connect(self._subplot_motion)

        self._global_min = None
        self._global_max = None

    def set_colormap(self, colormap):
        self._colormap_name = colormap
        self._colormappable.set_cmap(colormap)
        self._context_changed()

    def show_indicators(self, visible):
        self._show_indicators = visible
        self._context_changed()

    def _create_context(self):
        view_min = None
        view_max = None

        for model in self._assigned_slice_models:
            view_min = model.min_value if view_min is None else min(model.min_value, view_min)
            view_max = model.max_value if view_max is None else max(model.max_value, view_max)
            self._global_min = view_min if self._global_min is None else min(self._global_min, view_min)
            self._global_max = view_max if self._global_max is None else max(self._global_max, view_max)

        vmin = self._global_min
        vmax = self._global_max
        if vmin <= 0.0 <= vmax:
            vmax = max(abs(vmin), vmax)
            vmin = -vmax

        return {
            "colormap": self._colormap_name,
            "show_indicators": self._show_indicators,
            "global_min": self._global_min,
            "global_max": self._global_max,
            "view_min": view_min,
            "view_max": view_max,
            "min": vmin,
            "max": vmax,
            "normalize": Normalize(vmin=vmin, vmax=vmax)
        }

    def _layout_changed(self):
        fig = self.layout_figure()
        axes = fig.layout_axes()
        self._slice_views.clear()

        for model in self._available_slice_models:
            model.visible = False

        for index, ax in enumerate(axes):
            ax.clear()
            if index < len(self._assigned_slice_models):
                model = self._assigned_slice_models[index]
                model.visible = True
                self._slice_views[ax] = SliceView(ax, model)
                self._slice_views[ax].create_slice(self._create_context())

        colormap_axes = self.layout_figure().colormap_axes()
        colorbar = self.layout_figure().colorbar(self._colormappable, cax=colormap_axes, use_gridspec=True)
        colorbar.ax.tick_params(labelsize=9)

        self._slice_model_controller.load_data()
        self._data_changed()

    def _data_changed(self):
        context = self._create_context()
        for slice_view in self._slice_views.values():
            slice_view.data_changed(context)
        self._context_changed()

    def _context_changed(self):
        for slice_view in self._slice_views.values():
            slice_view.context_changed(self._create_context())

        ctx = self._create_context()
        self._colormappable.set_clim(ctx['min'], ctx['max'])
        self.draw()

    def _create_slice_view_context_menu(self, subplot_index):
        context_menu = QMenu("Slice Model Reassignment Menu", self)

        def reassign(model):
            def fn():
                self._assigned_slice_models[subplot_index] = model
                self._layout_changed()

            return fn

        for model in self._available_slice_models:
            action = QAction(model.title, self)
            action.triggered.connect(reassign(model))
            context_menu.addAction(action)

        return context_menu

    def _subplot_clicked(self, event):
        keys = event['key']

        if self._show_indicators and event['button'] == 1 and not keys:
            x = int(event['x'])
            y = int(event['y'])
            slice_model = self._get_slice_view(event).model()
            self._slice_model_controller.model_xy_indexes_changed(slice_model, x, y)
            self._data_changed()

        elif event['button'] == 3 and (not keys or keys.state(ctrl=True)):
            subplot_index = event['subplot_index']
            context_menu = self._create_slice_view_context_menu(subplot_index)
            context_menu.exec_(self.mapToGlobal(QPoint(event['mx'], self.height() - event['my'])))

    def _subplot_scrolled(self, event):
        keys = event['key']
        if not keys:
            # at least 1 step per event but a maximum of 5
            step = max(1, abs(int(event['step'])))
            step = min(step, 5)
            step = copysign(step, event['step'])

            slice_model = self._get_slice_view(event).model()
            index = slice_model.index + step

            if 0 <= index < len(slice_model):
                self._slice_model_controller.model_index_changed(slice_model, int(index))
                self._data_changed()

        elif keys.state(ctrl=True) or keys.state(shift=True):
            x = event['x']
            y = event['y']
            step = max(1, abs(int(event['step'])))
            step = copysign(step / 20.0, event['step'])

            slice_view = self._get_slice_view(event)

            if slice_view.zoom(x, y, step):
                self._context_changed()

    def _get_slice_view(self, event):
        subplot_index = event['subplot_index']
        fig = self.layout_figure()
        ax = fig.layout_axes()[subplot_index]
        slice_view = self._slice_views[ax]
        return slice_view

    def _subplot_motion(self, event):
        keys = event['key']
        if keys.state(shift=True) or keys.state(ctrl=True):
            dx = event['dx']
            dy = event['dy']

            if dx is not None and dy is not None:
                slice_view = self._get_slice_view(event)
                slice_view.pan(dx, dy)
                self._context_changed()

    def slice_data_source_changed(self):
        self._global_max = None
        self._global_min = None
        self._slice_model_controller.reset()
        self._layout_changed()
