from sruth.oideachais.data_platform.dagster_defs.assets.ireland.curriculum_dlt_assets import (
    CYCLE_PARTITIONS,
)

jc_partitions = CYCLE_PARTITIONS["junior_cycle"]
print(jc_partitions.get_partition_keys()[:10])
