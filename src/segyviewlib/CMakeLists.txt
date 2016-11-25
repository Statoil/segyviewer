set(PYTHON_SOURCES
    __init__.py
    layoutcombo.py
    layoutcanvas.py
    layoutfigure.py
    colormapcombo.py

    slicemodel.py
    slicedatasource.py
    slicemodelcontroller.py
    sliceview.py
    sliceviewwidget.py

    segyviewwidget.py

    )

add_python_package(segyviewlib segyviewlib "${PYTHON_SOURCES}")
