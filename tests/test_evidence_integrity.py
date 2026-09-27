import hashlib, json
from pathlib import Path

def test_p1_sha():
    root = Path(__file__).resolve().parents[1]
    m = json.loads((root / "datasets/frozen/p1_mechanism_v1.0.0/manifest.json").read_text())
    exp = m["dataset_sha256"]
    h = hashlib.sha256((root / "datasets/frozen/p1_mechanism_v1.0.0/dataset.jsonl").read_bytes()).hexdigest()
    assert h == exp
