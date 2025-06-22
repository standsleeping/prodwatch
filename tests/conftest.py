import sys
from pathlib import Path

from .fixtures import *  # noqa: F403

# Add the src directory to the path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
