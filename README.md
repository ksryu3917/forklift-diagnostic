# Forklift Diagnostic Android v0.18 RC Auto

Native Android field test build.

v0.18 release-candidate validation:
- Every reachable individual diagnosis/result is exercised with at least 30 distinct operating-condition scenarios.
- CI rejects broken links, unreachable results, dead ends, placeholders, missing OEM page assets, scenario collisions, and wrong terminal outcomes.
- GitHub Actions builds the `v18-rc-auto` branch and publishes both the debug APK and validation reports.

Changes in v0.2:
- Brand + model display (두산 · D25S-7 style)
- Persistent Home button in top bar
- Removed '정규화 대기' UI: all 64 symptoms / 268 causes are normalized as exact graph, OEM procedure chain, or OEM source/action
- OEM remedies added where explicitly present in troubleshooting tables
- F/R electrical diagnosis gets an app-rendered service schematic based on OEM procedure, with current target highlighting
- D34 engine provisional reference entry and verified sample DTC flows (P0605/P0641/P0651)
- Version code/name updated to 2 / 0.2-field

Important: D34 engine information is provisional and is not shown as confirmed D24 vehicle-specific data.
