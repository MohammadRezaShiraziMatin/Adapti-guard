"""TF-IDF + logistic regression ML detector baseline."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from baselines.base import BaselineDecision, BaselineMethod
from baselines.regex_baseline import RegexBaseline

logger = logging.getLogger(__name__)


class TfidfMLBaseline(BaselineMethod):
    name = "tfidf_ml"

    def __init__(self, benchmark_dir: str = "datasets/benchmark_q1"):
        self._clf = None
        self._vectorizer = None
        self._fallback = RegexBaseline()
        self._train(benchmark_dir)

    def _train(self, benchmark_dir: str) -> None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
        except ImportError:
            logger.warning("sklearn unavailable; TF-IDF baseline uses regex fallback")
            return

        texts: list[str] = []
        labels: list[int] = []
        train_path = Path(benchmark_dir) / "train.jsonl"
        if not train_path.exists():
            train_path = Path("datasets/benchmark_v2/train.jsonl")
        if not train_path.exists():
            return

        with train_path.open(encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                texts.append(str(row.get("prompt", "")))
                labels.append(1 if row.get("label") == "attack" else 0)

        if len(set(labels)) < 2 or len(texts) < 50:
            return

        self._vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        X = self._vectorizer.fit_transform(texts)
        self._clf = LogisticRegression(max_iter=500, random_state=42)
        self._clf.fit(X, labels)
        logger.info("TF-IDF ML baseline trained on %d samples", len(texts))

    def evaluate(self, prompt: str, context: str | None = None) -> BaselineDecision:
        if self._clf is None or self._vectorizer is None:
            d = self._fallback.evaluate(prompt, context)
            d.method = self.name
            d.metadata["fallback"] = "regex"
            return d

        text = f"{context}\n\n{prompt}" if context else prompt
        X = self._vectorizer.transform([text])
        proba = float(self._clf.predict_proba(X)[0][1])
        blocked = proba >= 0.5
        return BaselineDecision(
            method=self.name,
            allowed=not blocked,
            action="A3" if blocked else "A0",
            sanitized_prompt="" if blocked else prompt,
            score=proba,
            blocked=blocked,
        )
