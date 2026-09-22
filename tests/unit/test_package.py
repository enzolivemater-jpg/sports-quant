from sports_quant import __version__


def test_package_version_is_foundation_dev_version() -> None:
    assert __version__ == "0.1.0.dev1"
