"""
By-domain re-exports for backward compat with the legacy
`dagster.assets.{law,medicine}.{nation}` paths.

The legacy 7 `law/{nation}/__init__.py` + 7 `medicine/{nation}/__init__.py`
files are preserved for one release (until the next major version
bumps). All legacy paths re-export the new by_domain/ assets.

Per the v3 consolidation plan (consolidate-cianfhoghlaim-subdirs
Phase B.6).

Migration map:
  law_england_legislation  ←  by_domain.law.law_england_legislation
  law_scotland_legislation  ←  by_domain.law.law_scotland_legislation
  law_wales_legislation  ←  by_domain.law.law_wales_legislation
  law_northern_ireland_legislation  ←  by_domain.law.law_northern_ireland_legislation
  law_isle_of_man_legislation  ←  by_domain.law.law_isle_of_man_legislation
  law_jersey_legislation  ←  by_domain.law.law_jersey_legislation
  law_guernsey_legislation  ←  by_domain.law.law_guernsey_legislation

  medicine_england_nhs_england  ←  by_domain.medicine.medicine_england_nhs_england
  medicine_england_gmc  ←  by_domain.medicine.medicine_england_gmc
  medicine_england_nice  ←  by_domain.medicine.medicine_england_nice
  medicine_scotland_nhs_scotland  ←  by_domain.medicine.medicine_scotland_nhs_scotland
  medicine_wales_nhs_wales  ←  by_domain.medicine.medicine_wales_nhs_wales
  medicine_northern_ireland_nidirect  ←  by_domain.medicine.medicine_northern_ireland_nidirect
  medicine_isle_of_man_health_social_care  ←  by_domain.medicine.medicine_isle_of_man_health_social_care
  medicine_jersey_health_community_services  ←  by_domain.medicine.medicine_jersey_health_community_services
  medicine_guernsey_health_social_care  ←  by_domain.medicine.medicine_guernsey_health_social_care
"""
from .law import (
    law_england_legislation,
    law_scotland_legislation,
    law_wales_legislation,
    law_northern_ireland_legislation,
    law_isle_of_man_legislation,
    law_jersey_legislation,
    law_guernsey_legislation,
)
from .medicine import (
    medicine_england_nhs_england,
    medicine_england_gmc,
    medicine_england_nice,
    medicine_scotland_nhs_scotland,
    medicine_wales_nhs_wales,
    medicine_northern_ireland_nidirect,
    medicine_isle_of_man_health_social_care,
    medicine_jersey_health_community_services,
    medicine_guernsey_health_social_care,
)