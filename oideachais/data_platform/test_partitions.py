from dagster_defs.assets.ireland.curriculum_dlt_assets import CYCLE_PARTITIONS
print(CYCLE_PARTITIONS["junior_cycle"].get_partition_keys()[:10])
