#!/usr/bin/env python3
"""Fail closed until the documented full release gates are implemented.

Inventory counts and condition-vector uniqueness are not runtime coverage.
This checkpoint must not publish a VERIFIED artifact.
"""
import sys

BLOCKERS = (
    "83 graphs and 268 causes are structurally migrated; field contracts and numeric-node execution remain incomplete",
    "Scenario validator checks row uniqueness, not engine outcomes or distinct paths",
    "Scope and evidence guards pass synthetic tests; full model/P0/terminal coverage remains unverified",
    "OEM images are preserved locally; evidence linkage and runtime viewer verification remain incomplete",
    "STUDY lessons, manual search, history and parts workflows are incomplete",
    "P0 validator checks tokens rather than all eight executable case contracts",
    "Runtime tests lack double-tap assertions and rendered pinch/pan verification",
    "APK builds, full runtime evidence and remote SHA identity are unverified",
)

for blocker in BLOCKERS:
    print("RELEASE_BLOCKED:", blocker)
print("NOT VERIFIED: this is an incomplete development checkpoint.")
sys.exit(1)
