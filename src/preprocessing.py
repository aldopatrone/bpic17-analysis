# Pre-processing filters for the BPIC-17 event log, shared by all notebooks.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

CASE_COL = "case:concept:name"
ACT_COL = "concept:name"
TS_COL = "time:timestamp"
LIFECYCLE_COL = "lifecycle:transition"


@dataclass
class FilterReport:
    cases_before: int
    cases_after: int
    events_before: int
    events_after: int
    variants_before: int
    variants_after: int

    @property
    def cases_dropped(self) -> int:
        return self.cases_before - self.cases_after

    @property
    def events_dropped(self) -> int:
        return self.events_before - self.events_after

    @property
    def variants_dropped(self) -> int:
        return self.variants_before - self.variants_after


def _variant_count(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    return (
        df.sort_values([CASE_COL, TS_COL])
        .groupby(CASE_COL)[ACT_COL]
        .agg(tuple)
        .nunique()
    )

def filter_for_discovery(
    df: pd.DataFrame,
    *,
    lifecycle: Optional[str] = "complete",
    start_buffer_days: int = 14,
    end_buffer_days: int = 14,
) -> tuple[pd.DataFrame, FilterReport]:
    
    # Apply the standard BPIC-17 discovery filters.
    # 1. Lifecycle filter: keep only events with the given lifecycle
    #    transition (default "complete"). BPIC-17 logs several stages
    #    (schedule/start/complete/withdraw); using one keeps discovery on
    #    the business process rather than the work-item state machine.
    # 2. Trace-boundary filter: drop cases starting in the last
    #    end_buffer_days (right-truncated) or ending in the first
    #    start_buffer_days (left-truncated).
    
    cases_before = df[CASE_COL].nunique()
    events_before = len(df)
    variants_before = _variant_count(df)

    work = df
    if lifecycle is not None and LIFECYCLE_COL in work.columns:
        work = work[work[LIFECYCLE_COL] == lifecycle]

    log_start = work[TS_COL].min()
    log_end = work[TS_COL].max()
    case_span = work.groupby(CASE_COL)[TS_COL].agg(["min", "max"])
    cutoff_start = log_start + pd.Timedelta(days=start_buffer_days)
    cutoff_end = log_end - pd.Timedelta(days=end_buffer_days)
    keep_cases = case_span.index[
        (case_span["min"] <= cutoff_end) & (case_span["max"] >= cutoff_start)
    ]
    work = work[work[CASE_COL].isin(keep_cases)].copy()

    report = FilterReport(
        cases_before=cases_before,
        cases_after=work[CASE_COL].nunique(),
        events_before=events_before,
        events_after=len(work),
        variants_before=variants_before,
        variants_after=_variant_count(work),
    )
    return work, report
