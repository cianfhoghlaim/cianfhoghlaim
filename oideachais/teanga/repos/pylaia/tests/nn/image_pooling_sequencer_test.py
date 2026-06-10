import unittest

import torch

from laia.nn import ImagePoolingSequencer


class ImagePoolingSequencerTest(unittest.TestCase):
    def test_bad_sequencer(self):
        self.assertRaises(ValueError, ImagePoolingSequencer, sequencer="")
        self.assertRaises(ValueError, ImagePoolingSequencer, sequencer="foo")
        self.assertRaises(ValueError, ImagePoolingSequencer, sequencer="maxpool")
        self.assertRaises(ValueError, ImagePoolingSequencer, sequencer="avgpool-")
        self.assertRaises(ValueError, ImagePoolingSequencer, sequencer="maxpool-c")


def _generate_test(sequencer, poolsize, columnwise, x, output_size):
    def _test(self):
        m = ImagePoolingSequencer(
            sequencer=f"{sequencer}-{poolsize}", columnwise=columnwise
        )
        y = m(x)
        self.assertEqual(output_size, list(y.size()))

    return _test


def _generate_failing_test(sequencer, poolsize, columnwise, x):
    def _test(self):
        m = ImagePoolingSequencer(
            sequencer=f"{sequencer}-{poolsize}", columnwise=columnwise
        )
        self.assertRaises(ValueError, lambda: m(x))

    return _test


devices = ["cpu", "cuda"] if torch.cuda.is_available() else ["cpu"]
dtypes = [torch.float, torch.double]

for sequencer in ["none", "maxpool", "avgpool"]:
    setattr(
        ImagePoolingSequencerTest,
        f"test_tensor_{sequencer}_col",
        _generate_test(
            sequencer=sequencer,
            poolsize=10,
            columnwise=True,
            x=torch.randn(2, 3, 10, 11),
            output_size=[11, 2, 3 * 10],
        ),
    )
    setattr(
        ImagePoolingSequencerTest,
        f"test_tensor_{sequencer}_row",
        _generate_test(
            sequencer=sequencer,
            poolsize=11,
            columnwise=False,
            x=torch.randn(2, 3, 10, 11),
            output_size=[10, 2, 3 * 11],
        ),
    )

for columnwise in True, False:
    setattr(
        ImagePoolingSequencerTest,
        f"test_tensor_bad_input_{'col' if columnwise else 'row'}",
        _generate_failing_test(
            sequencer="none",
            poolsize=9,
            columnwise=columnwise,
            x=torch.randn(2, 3, 4, 5),
        ),
    )

if __name__ == "__main__":
    unittest.main()
