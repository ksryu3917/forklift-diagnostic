# V20 clean architecture

## 핵심 목표
overlay가 MainActivity를 문자열 치환하고 validator가 버전 문자열을 여러 파일에서 맞추는 구조를 없앤다.

## 계층

### core
- `ProjectState`: release identity 단일 로더
- `VehicleScope`: 제조사/모델/사양 범위 판정
- `EvidenceRef`: 매뉴얼 근거
- `ResultValue`: PASS/FAIL/숫자/선택 입력

### data
- `VehicleRepository`
- `DiagnosticRepository`
- `StudyRepository`
- `ManualCatalogRepository`
- `LocalHistoryRepository`

### engine
- `DiagnosticEngine`: 현재 node 하나만 제공
- `BranchEvaluator`: 입력값에 따라 next node 결정
- `ScopeGuard`: 모델/제조사 누출 차단
- `TeardownGate`: 분해 가능 여부
- `EvidenceGate`: 숫자/핀/토크/절차에 근거 요구

### ui
- `MainActivity`
- `VehicleSelectActivity`
- `DiagnosisHomeActivity`
- `DiagnosticRunnerActivity`
- `StudyActivity`
- `ManualLibraryActivity`
- `EvidenceViewerActivity`
- `HistoryActivity`
- `PartsLaborActivity`

Activity가 JSON 구조를 직접 해석하지 않는다.
UI는 engine이 제공하는 ViewModel 성격의 plain object만 표시한다.

## assets

`app/src/main/assets/v20/`
- `project_state.json`
- `vehicles/*.json`
- `diagnostics/*.json`
- `study/*.json`
- `manual_catalog.json`
- `evidence_index.json`
- `p0_regressions.json`

## version identity

빌드 전 스크립트는 `PROJECT_STATE.json` 원본을 읽고
build output용 `assets/v20/project_state.json`에만
실제 SHA/branch를 stamp한다.

소스 파일을 CI에서 rewrite하여 런타임 코드를 바꾸지 않는다.

## 상태보고

앱의 "앱/데이터 상태" 화면은:
- release
- state
- app version
- data schema
- source branch
- full SHA
- normalized vehicle count
- graph count
- study lesson count
- manual catalog count
- latest validator report ID
를 표시한다.
