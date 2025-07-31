import warnings
import pytest

@pytest.fixture(autouse=True)
def suppress_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="unidecode")
    warnings.filterwarnings("ignore")
    yield
