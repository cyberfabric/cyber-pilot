from unittest.mock import patch


def test_package_main_is_lazy_import_wrapper():
    # Ensure skills.cypilot.scripts.cypilot.main calls through to cli.main
    # without importing cli at package import time.
    from skills.cypilot.scripts import cypilot

    with patch("skills.cypilot.scripts.cypilot.cli.main", return_value=0) as m:
        assert cypilot.main(["validate", "--skip-code"]) == 0
        m.assert_called_once()
