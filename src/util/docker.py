"""
Integration with Docker (and Compose and Swarm).

Here is currently just a method for getting secrets.
"""

from pathlib import Path
from typing import Optional


def secret(
        name: str, secrets_dir: Path = Path("/run/secrets")
) -> Optional[str]:
    """Load the named secret from /run/secrets and return None otherwise."""
    path = secrets_dir / name
    if path.exists():
        return path.read_text().strip()
    return None
