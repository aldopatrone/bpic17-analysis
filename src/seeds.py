# Central place for the random seed used across the analysis.

from __future__ import annotations

import random

import numpy as np

RANDOM_SEED: int = 42


def set_all_seeds(seed: int = RANDOM_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import sklearn.utils
        sklearn.utils.check_random_state(seed)
    except ImportError:
        pass
