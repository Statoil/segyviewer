from unittest import TestCase

from segyviewlib import SliceModel, SliceDirection as SD
import numpy as np


class SliceModelTest(TestCase):
    def test_default_model(self):
        model = SliceModel("test", SD.inline, SD.crossline, SD.depth)

        self.assertEqual(model.title, "test")
        self.assertEqual(model.x_axis_name, SD.crossline['name'])
        self.assertEqual(model.y_axis_name, SD.depth['name'])
        self.assertIsNone(model.data)
        self.assertEqual(model.index, 0)
        self.assertIsNone(model.max_value)
        self.assertEqual(model.x_index, 0)
        self.assertEqual(model.y_index, 0)
        self.assertIsNone(model.indexes)
        self.assertIsNone(model.x_indexes)
        self.assertIsNone(model.y_indexes)
        self.assertTrue(model.visible)
        self.assertFalse(model.dirty)

        self.assertEqual(model.index_direction, SD.inline)
        self.assertEqual(model.x_index_direction, SD.crossline)
        self.assertEqual(model.y_index_direction, SD.depth)

        with self.assertRaises(TypeError):
            r = model.min_x

        with self.assertRaises(TypeError):
            r = model.min_y

        with self.assertRaises(TypeError):
            r = model.max_x

        with self.assertRaises(TypeError):
            r = model.max_y

        with self.assertRaises(TypeError):
            r = model.width

        with self.assertRaises(TypeError):
            r = model.height

    def test_minimal_model_with_data(self):
        model = SliceModel("test", SD.inline, SD.crossline, SD.depth)
        data = np.zeros((3, 5))
        data[0, 0] = -1.5
        data[2, 3] = 1.5
        model.data = data

        self.assertIsInstance(model.data, np.ndarray)
        self.assertListEqual(model.x_indexes, [0, 1, 2])
        self.assertListEqual(model.y_indexes, [0, 1, 2, 3, 4])
        self.assertEqual(model.min_x, 0)
        self.assertEqual(model.min_y, 0)
        self.assertEqual(model.max_x, 2)
        self.assertEqual(model.max_y, 4)
        self.assertAlmostEqual(model.min_value, -1.5)
        self.assertAlmostEqual(model.max_value, 1.5)
        self.assertEqual(model.width, 3)
        self.assertEqual(model.height, 5)

    def test_adjusted_model_with_data(self):
        model = SliceModel("test", SD.inline, SD.crossline, SD.depth)
        model.data = np.zeros((3, 5))

        model.x_indexes = [2, 4, 6, 8, 10]
        model.y_indexes = [1, 3, 5]
        self.assertListEqual(model.x_indexes, [2, 4, 6, 8, 10])
        self.assertListEqual(model.y_indexes, [1, 3, 5])
        self.assertEqual(model.min_x, 2)
        self.assertEqual(model.min_y, 1)
        self.assertEqual(model.max_x, 10)
        self.assertEqual(model.max_y, 5)
        self.assertEqual(model.width, 5)
        self.assertEqual(model.height, 3)

        with self.assertRaises(ValueError):
            model.x_indexes = [2, 4, 6, 8]

        with self.assertRaises(ValueError):
            model.y_indexes = [2, 4, 6, 8]

        with self.assertRaises(ValueError):
            model.data = np.zeros((2, 2))

    def test_formatters(self):
        model = SliceModel("test", SD.inline, SD.crossline, SD.depth)
        model.x_indexes = [1, 3, 7, 9]
        model.y_indexes = [2, 4, 6, 8]

        self.assertEqual(model.x_axis_formatter(0, 0), 1)
        self.assertEqual(model.x_axis_formatter(2, 0), 7)
        self.assertEqual(model.x_axis_formatter(-1, 0), '')

        self.assertEqual(model.y_axis_formatter(0, 0), 2)
        self.assertEqual(model.y_axis_formatter(2, 0), 6)
        self.assertEqual(model.y_axis_formatter(7, 0), '')

    def test_simple_setters(self):
        model = SliceModel("test", SD.inline, SD.crossline, SD.depth)
        model.indexes = [1, 2, 3]
        model.index = 5
        model.x_index = 99
        model.y_index = 33
        model.visible = False

        self.assertTrue(model.dirty)
        model.data = np.zeros((2, 2))
        self.assertFalse(model.dirty)

        self.assertEqual(model.index, 5)
        self.assertEqual(model.indexes, [1, 2, 3])
        self.assertEqual(len(model), 3)
        self.assertEqual(model.x_index, 99)
        self.assertEqual(model.y_index, 33)
        self.assertFalse(model.visible)

    def test_reset(self):
        model = SliceModel("test", SD.inline, SD.crossline, SD.depth)
        model.data = np.zeros((3, 5))
        model.data[0, 0] = -1.0
        model.data[1, 0] = 1.0

        model.x_indexes = [2, 4, 6, 8, 10]
        model.y_indexes = [1, 3, 5]

        model.indexes = [1, 2, 3]
        model.index = 5
        model.x_index = 99
        model.y_index = 33

        model.reset()

        self.assertIsNone(model.data)
        self.assertEqual(model.index, 0)
        self.assertIsNone(model.max_value)
        self.assertEqual(model.x_index, 0)
        self.assertEqual(model.y_index, 0)
        self.assertIsNone(model.indexes)
        self.assertIsNone(model.x_indexes)
        self.assertIsNone(model.y_indexes)