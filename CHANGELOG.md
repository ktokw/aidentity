# aidentity CHANGELOG

## [Unreleased]

### Fixed — packaging

- `pyproject.toml`: `build-backend` pointed at a nonexistent
  `setuptools.backends.legacy:build`, which made `pip install -e .` fail
  outright (`BackendUnavailable: Cannot import 'setuptools.backends.legacy'`).
  Corrected to `setuptools.build_meta`. Verified: fresh venv, `pip install -e .`,
  full test suite (62 passed), and `aidentity init/validate/status/boot` all work.

### Added

- `bootstrap.sh` — one-command install + demo (`init` → `validate` → `status`
  → `boot --mode lite` in a throwaway directory). README/QUICKSTART now lead
  with this since the package isn't published to PyPI yet.

### Added — schema/somatic.yaml

**gap-S2: arousal range 범용화 (range_spec 추가)**
- `mood_schema` 의 valence / arousal / dominance 각 축에 `range_spec: {min, max}` 필드 추가.
- 기존 `range: "-1.0 ~ 1.0"` 문자열 유지 (backward-compat — 사람이 읽는 용도).
- `range_spec` 은 프로그래밍 방식 검증 및 정규화에 사용. 기본값 `{min: -1.0, max: 1.0}` (PAD 표준).
- 0~1 범위 시스템은 `range_spec: {min: 0.0, max: 1.0}` 으로 override 가능.
- 참조: Reef CHG-1849 drift 보고 + tso_in_the_loop Somatic layer 0~1 기반 (CHG-2072).

**gap-P1: allow_feeling_null 추가**
- `episode_schema` 에 `feeling: string` 필드 명시 (nullable).
- `allow_feeling_null: true` 필드 추가: feeling 필드 생략 허용 여부를 schema 수준에서 제어.
- 기본값 `true` — feeling 없이도 episode 검증 통과.
- 합성검증 룰 주석 명시: null feeling = "미기록" 으로 해석, "중립 감정" 과 구분.
- 참조: CHG-2072.
