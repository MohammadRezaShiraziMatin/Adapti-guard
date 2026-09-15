import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector

DATA = ROOT / "dataset/raw/NotInject/datasets/valid.json"

with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

detector = PromptInjectionDetector()

tp = tn = fp = fn = 0

for r in data:
    y = int(r["label"])
    pred = int(detector.detect(r["prompt"]).is_injection)

    if y == 1 and pred == 1:
        tp += 1
    elif y == 0 and pred == 0:
        tn += 1
    elif y == 0 and pred == 1:
        fp += 1
    else:
        fn += 1

precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
fpr = fp / (fp + tn) if fp + tn else 0.0
fnr = fn / (fn + tp) if fn + tp else 0.0
specificity = tn / (tn + fp) if tn + fp else 0.0
balanced_accuracy = (recall + specificity) / 2

print("=" * 70)
print("NOTINJECT V17 HELD-OUT VALIDATION")
print("=" * 70)
print(f"Samples:             {len(data):,}")
print(f"TP:                  {tp:,}")
print(f"TN:                  {tn:,}")
print(f"FP:                  {fp:,}")
print(f"FN:                  {fn:,}")
print()
print(f"Precision:           {precision:.4f}")
print(f"Recall:              {recall:.4f}")
print(f"F1:                  {f1:.4f}")
print(f"FPR:                 {fpr:.4f}")
print(f"FNR:                 {fnr:.4f}")
print(f"Balanced Accuracy:   {balanced_accuracy:.4f}")
print("=" * 70)
