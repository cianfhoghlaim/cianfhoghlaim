from collections import Counter, defaultdict
from functools import partial
from typing import Dict, List, Union

import numpy as np
from mdutils.mdutils import MdUtils
from prettytable import MARKDOWN, PrettyTable

from laia.callbacks.meters.sequence_error import char_to_word_seq

# Name of the first column
METRIC_COLUMN = "Metric"


def create_table(
    data: Dict[str, List[Union[int, float]]],
    count: bool = False,
    total: bool = True,
) -> PrettyTable:
    """
    Generate a PrettyTable object from an input dictionary.
    Compute min, max, mean, median, total by default.
    Total can be disabled. Count (length) computation can be enabled.

    Args:
        data: Data to display. Each key will be made into a column.
        count: Whether to display an additional row for data count.
        total: Whether to display an additional row for data total sum.

    Returns:
        PrettyTable: A Markdown table
    """

    statistics = PrettyTable(field_names=[METRIC_COLUMN, *data.keys()])
    statistics.align.update({METRIC_COLUMN: "l"})
    statistics.set_style(MARKDOWN)

    operations = []

    if count:
        operations.append(("Count", len, None))

    operations.extend(
        [
            ("Min", np.min, None),
            ("Max", np.max, None),
            ("Mean", np.mean, 2),
            ("Median", np.median, None),
        ]
    )
    if total:
        operations.append(("Total", np.sum, None))

    statistics.add_rows(
        [
            [
                col_name,
                *list(
                    map(
                        # Round values if needed
                        partial(round, ndigits=digits),
                        map(operator, data.values()),
                    )
                ),
            ]
            for col_name, operator, digits in operations
        ]
    )

    return statistics


class Statistics:
    HEADERS = {
        "Images": "Images statistics",
        "Labels": "Labels statistics",
        "Chars": "Characters statistics",
    }

    def __init__(self, filename: str) -> None:
        self.document = MdUtils(file_name=filename, title="Statistics")

    def _write_section(self, table: PrettyTable, title: str, level: int = 2):
        """
        Write the new section in the file.

        <title with appropriate level>

        <table>

        """
        self.document.new_header(level=level, title=title, add_table_of_contents="n")
        self.document.write("\n")

        self.document.write(table.get_string())
        self.document.write("\n")

    def create_image_statistics(self, widths: List[int], heights: List[int]):
        """
        Compute statistics on image sizes and write them to file.
        """
        self._write_section(
            table=create_table(
                data={"Width": widths, "Height": heights}, count=True, total=False
            ),
            title=Statistics.HEADERS["Images"],
        )

    def create_label_statistics(self, labels: List[str], delimiters: List[str]):
        """
        Compute statistics on text labels and write them to file.
        """
        char_counter = Counter()
        data = defaultdict(list)

        for text in labels:
            char_counter.update(text)
            data["Chars"].append(len(text))
            data["Words"].append(len(char_to_word_seq("".join(text), delimiters)))

        self._write_section(
            table=create_table(data=data),
            title=Statistics.HEADERS["Labels"],
        )

        self.create_character_occurrences_statistics(char_counter)

    def create_character_occurrences_statistics(self, char_counter: Counter):
        """
        Compute statistics on the character distribution and write them to file.
        """
        char_occurrences = PrettyTable(
            field_names=["Character", "Occurrence"],
        )
        char_occurrences.align.update({"Character": "l", "Occurrence": "r"})
        char_occurrences.set_style(MARKDOWN)
        char_occurrences.add_rows(list(char_counter.most_common()))

        self._write_section(
            table=char_occurrences, title=Statistics.HEADERS["Chars"], level=3
        )

    def create_split_section(self, split, widths, heights, labels, delimiters):
        # prepare the data
        self.document.new_header(level=1, title=split.capitalize())
        self.create_image_statistics(widths=widths, heights=heights)
        self.create_label_statistics(labels=labels, delimiters=delimiters)
