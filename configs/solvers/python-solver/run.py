#!/usr/bin/env python3
"""Sample solver with nondeterministic wall time (random sleep)."""
import random
import sys
import time

print("Solver: python-solver")
t0 = time.perf_counter()
time.sleep(random.uniform(0.0, 1.0))
elapsed = time.perf_counter() - t0
# Harness sets metrics["runtime_seconds"] from process wall time; this is only the sleep interval.
print(f"sleep_seconds: {elapsed:.6f}")
print("status: success")
sys.exit(0)
