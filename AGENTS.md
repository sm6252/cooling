# 작업 안내 (Codex, Claude 등 코딩 에이전트용)

## 구조
`index.html` 한 파일. `<script>` 블록이 두 개 있습니다.

1. **계산 엔진** (`// ===== 열·유동 계산 엔진` 으로 시작, 전역 `TC`)
   - `FLUIDS`: 단상 절연유체 데이터시트 값. 새 유체는 이 객체에 추가합니다.
     필수 필드: `name, full, maker, rhoRef:[T,ρ], beta, nuPts:[[T1,ν1],[T2,ν2]], cpPts 또는 (cp25,cpT), kPts 또는 (k25,kT), diel, dielTxt, flash, flashC, compatS, dataS, src, url`.
   - `props1p(f,T)`: 물성 온도보간 (점도는 Andrade 두 점 맞춤).
   - `coolA / coolB / coolC`: 냉각면 모델 (Zukauskas+Gaddis / Martin / Martin×χ+핀).
   - `packageR, baseR`: 패키지 45° 확산, Lee-Song-Au-Moran 확산저항.
   - `evaluate(cs,V,P)`, `solve(cs,P,mode,target)`: 한 경우 계산, 동일 펌프동력·Δp·유량 조건으로 유량 결정.
   - `score`, `CRIT`: PDF 5)항 가중치 평가.
2. **화면(UI)**: 입력 패널(`SPEC`, `LAYERS`, `buildInputs`), 탭(`TABS`), 탭별 `render*` 함수.

## 규칙
- 단위는 내부 SI(m, W, Pa, m³/s). 입력 패널만 mm·L/min·kPa.
- 물성값을 추가·수정할 때는 반드시 `src`와 `url`에 출처를 적고, 가정한 값은 `src`에 "가정"이라고 씁니다.
- 계산식을 바꾸면 `tests/independent_check.py`도 같이 고치고 아래 검증을 통과시킵니다.
- 외부 라이브러리를 쓰지 않습니다 (Google Fonts만 사용).

## 검증
```bash
python3 tests/independent_check.py && node tests/run_engine.js
```
