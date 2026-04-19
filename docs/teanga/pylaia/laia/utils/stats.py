from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import List, Optional, TextIO, Union

import imagesize

from laia.data.image_from_list_dataset import _get_img_ids_and_filepaths
from laia.data.text_image_from_text_table_dataset import (
    _get_images_and_texts_from_text_table,
)
from laia.utils.symbols_table import SymbolsTable


class Split(Enum):
    """
    Split names
    """

    train = "train"
    val = "val"
    test = "test"

    def __str__(self) -> str:
        return self.value


class ImageLabelsStats:
    """
    Compute statistics on the dataset

    Args:
        stage: String indicating the stage of the processing, either "test" or "fit"
        tables: List of ids (test mode) with tokenized text (train and val mode)
        img_dirs: Path to images
    """

    def __init__(
        self,
        stage: Union[str, Split],
        tables: List[Union[TextIO, str, List[str]]],
        img_dirs: Optional[Union[List[str], str, List[Path], Path]] = None,
    ):
        self.filenames = []
        self.labels = []
        for table in tables:
            # Test split has no labels
            if isinstance(stage, Split) and stage == Split.test:
                self.filenames.extend(_get_img_ids_and_filepaths(table, img_dirs)[1])
                continue

            _, filenames, labels = _get_images_and_texts_from_text_table(
                table, img_dirs
            )
            self.filenames.extend(filenames)
            self.labels.extend(x.split() for x in labels)

        sizes = list(map(imagesize.get, self.filenames))
        self.widths, self.heights = zip(*sizes)

    def validate(self, model, syms: SymbolsTable, fixed_input_height: int) -> list[str]:
        """Validate input dataset.

        Args:
            model : Laia model.
            syms (SymbolsTable): Symbols known.
            fixed_input_height (int): When set, all images must have this exact height.

        Returns:
            list[str]: List of errors found in the dataset.
        """
        errors: list[str] = []
        # Check if images have variable height
        if fixed_input_height > 0 and not self.is_fixed_height:
            errors.append(
                f"Found images with variable heights: {self.get_invalid_images_height(fixed_input_height)}."
            )

        # Check if characters are in syms
        missing_symbols = syms.check_symbols(self.character_set)
        if missing_symbols:
            errors.append(f"Found some unknown symbols: {missing_symbols}")

        # Check if images are too small
        min_valid_width = model.get_min_valid_image_size(self.max_width)
        if self.min_width < min_valid_width:
            errors.append(
                f"Found some images too small for convolutions (width<{min_valid_width}). They will be padded during training."
            )

        return errors

    @cached_property
    def character_set(self) -> set[str]:
        """
        Get the set of characters
        """
        return set([char for line in self.labels for char in line])

    @cached_property
    def min_width(self) -> int:
        """
        Compute the minimum width of images
        """
        return min(self.widths)

    @cached_property
    def max_width(self) -> int:
        """
        Compute the maximum width of images
        """
        return max(self.widths)

    @cached_property
    def min_height(self) -> bool:
        """
        Compute the minimum height of images
        """
        return min(self.heights)

    @cached_property
    def max_height(self) -> bool:
        """
        Compute the maximum height of images
        """
        return max(self.heights)

    @cached_property
    def is_fixed_height(self) -> bool:
        """
        Check if all images have the same height
        """
        return self.max_height == self.min_height

    def get_invalid_images_height(self, expected_height: int) -> List[str]:
        """
        List images with invalid height
        """
        return [
            filename
            for filename, height in zip(self.filenames, self.heights)
            if height != expected_height
        ]
