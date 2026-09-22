# forklift_v20_clean_rebuild_master

이 ZIP은 과거 V8.x overlay를 또 적용하는 패치가 아니다.
프로젝트를 하나의 기준으로 다시 시작하기 위한 **authoritative reset package**다.

먼저 `WORK_START_HERE.md`를 읽는다.

핵심:
- 새 branch `v20-clean-rebuild`
- old runtime code 재사용 금지
- validated data/behavior만 migration
- single state file
- single diagnostic engine
- model scope hard gate
- field-first diagnostic contract
- P0 real-world regressions
- 30 distinct scenarios per terminal
- runtime evidence + exact SHA VERIFIED APK
