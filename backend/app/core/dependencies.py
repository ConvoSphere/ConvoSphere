from .config import get_settings
from .security import security


def get_settings_dep():
    return get_settings()


def get_security_dep():
    return security
