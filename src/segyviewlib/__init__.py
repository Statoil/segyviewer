import os.path as path

img_prefix = path.abspath(path.join(path.dirname(path.abspath(__file__)), "resources", "img"))

if not path.exists(img_prefix):
    img_prefix = path.abspath(path.join(path.dirname(path.abspath(__file__)), "..", "..", "resources", "img"))


def resource_icon_path(name):
    return path.join(img_prefix, name)


def resource_icon(name):
    """Load an image as an icon"""
    # print("Icon used: %s" % name)
    from PyQt4.QtGui import QIcon
    return QIcon(resource_icon_path(name))


from .colormapcombo import ColormapCombo
from .layoutcombo import LayoutCombo
from .layoutfigure import LayoutFigure
from .layoutcanvas import LayoutCanvas

from .slicemodel import SliceModel, SliceDirection
from .slicedatasource import SliceDataSource
from .slicemodelcontroller import SliceModelController
from .sliceview import SliceView
from .sliceviewwidget import SliceViewWidget
from .segyviewwidget import SegyViewWidget

__version__ = '1.0.4'
__copyright__ = 'Copyright 2016, Statoil ASA'
__license__ = 'GNU Lesser General Public License version 3'
__status__ = 'Production'
