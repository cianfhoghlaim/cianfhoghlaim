import torch

from laia.data import PaddedTensor
from laia.nn import PyramidMaxPool2d


def test_tensor():
    x = torch.randn(3, 5, 7, 8, dtype=torch.double, requires_grad=True)
    layer = PyramidMaxPool2d(levels=[1, 2])
    assert (3, 5 * (1 + 2 * 2)) == layer(x).size()
    torch.autograd.gradcheck(lambda x: layer(x).sum(), x)


def test_padded_tensor():
    x = torch.tensor(
        [
            [
                [
                    [1, 2, 3, 4, 5, 6, 7, 8],
                    [9, 10, 11, 12, 13, 14, 15, 16],
                    [17, 18, 19, 20, 21, 22, 23, 24],
                    [25, 26, 27, 28, 29, 30, 31, 32],
                ]
            ]
        ],
        dtype=torch.double,
        requires_grad=True,
    )
    xs = torch.tensor([[3, 4]])
    layer = PyramidMaxPool2d(levels=[1, 2])
    y = layer(PaddedTensor(x, xs))
    torch.testing.assert_close(y, torch.tensor([[20, 10, 12, 18, 20]], dtype=x.dtype))
    torch.autograd.gradcheck(lambda x: layer(PaddedTensor(x, xs)), x)
