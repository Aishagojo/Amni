import pytest
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from app.core.config import ENV_FILE, Settings


def test_password_is_encoded_and_hidden_in_display():
    password = "example@:/password"
    settings = Settings(_env_file=None, postgres_password=password)
    assert make_url(settings.database_url.render_as_string(hide_password=False)).password == password
    assert password not in str(settings.database_url)
    assert password not in repr(settings)
    assert ENV_FILE.name == ".env"
    assert ENV_FILE.parent.name == "amni"


@pytest.mark.parametrize("port", [0, -1, 65536])
def test_invalid_port_is_rejected(port):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, postgres_password="example", postgres_port=port)


def test_empty_password_is_rejected_without_input_values():
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, postgres_password="")
    assert "input_value" not in str(error.value)
