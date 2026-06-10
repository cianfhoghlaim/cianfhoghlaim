from laia import *


def test_wildcard_import():
    # these are defined in __all__
    assert __version__
    assert __root__
    assert get_installed_versions
