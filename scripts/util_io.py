import os, json, hashlib, pathlib
from typing import Any, Dict
import yaml

def atomic_write(path: str, data: bytes):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, p)

def write_yaml(path: str, obj: Any):
    s = yaml.safe_dump(obj, sort_keys=True, allow_unicode=False)
    if not s.endswith("\n"):
        s += "\n"
    atomic_write(path, s.encode("utf-8"))

def read_yaml(path: str) -> Any:
    return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))

def sha256_of_json(obj: Dict) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
