from PyQt4.QtGui import QSpinBox, QValidator


class ArraySpinBox(QSpinBox):
    def __init__(self, values, parent=None):
        QSpinBox.__init__(self, parent)
        self.setKeyboardTracking(False)
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
        val = self._values[index]
        if isinstance(val, float):
            val = round(val, 4)
        return str(val)

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
                if str(value).startswith(text[:pos]):
                    return QValidator.Intermediate, pos
            return QValidator.Invalid, pos

        return QValidator.Acceptable, pos
