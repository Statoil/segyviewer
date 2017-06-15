from unittest import TestCase
from segyviewlib import SliceViewContext, SliceModel, SliceDirection as SD, SliceDataSource


class SliceViewContextTest(TestCase):
    @staticmethod
    def _generate_mock_model_and_context():
        model = SliceModel("test", SD.inline, SD.crossline, SD.depth)
        svc = SliceViewContext([model], SliceDataSource(None))
        return model, svc

    def test_min_max_symmetry(self):
        model, svc = SliceViewContextTest._generate_mock_model_and_context()

        model._min_value = -20
        model._max_value = 120
        context = svc.create_context([model])

        # when min<0<max, expect the scale to be symmetrically centered around 0
        self.assertEqual(context['min'], -120)
        self.assertEqual(context['max'], 120)

    def test_min_max_pos_values(self):
        model, svc = SliceViewContextTest._generate_mock_model_and_context()

        model._min_value = 1
        model._max_value = 120
        context = svc.create_context([model])

        self.assertEqual(context['min'], 1)
        self.assertEqual(context['max'], 120)

    def test_min_max_neg_values(self):
        model, svc = SliceViewContextTest._generate_mock_model_and_context()

        model._min_value = -40
        model._max_value = -21
        context = svc.create_context([model])

        self.assertEqual(context['min'], -40)
        self.assertEqual(context['max'], -21)
