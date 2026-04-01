"""Tests for sacct Start/End / Elapsed / ElapsedRaw parsing and runtime refinement."""

from unittest.mock import MagicMock, patch

import pytest

from harness.runner import RunResult
from harness.slurm_elapsed import (
    _parse_elapsed_string,
    _parse_sacct_elapsedraw_output,
    _parse_sacct_start_end_output,
    fetch_slurm_elapsed_seconds,
    parse_harness_solver_wall_seconds,
    refine_run_result_runtime_from_slurm,
)


def _proc_out(s: str) -> MagicMock:
    m = MagicMock()
    m.stdout = s
    return m


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "2026-03-31T10:00:00|2026-03-31T10:01:00.500",
            60.5,
        ),
        (
            "24|2026-03-31T10:00:00|2026-03-31T10:01:01",
            61.0,
        ),
        ("Unknown|2026-03-31T10:01:00", None),
        ("", None),
    ],
)
def test_parse_sacct_start_end_output(text, expected):
    assert _parse_sacct_start_end_output(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("60", 60.0),
        ("60.5", 60.5),
        ("23|60\n", 60.0),
        ("23.batch|45\n23|45\n", 45.0),
        ("", None),
        ("N/A\n", None),
    ],
)
def test_parse_sacct_elapsedraw_output(text, expected):
    assert _parse_sacct_elapsedraw_output(text) == expected


@pytest.mark.parametrize(
    "s,expected",
    [
        ("00:01:00", 60.0),
        ("01:00:00", 3600.0),
        ("1-00:00:00", 86400.0),
        ("00:00:30.5", 30.5),
        ("", None),
        ("N/A", None),
    ],
)
def test_parse_elapsed_string(s, expected):
    assert _parse_elapsed_string(s) == expected


@patch("harness.slurm_elapsed.subprocess.run")
def test_fetch_slurm_elapsed_seconds_docker_prefers_start_end(mock_run):
    mock_run.side_effect = [
        _proc_out("2026-03-31T12:00:00|2026-03-31T12:01:00.250\n"),
    ]
    el = fetch_slurm_elapsed_seconds(["23"], "my-slurm-ct")
    assert el == 60.25
    assert mock_run.call_count == 1
    args, _kw = mock_run.call_args
    assert list(args[0][:3]) == ["docker", "exec", "my-slurm-ct"]
    assert "Start,End" in str(args[0][-1])


@patch("harness.slurm_elapsed.subprocess.run")
def test_fetch_slurm_elapsed_seconds_falls_back_elapsed_then_raw(mock_run):
    mock_run.side_effect = [
        _proc_out("Unknown|Unknown\n"),
        _proc_out("00:01:00.125\n"),
    ]
    el = fetch_slurm_elapsed_seconds(["23"], "host")
    assert el == pytest.approx(60.125)
    assert mock_run.call_count == 2


@patch("harness.slurm_elapsed.subprocess.run")
def test_fetch_slurm_elapsed_seconds_falls_back_elapsedraw(mock_run):
    mock_run.side_effect = [
        _proc_out(""),
        _proc_out("N/A\n"),
        _proc_out("61\n"),
    ]
    el = fetch_slurm_elapsed_seconds(["23"], "host")
    assert el == 61.0
    assert mock_run.call_count == 3


@patch("harness.slurm_elapsed.subprocess.run")
def test_fetch_slurm_elapsed_seconds_host_start_end(mock_run):
    mock_run.side_effect = [
        _proc_out("2026-03-31T12:00:00|2026-03-31T12:00:30\n"),
    ]
    el = fetch_slurm_elapsed_seconds(["23"], "host")
    assert el == 30.0
    args, _kw = mock_run.call_args
    assert args[0][0] == "bash"


@patch("harness.slurm_elapsed.fetch_slurm_elapsed_seconds", return_value=60.0)
def test_refine_run_result_runtime_from_slurm(mock_fetch):
    r = RunResult(
        job_name="s@sys",
        solver_name="s",
        system_name="sys",
        returncode=0,
        stdout="HARNESS_SLURM_JOB_ID=23\n",
        stderr="",
        runtime_seconds=62.5,
        timestamp="",
        passed=True,
        metrics={"runtime_seconds": 62.5},
        scheduler_backend="slurm",
        scheduler_job_ids=["23"],
        submit_container="c1",
    )
    refine_run_result_runtime_from_slurm(r)
    assert r.runtime_seconds == 60.0
    assert r.metrics["runtime_seconds"] == 60.0
    mock_fetch.assert_called_once_with(["23"], "c1")


def test_refine_queries_sacct_when_backend_empty_but_job_ids_present():
    """Merging may leave backend blank in tests; ids still imply Slurm."""
    r = RunResult(
        job_name="x",
        solver_name="x",
        system_name="y",
        returncode=0,
        stdout="",
        stderr="",
        runtime_seconds=1.0,
        timestamp="",
        metrics={"runtime_seconds": 1.0},
        scheduler_backend="",
        scheduler_job_ids=["23"],
    )
    with patch("harness.slurm_elapsed.fetch_slurm_elapsed_seconds", return_value=55.0) as mock_fetch:
        refine_run_result_runtime_from_slurm(r)
    mock_fetch.assert_called_once_with(["23"], "")
    assert r.runtime_seconds == 55.0


def test_refine_skips_when_no_job_ids():
    r = RunResult(
        job_name="x",
        solver_name="x",
        system_name="y",
        returncode=0,
        stdout="",
        stderr="",
        runtime_seconds=1.0,
        timestamp="",
        metrics={"runtime_seconds": 1.0},
        scheduler_backend="slurm",
        scheduler_job_ids=[],
    )
    with patch("harness.slurm_elapsed.fetch_slurm_elapsed_seconds") as mock_fetch:
        refine_run_result_runtime_from_slurm(r)
    mock_fetch.assert_not_called()


def test_refine_skips_non_slurm_backend():
    r = RunResult(
        job_name="x",
        solver_name="x",
        system_name="y",
        returncode=0,
        stdout="",
        stderr="",
        runtime_seconds=1.0,
        timestamp="",
        metrics={"runtime_seconds": 1.0},
        scheduler_backend="local",
        scheduler_job_ids=["23"],
    )
    with patch("harness.slurm_elapsed.fetch_slurm_elapsed_seconds") as mock_fetch:
        refine_run_result_runtime_from_slurm(r)
    mock_fetch.assert_not_called()


@pytest.mark.parametrize(
    "out,err,expected",
    [
        ("HARNESS_SOLVER_WALL_SECONDS=60.041\n", "", 60.041),
        ("x\nHARNESS_SOLVER_WALL_SECONDS=1.5\n", "", 1.5),
        ("", "HARNESS_SOLVER_WALL_SECONDS=2.25", 2.25),
        ("HARNESS_SOLVER_WALL_SECONDS=-1\n", "", None),
        ("HARNESS_SOLVER_WALL_SECONDS=nan\n", "", None),
        ("no line", "", None),
    ],
)
def test_parse_harness_solver_wall_seconds(out, err, expected):
    assert parse_harness_solver_wall_seconds(out, err) == expected


def test_refine_prefers_harness_solver_wall_skips_sacct():
    r = RunResult(
        job_name="slurm-sleep-60@sys",
        solver_name="slurm-sleep-60",
        system_name="sys",
        returncode=0,
        stdout=(
            "HARNESS_SLURM_JOB_ID=24\n"
            "--- slurm-24.out ---\n"
            "HARNESS_SOLVER_WALL_SECONDS=60.041\n"
        ),
        stderr="",
        runtime_seconds=62.0,
        timestamp="",
        passed=True,
        metrics={"runtime_seconds": 62.0},
        scheduler_backend="slurm",
        scheduler_job_ids=["24"],
        submit_container="c1",
    )
    with patch("harness.slurm_elapsed.fetch_slurm_elapsed_seconds") as mock_fetch:
        refine_run_result_runtime_from_slurm(r)
    mock_fetch.assert_not_called()
    assert r.runtime_seconds == 60.041
    assert r.metrics["runtime_seconds"] == 60.041


def test_refine_applies_harness_wall_for_local_without_slurm_ids():
    """dev-system subprocess solvers can emit HARNESS_SOLVER_WALL_SECONDS like Slurm batch scripts."""
    r = RunResult(
        job_name="local-sleep-60@dev-system",
        solver_name="local-sleep-60",
        system_name="dev-system",
        returncode=0,
        stdout=(
            "local-sleep-60: starting sleep for 1s\n"
            "HARNESS_SOLVER_WALL_SECONDS=1.002\n"
            "local-sleep-60: finished\n"
        ),
        stderr="",
        runtime_seconds=1.5,
        timestamp="",
        passed=True,
        metrics={"runtime_seconds": 1.5},
        scheduler_backend="",
        scheduler_job_ids=[],
    )
    with patch("harness.slurm_elapsed.fetch_slurm_elapsed_seconds") as mock_fetch:
        refine_run_result_runtime_from_slurm(r)
    mock_fetch.assert_not_called()
    assert r.runtime_seconds == 1.002
    assert r.metrics["runtime_seconds"] == 1.002
