import pytest
from PIL import Image

from laia.utils.stats import ImageLabelsStats, Split

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
tmp-6
tmp-7
tmp-8
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


@pytest.mark.parametrize(
    "stage, tables, img_sizes, expected_min_width, expected_max_width, expected_is_fixed_height, expected_charset, expected_height, expected_filenames_invalid_height",
    [
        (
            Split.train,
            ["train.txt"],
            IMG_SIZES_VALID,
            1000,
            2000,
            True,
            {"a", "b", "c", "d", "e"},
            128,
            [],
        ),
        (
            Split.val,
            ["val.txt"],
            IMG_SIZES_VALID,
            1000,
            2000,
            True,
            {"a", "b", "c", "f"},
            128,
            [],
        ),
        (Split.test, ["test.txt"], IMG_SIZES_VALID, 100, 2000, True, set(), 128, []),
        (
            Split.train,
            ["train.txt"],
            IMG_SIZES_INVALID,
            1000,
            2000,
            False,
            {"a", "b", "c", "d", "e"},
            128,
            ["tmp-2.jpg"],
        ),
        (Split.test, ["test.txt"], IMG_SIZES_INVALID, 4, 2000, True, set(), 128, []),
        (
            "fit",
            ["train.txt", "val.txt"],
            IMG_SIZES_VALID,
            1000,
            2000,
            True,
            {"a", "b", "c", "d", "e", "f"},
            128,
            [],
        ),
        (
            "fit",
            ["train.txt", "val.txt"],
            IMG_SIZES_INVALID,
            1000,
            2000,
            False,
            {"a", "b", "c", "d", "e", "f"},
            128,
            ["tmp-2.jpg"],
        ),
    ],
)
def test_img_stats(
    tmpdir,
    stage,
    tables,
    img_sizes,
    expected_min_width,
    expected_max_width,
    expected_is_fixed_height,
    expected_charset,
    expected_height,
    expected_filenames_invalid_height,
):
    prepare_data(tmpdir, img_sizes)
    img_stats = ImageLabelsStats(
        stage=stage,
        tables=[str(tmpdir / table) for table in tables],
        img_dirs=[tmpdir],
    )
    assert img_stats.max_width == expected_max_width
    assert img_stats.min_width == expected_min_width
    assert img_stats.is_fixed_height == expected_is_fixed_height
    assert img_stats.character_set == expected_charset
    if img_stats.is_fixed_height:
        assert img_stats.min_height == expected_height
    assert img_stats.get_invalid_images_height(expected_height) == [
        str(tmpdir / filename) for filename in expected_filenames_invalid_height
    ]
