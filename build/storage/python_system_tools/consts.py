import os.path
from pathlib import Path

# paths on master machine
HOME_PATH = Path.home()
WORKSPACE_PATH = os.path.join(HOME_PATH, "IPDK_workspace")
SHARE_DIR_PATH = os.path.join(WORKSPACE_PATH, "SHARE")
SCRIPTS_PATH = os.path.join(WORKSPACE_PATH, "ipdk/build/storage/scripts")
