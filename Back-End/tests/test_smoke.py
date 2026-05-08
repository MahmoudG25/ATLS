import pytest

@pytest.mark.django_db
def test_django_boot_and_urls():
    """
    Smoke test to ensure the Django application boots,
    settings are loaded, and the database connects.
    """
    from apps.users.models import User
    
    # DB should be clean for tests
    assert User.objects.count() == 0

def test_imports():
    """
    Smoke test to ensure critical configurations are importable
    and no circular dependencies prevent startup.
    """
    from core import settings
    assert settings.INSTALLED_APPS is not None
    assert 'rest_framework' in settings.INSTALLED_APPS
