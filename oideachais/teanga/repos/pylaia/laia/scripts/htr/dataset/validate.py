#!/usr/bin/env python3
from typing import Any, Dict, List, Optional

import jsonargparse
from jsonargparse.typing import NonNegativeInt

import laia.common.logging as log
from laia.common.arguments import CommonArgs, TrainArgs
from laia.common.loader import ModelLoader
from laia.scripts.htr import common_main
from laia.utils import ImageLabelsStats, Split, Statistics, SymbolsTable


def run(
    syms: str,
    img_dirs: List[str],
    tr_txt_table: str,
    va_txt_table: str,
    te_txt_table: str,
    fixed_input_height: NonNegativeInt,
    statistics_output: str,
    common: CommonArgs = CommonArgs(),
    train: TrainArgs = TrainArgs(),
):
    # Check model
    loader = ModelLoader(
        common.train_path, filename=common.model_filename, device="cpu"
    )
    model = loader.load()
    assert (
        model is not None
    ), "Could not find the model. Have you run pylaia-htr-create-model?"

    # Where all issues will be stored
    dataset_issues = dict()

    # Prepare the symbols
    syms: SymbolsTable = SymbolsTable(syms)
    if missing := syms.check_symbols(train.delimiters):
        dataset_issues["Delimiters"] = [f"Found some unknown symbols: {missing}"]

    mdfile = Statistics(statistics_output)

    for split, table in zip(Split, (tr_txt_table, va_txt_table, te_txt_table)):
        # Check for missing image
        dataset_stats = ImageLabelsStats(
            stage=split.value,
            tables=[table],
            img_dirs=img_dirs,
        )
        dataset_issues[split.value] = dataset_stats.validate(
            model, syms, fixed_input_height
        )

        if not dataset_issues[split.value]:
            # Write markdown section
            mdfile.create_split_section(
                split.value,
                dataset_stats.widths,
                dataset_stats.heights,
                dataset_stats.labels,
                train.delimiters,
            )

    if any(errors for errors in dataset_issues.values()):
        log.error("Issues found in the dataset.")
        # Log all issues
        for source, issues in dataset_issues.items():
            if not issues:
                continue

            for issue in issues:
                log.error(f"{source} - {issue}")
        return

    log.info("Dataset is valid")

    # Write markdown statistics file
    mdfile.document.create_md_file()
    log.info(f"Statistics written to {statistics_output}")


def get_args(argv: Optional[List[str]] = None) -> Dict[str, Any]:
    parser = jsonargparse.ArgumentParser()
    parser.add_argument(
        "--config", action=jsonargparse.ActionConfigFile, help="Configuration file"
    )
    parser.add_argument(
        "syms",
        type=str,
        help=(
            "Mapping from strings to integers. "
            "The CTC symbol must be mapped to integer 0"
        ),
    )
    parser.add_argument(
        "img_dirs",
        type=List[str],
        default=[],
        help="Directories containing segmented line images",
    )
    parser.add_argument(
        "tr_txt_table",
        type=str,
        help="Train labels",
    )
    parser.add_argument(
        "va_txt_table",
        type=str,
        help="Val labels",
    )
    parser.add_argument(
        "te_txt_table",
        type=str,
        help="Test labels",
    )
    parser.add_argument(
        "--fixed_input_height",
        type=NonNegativeInt,
        default=0,
        help=(
            "Height of the input images. If 0, a variable height model "
            "will be used (see `adaptive_pooling`). This will be used to compute the "
            "model output height at the end of the convolutional layers"
        ),
    )
    parser.add_argument(
        "--statistics_output",
        type=str,
        default="statistics.md",
        help="Where the Markdown summary will be written",
    )
    parser.add_class_arguments(CommonArgs, "common")
    parser.add_class_arguments(TrainArgs, "train")
    parser.add_function_arguments(log.config, "logging")

    args = parser.parse_args(argv, with_meta=False).as_dict()
    args["common"] = CommonArgs(**args["common"])
    args["train"] = TrainArgs(**args["train"])
    return args


def main() -> None:
    args = get_args()
    args = common_main(args)
    run(**args)


if __name__ == "__main__":
    main()
