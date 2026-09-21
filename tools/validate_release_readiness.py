#!/usr/bin/env python3
"""Fail closed until the documented full release gates are implemented.

Inventory counts and condition-vector uniqueness are not runtime coverage.
This checkpoint must not publish a VERIFIED artifact.
"""
import sys

BLOCKERS = (
    "Legacy graphs/causes are archived, not migrated into executable V20 flows",
    "Scenario validator checks row uniqueness, not engine outcomes or distinct paths",
    "Exact vehicle scope and evidence are not enforced by DiagnosticEngine",
    "OEM evidence images and supporting registries are absent from the new runtime",
    "STUDY lessons, manual search, history and parts workflows are incomplete",
    "P0 validator checks tokens rather than all eight executable case contracts",
    "Runtime tests lack double-tap assertions and rendered pinch/pan verification",
    "APK builds, full runtime evidence and remote SHA identity are unverified",
)

for blocker in BLOCKERS:
    print("RELEASE_BLOCKED:", blocker)
print("NOT VERIFIED: this is an incomplete development checkpoint.")
sys.exit(1)
