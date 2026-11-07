# 절연유체 파워모듈 냉각안 비교기

열시스템 디자인 학기말 프로젝트(1단계 예비설계)용 계산 도구입니다. 전력반도체(SiC) 냉각안 A(마이크로필라), B(임핀징 제트), C(제트+필라)를 NREL 논문 조건에서 비교합니다.

- **실행:** `index.html`을 브라우저로 열면 됩니다. 서버나 설치가 필요 없습니다.
- **웹 주소:** GitHub Pages를 켜면 `https://<계정>.github.io/<저장소>/`로 항상 같은 주소에서 열립니다.

## 수정 방법
`index.html` 한 파일에 모든 것이 들어 있습니다. Claude, Codex, 직접 편집 등 무엇으로 고쳐도 됩니다.
커밋하면 Pages 주소에 1~2분 안에 반영됩니다.

## 검증 (수정 후 꼭 실행)
```bash
python3 tests/independent_check.py   # 원 문헌 식으로 따로 짠 독립 계산 → tests/py.json
node tests/run_engine.js             # index.html 엔진 결과와 비교 (차이 0.05 K 넘으면 실패)
```

## 출처
조건과 물성은 NREL SiC 모듈 연구(IEEE EPS 2023, IMAPS 2024, DOE AMR 2019)와 각 유체 제조사 데이터시트에서 가져왔습니다. 링크는 도구의 "논문 조건·검증" 탭과 "유체 선정표" 탭에 있습니다.
