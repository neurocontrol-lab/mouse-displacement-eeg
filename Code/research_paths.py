"""Resolve experiment code/results from Code/experiments.json, independent of cwd."""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS = json.loads((ROOT / "Code" / "experiments.json").read_text())


def result_path(experiment_id):
    return ROOT / EXPERIMENTS[experiment_id]["result"]


def code_path(experiment_id):
    return ROOT / EXPERIMENTS[experiment_id]["code"]
