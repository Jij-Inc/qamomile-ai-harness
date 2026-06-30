from __future__ import annotations

from pathlib import Path

from qamomile_ai_harness.dataset import summarize_dataset


if __name__ == "__main__":
    summarize_dataset(
        Path("data/raw/qcoder_benchmark/QCoder_Benchmark.jsonl"),
        Path("data/processed/qcoder_benchmark"),
    )
