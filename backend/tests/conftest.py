from pathlib import Path
import sys

# 确保在不同执行目录下都能 import app
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
