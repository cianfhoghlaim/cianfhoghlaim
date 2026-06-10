from laia.utils.mdutils import Statistics


def test_display_image_statistics(tmp_path):
    stats = Statistics(filename=tmp_path)
    stats.create_image_statistics(widths=[150, 1500, 1600], heights=[128, 128, 128])
    assert (
        stats.document.get_md_text()
        == """
Statistics
==========

## Images statistics

| Metric |  Width  | Height |
| :------| :-----: | :----: |
| Count  |    3    |   3    |
| Min    |   150   |  128   |
| Max    |   1600  |  128   |
| Mean   | 1083.33 | 128.0  |
| Median |   1500  |  128   |
"""
    )


def test_display_label_statistics(tmp_path):
    filename = tmp_path / "labels.md"
    stats = Statistics(filename=str(filename))
    stats.create_label_statistics(
        labels=[
            ["a", "<space>", "t", "e", "x", "t"],
            ["a", "n", "o", "t", "h", "e", "r" "<space>", "t", "e", "x", "t"],
        ],
        delimiters=["<space>"],
    )
    assert (
        stats.document.get_md_text()
        == """
Statistics
==========

## Labels statistics

| Metric | Chars | Words |
| :------| :---: | :---: |
| Min    |   6   |   2   |
| Max    |   11  |   2   |
| Mean   |  8.5  |  2.0  |
| Median |   8   |   2   |
| Total  |   17  |   4   |

### Characters statistics

| Character | Occurrence |
| :---------|----------: |
| t         |          5 |
| e         |          3 |
| a         |          2 |
| x         |          2 |
| <space>   |          1 |
| n         |          1 |
| o         |          1 |
| h         |          1 |
| r<space>  |          1 |
"""
    )
