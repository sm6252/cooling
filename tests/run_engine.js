// index.html 안의 계산 엔진(TC)을 꺼내 Node에서 실행하는 회귀 테스트
// 사용: node tests/run_engine.js   (Python 독립 계산 결과와 비교: python3 tests/independent_check.py 먼저 실행)
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const m = html.match(/<script>\s*(\/\/ ===== 열·유동 계산 엔진[\s\S]*?)<\/script>/);
if (!m) { console.error('계산 엔진 블록을 찾지 못했습니다.'); process.exit(1); }
const TC = new Function(m[1].replace("if (typeof module !== 'undefined') module.exports = TC;", '') + '; return TC;')();
const mm = 1e-3;
const P = { Tin: 70, etaPump: 0.5, common: { Q: 42.5, chipL: 5 * mm, chipW: 5 * mm, L: 12 * mm, W: 12 * mm, tBase: 2 * mm, kBase: 390,
  layers: [[0.18, 118], [0.08, 50], [0.3, 390], [0.38, 170], [0.3, 390], [0.3, 50]].map(([t, k]) => ({ t: t * mm, k })) },
  geo: { A: { D: .5 * mm, H: 1 * mm, ST: 1 * mm, SL: 1 * mm, arr: 'stag', Hhdr: 3 * mm }, B: { d: .5 * mm, S: 2.5 * mm, Hj: 1.5 * mm, ln: 1 * mm, Hp: 3 * mm, exh: 'dist', inlet: 'sharp', rough: 2e-6 },
    C: { d: .5 * mm, S: 2.5 * mm, Hj: 1.5 * mm, ln: 1 * mm, Hp: 3 * mm, Dp: .4 * mm, Hpil: .8 * mm, Sp: .8 * mm, chi: 1, inlet: 'sharp', rough: 2e-6 } } };
let py = null; try { py = JSON.parse(fs.readFileSync(path.join(__dirname, 'py.json'), 'utf8')); } catch (e) { }
let worst = 0, n = 0;
for (const f of ['amp110', 'amp122', 'amp120', 'valde1', 'castrol', 'fuchs', 'hxl9119', 'e565', 'repsol']) for (const t of ['A', 'B', 'C']) {
  const r = TC.solve({ type: t, fluid: f }, P, 'power', 0.0133); n++;
  let line = `${f.padEnd(8)} ${t}  Tj ${r.Tj.toFixed(2)} °C`;
  if (py) { const d = Math.abs(r.Tj - py[`${f}|${t}`].Tj); worst = Math.max(worst, d); line += `  |Py차이| ${d.toFixed(3)} K`; }
  console.log(line);
}
if (py) { console.log(`최대 차이 ${worst.toFixed(3)} K (${n}개 경우)`); process.exit(worst < 0.05 ? 0 : 1); }
