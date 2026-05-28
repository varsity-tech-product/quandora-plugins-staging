import os
import stat
from pathlib import Path
from typing import Mapping


DEFAULT_HOME = Path.home() / ".factor-mining-agent"
HOME_ENV = "FACTOR_MINING_AGENT_HOME"


def agent_home(home: str | Path | None = None, env: Mapping[str, str] | None = None) -> Path:
    if home is not None:
        return Path(home).expanduser()
    env = env if env is not None else os.environ
    if env.get(HOME_ENV):
        return Path(env[HOME_ENV]).expanduser()
    return DEFAULT_HOME


def ensure_agent_home(home: str | Path | None = None) -> Path:
    root = agent_home(home)
    root.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(root, stat.S_IRWXU)
    except OSError:
        pass
    return root
