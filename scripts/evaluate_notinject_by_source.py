import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector

DATA = ROOT / "dataset/raw/NotInject/datasets/valid.json"

with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

detector = PromptInjectionDetector()
groups = defaultdict(list)

for row in data:
    groups[row.get("source", "UNKNOWN")].append(row)

print("=" * 90)
print("NOTINJECT VALIDATION — SOURCE-WISE EVALUATION")
print("=" * 90)

for source in sorted(groups):
    tp = tn = fp = fn = 0

    for row in groups[source]:
        y = int(row["label"])
        pred = int(detector.detect(row["prompt"]).is_injection)

        if y == 1 and pred == 1:
            tp += 1
        elif y == 0 and pred == 0:
            tn += 1
        elif y == 0 and pred == 1:
            fp += 1
        else:
            fn += 1

    n = tp + tn + fp + fn

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )
    specificity = tn / (tn + fp) if tn + fp else 0.0
    balanced_accuracy = (recall + specificity) / 2

    print()
    print(f"SOURCE: {source}")
    print(f"Samples:              {n}")
    print(f"TP:                   {tp}")
    print(f"TN:                   {tn}")
    print(f"FP:                   {fp}")
    print(f"FN:                   {fn}")
    print(f"Precision:            {precision:.4f}")
    print(f"Recall:               {recall:.4f}")
    print(f"F1:                   {f1:.4f}")
    print(f"Balanced Accuracy:    {balanced_accuracy:.4f}")
    print(f"FPR:                  {fp/(fp+tn) if fp+tn else 0:.4f}")
    print(f"FNR:                  {fn/(fn+tp) if fn+tp else 0:.4f}")

print()
print("=" * 90)
print("DONE")
print("=" * 90)
