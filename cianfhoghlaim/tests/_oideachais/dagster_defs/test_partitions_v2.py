"""Test `oideachais/dagster_defs/partitions_v2.py` partition definitions.

The 4-cycle simplified partition scheme replaced the 208-partition
explosion. This test guards against accidental re-introduction of the
old ncca_multipartitions.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def test_ireland_curriculum_partitions_has_4_keys() -> None:
    from cianfhoghlaim.dagster.partitions_v2 import ireland_curriculum_partitions

    keys = list(ireland_curriculum_partitions.get_partition_keys())
    assert keys == ["early_childhood", "primary", "junior_cycle", "senior_cycle"]


def test_ireland_curriculum_with_language_has_8_keys() -> None:
    from cianfhoghlaim.dagster.partitions_v2 import ireland_curriculum_with_language

    keys = list(ireland_curriculum_with_language.get_partition_keys())
    # 4 cycles × 2 languages = 8
    assert len(keys) == 8
    assert {"junior_cycle|en", "senior_cycle|ga"}.issubset(set(keys))
