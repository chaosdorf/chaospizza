# pylint: disable=E1101
# for pathlib, see https://github.com/PyCQA/pylint/issues/1660
"""
Tests for util/docker.py

This is currently just Docker's secrets mechanism.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from util import docker


class TestDockerSecrets:
    """Test the secret method."""
    secrets_dir = secrets_path = None
    secret_name = "TEST_SECRET"
    secret_value = "very secret key"

    def setup_method(self, _):
        """Initializa a temporary directory."""
        self.secrets_dir = TemporaryDirectory()  # pylint: disable=R1732
        self.secrets_path = Path(self.secrets_dir.name)
        (  # noqa
            self.secrets_path / self.secret_name
        ).write_text(f"{self.secret_value}\n")

    def teardown_method(self, _):
        """Delete the temporary directory."""
        self.secrets_dir.cleanup()

    def test_can_read_existing_secret(self):
        """Test whether we can actually read the file."""
        assert self.secret_value in docker.secret(
            self.secret_name, self.secrets_path
        )

    def test_strips_secret(self):
        """Test whether a trailing newline is being removed."""
        assert docker.secret(
            self.secret_name, self.secrets_path
        ) == self.secret_value

    def test_nonexisting_secret(self):
        """Test whether reading a non-existing secret returns None."""
        assert docker.secret("NONEXISTING", self.secrets_path) is None
