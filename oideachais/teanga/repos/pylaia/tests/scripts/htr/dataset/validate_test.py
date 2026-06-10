import torch
from conftest import call_script
from PIL import Image

import laia.scripts.htr.dataset.validate as script
from laia.common.saver import ModelSaver
from laia.models.htr.laia_crnn import LaiaCRNN

TR_TXT_TABLE = """
tmp-0 a a e b c
tmp-1 a a b b c
tmp-2 d a b b c
"""

VA_TXT_TABLE = """
tmp-3 a a a a c
tmp-4 b b f b c
tmp-5 b a b b c
"""

TE_TXT_TABLE = """
tmp-6 a a a a c
tmp-7 b b b b c
tmp-8 b a b b c
"""

IMG_SIZES_VALID = {
    "tmp-0": (1000, 128),
    "tmp-1": (2000, 128),
    "tmp-2": (1500, 128),
    "tmp-3": (1000, 128),
    "tmp-4": (2000, 128),
    "tmp-5": (1500, 128),
    "tmp-6": (100, 128),
    "tmp-7": (2000, 128),
    "tmp-8": (1500, 128),
}

IMG_SIZES_INVALID = {
    "tmp-0": (1000, 128),
    "tmp-1": (2000, 128),
    "tmp-2": (1500, 129),
    "tmp-3": (1000, 128),
    "tmp-4": (2000, 128),
    "tmp-5": (1500, 128),
    "tmp-6": (4, 128),
    "tmp-7": (2000, 128),
    "tmp-8": (1500, 128),
}

SYMS = """
<ctc> 0
a 1
b 2
c 3
d 4
e 5
f 6
<space> 7
"""

EXPECTED_STATS = """
Statistics
==========

# Train

## Images statistics

| Metric | Width  | Height |
| :------| :----: | :----: |
| Count  |   3    |   3    |
| Min    |  1000  |  128   |
| Max    |  2000  |  128   |
| Mean   | 1500.0 | 128.0  |
| Median |  1500  |  128   |

## Labels statistics

| Metric | Chars | Words |
| :------| :---: | :---: |
| Min    |   5   |   1   |
| Max    |   5   |   1   |
| Mean   |  5.0  |  1.0  |
| Median |   5   |   1   |
| Total  |   15  |   3   |

### Characters statistics

| Character | Occurrence |
| :---------|----------: |
| a         |          5 |
| b         |          5 |
| c         |          3 |
| e         |          1 |
| d         |          1 |

# Val

## Images statistics

| Metric | Width  | Height |
| :------| :----: | :----: |
| Count  |   3    |   3    |
| Min    |  1000  |  128   |
| Max    |  2000  |  128   |
| Mean   | 1500.0 | 128.0  |
| Median |  1500  |  128   |

## Labels statistics

| Metric | Chars | Words |
| :------| :---: | :---: |
| Min    |   5   |   1   |
| Max    |   5   |   1   |
| Mean   |  5.0  |  1.0  |
| Median |   5   |   1   |
| Total  |   15  |   3   |

### Characters statistics

| Character | Occurrence |
| :---------|----------: |
| b         |          6 |
| a         |          5 |
| c         |          3 |
| f         |          1 |

# Test

## Images statistics

| Metric | Width  | Height |
| :------| :----: | :----: |
| Count  |   3    |   3    |
| Min    |  100   |  128   |
| Max    |  2000  |  128   |
| Mean   | 1200.0 | 128.0  |
| Median |  1500  |  128   |

## Labels statistics

| Metric | Chars | Words |
| :------| :---: | :---: |
| Min    |   5   |   1   |
| Max    |   5   |   1   |
| Mean   |  5.0  |  1.0  |
| Median |   5   |   1   |
| Total  |   15  |   3   |

### Characters statistics

| Character | Occurrence |
| :---------|----------: |
| b         |          7 |
| a         |          5 |
| c         |          3 |
"""


def prepare_model(tmpdir):
    args = [
        1,  # num_input_channels
        12,  # num_output_channels
        [12, 24, 48, 48],  # cnn_num_features
        [(3, 3)] * 4,  # cnn_kernel_size
        [(1, 1)] * 4,  # cnn_stride
        [(1, 1)] * 4,  # cnn_dilation
        [torch.nn.LeakyReLU] * 4,  # cnn_activation
        [(2, 2), (2, 2), (0, 0), (2, 2)],  # cnn_poolsize
        [0] * 4,  # cnn_dropout
        [False] * 4,  # cnn_batchnorm
        "avgpool-8",
        256,  # rnn_units
        3,  # rnn_layers
        0.5,  # rnn_dropout
        0.5,  # lin_dropout
    ]
    LaiaCRNN(*args)  # check for failures
    ModelSaver(tmpdir).save(LaiaCRNN, *args)


def prepare_data(tmpdir, img_sizes) -> None:
    # Prepare images
    for image_id, size in img_sizes.items():
        im = Image.new(mode="L", size=size)
        im.save(str(tmpdir / f"{image_id}.jpg"))
    # Prepare data
    (tmpdir / "train.txt").write_text(TR_TXT_TABLE, "utf-8")
    (tmpdir / "val.txt").write_text(VA_TXT_TABLE, "utf-8")
    (tmpdir / "test.txt").write_text(TE_TXT_TABLE, "utf-8")
    (tmpdir / "syms.txt").write_text(SYMS, "utf-8")


def test_run_validate_valid_dataset(tmpdir) -> None:
    prepare_data(tmpdir, IMG_SIZES_VALID)
    prepare_model(tmpdir)
    args = [
        f"{tmpdir/'syms.txt'}",
        f"[{tmpdir}]",
        f"{tmpdir/'train.txt'}",
        f"{tmpdir/'val.txt'}",
        f"{tmpdir/'test.txt'}",
        "--fixed_input_height=128",
        "--statistics_output=statistics.md",
        f"--common.train_path={tmpdir}",
    ]
    _, stderr = call_script(script.__file__, args)
    assert "Dataset is valid" in stderr
    assert "Statistics written to statistics.md" in stderr


def test_run_validate_invalid_dataset(tmpdir) -> None:
    prepare_data(tmpdir, IMG_SIZES_INVALID)
    prepare_model(tmpdir)
    args = [
        f"{tmpdir/'syms.txt'}",
        f"[{tmpdir}]",
        f"{tmpdir/'train.txt'}",
        f"{tmpdir/'val.txt'}",
        f"{tmpdir/'test.txt'}",
        f"--fixed_input_height={128}",
        "--statistics_output=statistics.md",
        f"--common.train_path={tmpdir}",
    ]
    _, stderr = call_script(script.__file__, args)
    assert not tmpdir.join("statistics.md").exists()
    assert "Issues found in the dataset" in stderr
    assert "train - Found images with variable heights" in stderr
    assert (
        "test - Found some images too small for convolutions (width<8). They will be padded during training."
        in stderr
    )
