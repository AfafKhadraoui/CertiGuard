from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest

from certiguard.layers.storage import read_json, secure_write_json


class BehaviorDetector:
    def __init__(self, model_seed: int = 42, baseline_state_path: Path | None = None) -> None:
        self.model = IsolationForest(contamination=0.05, random_state=model_seed)
        self.fitted = False
        self.baseline_state_path = baseline_state_path
        self._state = read_json(baseline_state_path) if baseline_state_path else {}

    def fit_synthetic_baseline(self) -> None:
        rng = np.random.default_rng(42)
        active_users = rng.normal(loc=35, scale=8, size=2000).clip(1, 50)
        hour = rng.integers(8, 19, size=2000)
        machines = rng.normal(loc=3, scale=1, size=2000).clip(1, 6)
        api_rate = rng.normal(loc=40, scale=12, size=2000).clip(1, 140)
        X = np.column_stack([active_users, hour, machines, api_rate])
        self.model.fit(X)
        self.fitted = True

    def score(self, features: list[float]) -> tuple[bool, float]:
        if not self.fitted:
            self.fit_synthetic_baseline()
        X = np.array([features], dtype=float)
        prediction = self.model.predict(X)[0]
        score = float(self.model.score_samples(X)[0])
        return bool(prediction == -1), float(score)

    def update_customer_baseline(self, features: list[float], learning_days: int = 30) -> dict:
        sessions = int(self._state.get("sessions", 0)) + 1
        sum_vec = np.array(self._state.get("sum_vec", [0.0, 0.0, 0.0, 0.0]), dtype=float) + np.array(features, dtype=float)
        mean_vec = (sum_vec / sessions).tolist()
        self._state.update(
            {
                "sessions": sessions,
                "sum_vec": sum_vec.tolist(),
                "mean_vec": mean_vec,
                "learning_complete": sessions >= learning_days,
            }
        )
        if self.baseline_state_path:
            secure_write_json(self.baseline_state_path, self._state)
        return self._state

    def detect_drift(self, features: list[float], threshold: float = 2.5) -> tuple[bool, float]:
        mean_vec = self._state.get("mean_vec")
        if not mean_vec:
            return False, 0.0
        diff = np.linalg.norm(np.array(features, dtype=float) - np.array(mean_vec, dtype=float))
        return bool(diff > threshold), float(diff)

