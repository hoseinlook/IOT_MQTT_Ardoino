from pathlib import Path

ROOT_PATH = Path(__file__).parent
STORAGE_PATH = ROOT_PATH.joinpath('storage')
if not STORAGE_PATH.exists():
    STORAGE_PATH.mkdir()

CENTRAL_SERVER_PATH = STORAGE_PATH.joinpath('central')
if not CENTRAL_SERVER_PATH.exists():
    CENTRAL_SERVER_PATH.mkdir()

LOCAL_SERVER_PATH = STORAGE_PATH.joinpath('local')
if not LOCAL_SERVER_PATH.exists():
    LOCAL_SERVER_PATH.mkdir()

LOCAL_SERVER_API_KEY = "qwertyuiopsdfghjklxcvbnm"

CENTRAL_SERVER_HOST = '0.0.0.0'
CENTRAL_SERVER_PORT = 5000

LOCAL_SERVER_HOST = '0.0.0.0'
LOCAL_SERVER_PORT = 5001
