from app.settings import SettingsEnum, get_settings


def test_settings():
    assert get_settings().CONFIG_TYPE == SettingsEnum.TESTING
