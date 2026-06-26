"""
Shared helpers split from celtic/gaois.py

Phase 3D of openspec change.
"""

from __future__ import annotations
import re
from collections.abc import Iterator
import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource
from observability.logging import get_logger
try:
    from shared.http import ainm_client, logainm_client, tearma_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


LOGAINM_COUNTIES = {
    "an-cabhán": 100001,
    "cavan": 100001,
    "dún-na-ngall": 100002,
    "donegal": 100002,
    "muineachán": 100003,
    "monaghan": 100003,
    "connacht": 100004,
    "gaillimh": 100005,
    "galway": 100005,
    "liatroim": 100006,
    "leitrim": 100006,
    "maigh-eo": 100007,
    "mayo": 100007,
    "ros-comáin": 100008,
    "roscommon": 100008,
    "sligeach": 100009,
    "sligo": 100009,
    "laighin": 100010,
    "leinster": 100010,
    "ceatharlach": 100011,
    "carlow": 100011,
    "baile-átha-cliath": 100012,
    "dublin": 100012,
    "cill-dara": 100013,
    "kildare": 100013,
    "cill-chainnigh": 100014,
    "kilkenny": 100014,
    "laois": 100015,
    "an-longfort": 100016,
    "longford": 100016,
    "an-lú": 100017,
    "louth": 100017,
    "an-mhí": 100018,
    "meath": 100018,
    "uíbh-fhailí": 100019,
    "offaly": 100019,
    "iarmhí": 100020,
    "westmeath": 100020,
    "loch-garman": 100021,
    "wexford": 100021,
    "cill-mhantáin": 100022,
    "wicklow": 100022,
    "mumha": 100023,
    "munster": 100023,
    "an-clár": 100024,
    "clare": 100024,
    "corcaigh": 100025,
    "cork": 100025,
    "ciarraí": 100026,
    "kerry": 100026,
    "luimneach": 100027,
    "limerick": 100027,
    "tiobraid-árann": 100028,
    "tipperary": 100028,
    "port-láirge": 100029,
    "waterford": 100029,
    "ulster-roi": 100030,
    "aontroim": 100031,
    "antrim": 100031,
    "ard-mhacha": 100032,
    "armagh": 100032,
    "an-dún": 100033,
    "down": 100033,
    "fear-manach": 100034,
    "fermanagh": 100034,
    "doire": 100035,
    "derry": 100035,
    "tír-eoghain": 100036,
    "tyrone": 100036,
}

def _get_ainm_factory():
    """Get HTTP client factory for Ainm.ie."""
    return ainm_client()

def _get_logainm_factory():
    """Get HTTP client factory for Logainm.ie API."""
    return logainm_client()

def _get_tearma_factory():
    """Get HTTP client factory for Téarma.ie."""
    return tearma_client()
