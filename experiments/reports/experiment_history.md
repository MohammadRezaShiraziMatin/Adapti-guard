# ADAPTI-GUARD Experiment History

Generated: 2026-08-28T09:50:03.840038+00:00

Historical versions are reconstructed only from available project artifacts.
Unknown results are intentionally not fabricated.

## V1


No recoverable artifact/result is currently available.


**Status:** `UNRECOVERED`

## V2


No recoverable artifact/result is currently available.


**Status:** `UNRECOVERED`

## V3


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v3`
- `src/adapti_guard/detector/prompt_injection_detector.py.v3_backup`


**Status:** `HISTORICAL_ARTIFACT`

## V4


No recoverable artifact/result is currently available.


**Status:** `UNRECOVERED`

## V5


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v5`


**Status:** `HISTORICAL_ARTIFACT`

## V6


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v6`


**Status:** `HISTORICAL_ARTIFACT`

## V7


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v7`
- `src/adapti_guard/detector/prompt_injection_detector.py.v7_baseline`


**Status:** `HISTORICAL_ARTIFACT`

## V8


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v8`


**Status:** `HISTORICAL_ARTIFACT`

## V9


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v9`
- `src/adapti_guard/detector/prompt_injection_detector.py.v9_pre`


**Status:** `HISTORICAL_ARTIFACT`

## V10


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v10_backup`


**Status:** `HISTORICAL_ARTIFACT`

## V11


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v11_backup`


**Status:** `HISTORICAL_ARTIFACT`

**Change:** Contextual multilingual injection detection: instruction reset/override, role reassignment, and forced-output signals.

## V12


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v12_backup`


**Status:** `HISTORICAL_ARTIFACT`

**Change:** Contextual task, role, and prompt-extraction signals with contextual gating.

## V13


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py.v13_backup`
- `src/adapti_guard/detector/prompt_injection_detector.py.v13_backup2`


**Status:** `HISTORICAL_ARTIFACT`

**Change:** Contextual attack detection covering reset/override, role-play, extraction, and output hijacking.

## V14


No recoverable artifact/result is currently available.


**Status:** `UNRECOVERED`

## V15



**Evidence:** `src/adapti_guard/detector/prompt_injection_detector.py`


**Status:** `HISTORICAL_ARTIFACT`

**Change:** Contextual combination scoring for multi-signal attacks.

## V16


**Verified result:**

- Dataset: NotInject
- Split: smoke
- Samples: 1000
- TP: 306
- TN: 510
- FP: 64
- FN: 120
- Precision: 0.827
- Recall: 0.7183
- F1: 0.7688
- Balanced Accuracy: 0.8034
- FPR: 0.1115
- FNR: 0.2817


**Status:** `VERIFIED`

**Change:** Behavioral and structural attack signals.

## V17


**Artifact files:**

- `src/adapti_guard/detector/prompt_injection_detector.py`

**Status:** `VALIDATED_POOR_GENERALIZATION`

**Change:** Precision-oriented contextual gating with corrected regex escaping.

