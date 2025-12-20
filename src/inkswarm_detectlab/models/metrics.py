from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import numpy as np


@dataclass(frozen=True)
class ThresholdResult:
    threshold: float
    fpr: float
    recall: float
    precision: float


def choose_threshold_for_fpr(y_true: np.ndarray, scores: np.ndarray, target_fpr: float) -> ThresholdResult:
    """Choose a score threshold that achieves FPR <= target_fpr and is as close as possible to it.

    Deterministic: iterates unique thresholds in descending score order.
    """
    y = y_true.astype(int)
    s = scores.astype(float)

    neg = (y == 0)
    pos = (y == 1)
    n_neg = int(neg.sum())
    n_pos = int(pos.sum())

    if n_neg == 0:
        # degenerate: no negatives, allow threshold=+inf (predict none) for safety.
        return ThresholdResult(threshold=float("inf"), fpr=0.0, recall=0.0, precision=0.0)

    # Candidate thresholds = unique scores (descending)
    uniq = np.unique(s)
    uniq = uniq[::-1]  # descending

    best: ThresholdResult | None = None

    for thr in uniq:
        preds = (s >= thr)
        fp = int((preds & neg).sum())
        tp = int((preds & pos).sum())
        fpr = fp / n_neg if n_neg else 0.0
        if fpr <= target_fpr + 1e-12:
            recall = tp / n_pos if n_pos else 0.0
            precision = (tp / int(preds.sum())) if int(preds.sum()) else 0.0
            cand = ThresholdResult(threshold=float(thr), fpr=float(fpr), recall=float(recall), precision=float(precision))
            if best is None or cand.fpr > best.fpr + 1e-12:
                best = cand

    if best is not None:
        return best

    # If no threshold can satisfy target (e.g., one score ties), use +inf -> predict none.
    return ThresholdResult(threshold=float("inf"), fpr=0.0, recall=0.0, precision=0.0)


def top_thresholds_for_fpr(
    y_true: np.ndarray,
    scores: np.ndarray,
    target_fpr: float,
    *,
    k: int = 3,
) -> list[ThresholdResult]:
    """Return up to k candidate thresholds satisfying FPR<=target, ranked by recall.

    Deterministic: operates over unique score thresholds.

    Ranking (descending): recall, fpr, precision.
    """
    y = y_true.astype(int)
    s = scores.astype(float)

    neg = (y == 0)
    pos = (y == 1)
    n_neg = int(neg.sum())
    n_pos = int(pos.sum())

    if n_neg == 0:
        return [ThresholdResult(threshold=float("inf"), fpr=0.0, recall=0.0, precision=0.0)]

    uniq = np.unique(s)[::-1]
    cands: list[ThresholdResult] = []
    for thr in uniq:
        preds = (s >= thr)
        fp = int((preds & neg).sum())
        tp = int((preds & pos).sum())
        fpr = fp / n_neg if n_neg else 0.0
        if fpr <= target_fpr + 1e-12:
            recall = tp / n_pos if n_pos else 0.0
            precision = (tp / int(preds.sum())) if int(preds.sum()) else 0.0
            cands.append(ThresholdResult(threshold=float(thr), fpr=float(fpr), recall=float(recall), precision=float(precision)))

    cands.sort(key=lambda r: (r.recall, r.fpr, r.precision), reverse=True)
    return cands[: max(1, int(k))]
