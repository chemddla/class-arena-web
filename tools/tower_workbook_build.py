# 모험의 탑 몬스터 구성 엑셀(docs/모험의탑_몬스터구성.xlsx)을 index.html에서 다시 뽑아 만듦
# 사용법: python tools/tower_workbook_build.py   (node, openpyxl 필요)
# index.html의 SKILL_DEFS ~ TOWER_FLOORS 보상 줄까지를 node로 그대로 돌려 실제 층 편성을 읽음
import json, os, subprocess, sys, tempfile
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', '모험의탑_몬스터구성.xlsx')

DUMP_JS = r"""
const fs = require('fs'), vm = require('vm');
const L = fs.readFileSync(process.argv[2], 'utf8').split('\n');
const a = L.findIndex(l => l.startsWith('    const SKILL_DEFS = {'));
const b = L.findIndex(l => l.includes('TOWER_FLOORS.forEach(f => { f.rewardMc'));
if (a < 0 || b < 0) throw new Error('index.html에서 탑 데이터 구간을 못 찾음');
const code = L.slice(a, b + 1).join('\n') + `
;globalThis.OUT = { TOWER_FLOORS, MONSTER_DEFS, MONSTER_PASSIVES, TOWER_RACES, TOWER_NEW_JOB_STAT,
  TOWER_NEW_JOBS_FLOOR, TOWER_SUPPORT_JOBS_FLOOR, TOWER_BOSS_HP_MULT, TOWER_BOSS_SIZE_MULT, TOWER_BOSS_BODY_COMP, TOWER_BOSS_JOB_ATK,
  jobs: Object.fromEntries(Object.entries(JOB_DEFS).map(([k, v]) => [k, v.name])),
  skills: Object.fromEntries(Object.values(JOB_SKILL_BOOK).flatMap(o => Object.values(o)).map(s => [s.id, s.name])),
  setup: TOWER_FLOORS.map(f => towerEnemySetup(f.floor)),
  bossFloorScale: TOWER_FLOORS.map(f => towerRaceBossFloorScale(f.floor)),
  bossMult: TOWER_FLOORS.map(f => towerBossUnitMult(f.floor)) };`;
const ctx = { console, Math, JSON, Object, Array, location: { search: '' }, URLSearchParams, window: {} };
vm.createContext(ctx); vm.runInContext(code, ctx);
process.stdout.write(JSON.stringify(ctx.OUT));
"""


def load():
    with tempfile.NamedTemporaryFile('w', suffix='.cjs', delete=False, encoding='utf-8') as f:
        f.write(DUMP_JS)
        js = f.name
    try:
        out = subprocess.run(['node', js, os.path.join(ROOT, 'index.html')], capture_output=True, check=True)
    finally:
        os.unlink(js)
    return json.loads(out.stdout.decode('utf-8'))


D = load()
F, M, P, J, SK = D['TOWER_FLOORS'], D['MONSTER_DEFS'], D['MONSTER_PASSIVES'], D['jobs'], D['skills']
JS = D['TOWER_NEW_JOB_STAT']
RACES = {r['name']: r for r in D['TOWER_RACES']}

HEAD_FILL = PatternFill('solid', fgColor='1F2937')
BOSS_FILL = PatternFill('solid', fgColor='FDE68A')
EXTRA_FILL = PatternFill('solid', fgColor='F1F5F9')
THIN = Side(style='thin', color='CBD5E1')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def sheet(wb, title, header, rows, widths, fill_of=None, freeze='B2'):
    ws = wb.create_sheet(title)
    ws.append(header)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = BORDER
    for r in rows:
        ws.append(r)
        fill = fill_of(r) if fill_of else None
        for c in ws[ws.max_row]:
            c.border = BORDER
            c.alignment = Alignment(vertical='center', wrap_text=isinstance(c.value, str) and len(c.value) > 30)
            if fill:
                c.fill = fill
    for i, w in enumerate(widths):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i + 1)].width = w
    if freeze:
        ws.freeze_panes = freeze
        ws.auto_filter.ref = ws.dimensions
    return ws


def passives(mk):
    return ', '.join(P[p]['name'] for p in M[mk].get('passives', [])) or None


def unit_label(f, i):
    return f"{f['unitNames'][i]} ({J[f['comp'][i]]})"


# ===== 층별 구성 =====
floor_rows = []
for f, s in zip(F, D['setup']):
    core = f['extraFrom']
    extra = list(range(core, len(f['comp'])))
    cnt = {}
    for i in extra:
        k = unit_label(f, i)
        cnt[k] = cnt.get(k, 0) + 1
    extra_txt = ', '.join(k + (f'×{n}' if n > 1 else '') for k, n in cnt.items()) or None
    floor_rows.append([
        f['floor'], f['race'], f['name'].split(' · ', 1)[1], '★종족 보스' if f['isRaceBoss'] else None,
        s['level'], s['scale'], f['coreScale'],
        *[unit_label(f, i) for i in range(core)], len(extra), extra_txt, len(f['comp']), f['rewardMc']])

# ===== 유닛 상세 =====
unit_rows = []
for f in F:
    for i, job in enumerate(f['comp']):
        mk = f['monsters'][i]
        m = M[mk]
        t = m.get('trait', {})
        boss = f['isRaceBoss'] and i == 0
        js = {} if boss else JS.get(job, {})  # 종족 보스는 직업과 상관없이 전사 기준 능력치
        kind = '종족 보스' if boss else ('본대' if i < f['extraFrom'] else '추가')
        hp = t.get('hp', 1) * js.get('hp', 1)
        atk = t.get('atk', 1) * js.get('atk', 1)
        if boss:
            bm = D['bossMult'][f['floor'] - 1]
            hp *= bm['hp'] * D['TOWER_BOSS_HP_MULT']
            atk *= bm['atk'] * D['TOWER_BOSS_JOB_ATK'].get(job, 1)
        skills = f['unitSkills'][i]
        unit_rows.append([
            f['floor'], f['race'], i + 1, kind, J[job], f['unitNames'][i], m['name'], m['icon'],
            len(skills), ', '.join(SK.get(k, k) for k in skills), passives(mk),
            round(hp, 3), round(atk, 3), round(t.get('def', 1) * js.get('def', 1), 3), t.get('spd', 1),
            round(m.get('size', 1) * (D['TOWER_BOSS_SIZE_MULT'] if boss else 1), 2)])

# ===== 종족 =====
race_rows = []
for ri, r in enumerate(D['TOWER_RACES']):
    lo, hi = ri * 10 + 1, ri * 10 + 10
    mons = sorted({M[mk]['name'] for f in F[lo - 1:hi] for mk in f['monsters'] if mk != r['boss']})
    bm = D['bossMult'][hi - 1]
    race_rows.append([f'{lo}~{hi}층', r['name'], r['zone'], M[r['boss']]['name'], J[r['bossJob']], r.get('floorScale', 1),
                      round(D['bossFloorScale'][hi - 1], 3), r.get('bossHp', 1.4),
                      round(bm['hp'] * D['TOWER_BOSS_HP_MULT'], 3), round(bm['atk'] * D['TOWER_BOSS_JOB_ATK'].get(r['bossJob'], 1), 3), ', '.join(mons), r['desc']])

# ===== 직업 편성 (종족 × 직업) =====
job_rows = []
seen = set()
for f in F:
    for i, job in enumerate(f['comp']):
        key = (f['race'], f['unitNames'][i], job)
        if key in seen:
            continue
        seen.add(key)
        boss = f['isRaceBoss'] and i == 0
        floors = sorted({g['floor'] for g in F if g['race'] == f['race']
                         and any(g['unitNames'][k] == f['unitNames'][i] and g['comp'][k] == job for k in range(len(g['comp'])))})
        job_rows.append([f['race'], J[job], f['unitNames'][i] + (' (보스)' if boss else ''), M[f['monsters'][i]]['name'],
                         ' → '.join(SK.get(k, k) for k in f['unitSkills'][i]),
                         f'{floors[0]}층' if len(floors) == 1 else f'{len(floors)}개 층 ({floors[0]}~{floors[-1]}층)'])
order = list(RACES)
job_order = list(J)
job_rows.sort(key=lambda r: (order.index(r[0]), job_order.index(next(k for k, v in J.items() if v == r[1]))))

# ===== 몬스터 도감 =====
race_of = {}
for r in D['TOWER_RACES']:
    race_of[r['boss']] = (r['name'], '종족 보스')
for f in F:
    for mk in f['monsters']:
        race_of.setdefault(mk, (f['race'], '일반'))
dex_rows = []
for mk, m in M.items():
    t = m.get('trait', {})
    race, kind = race_of.get(mk, ('(탑 미등장)', '종족 보스' if m.get('big') else '일반'))
    ps = m.get('passives', [])
    dex_rows.append([mk, m['icon'], m['name'], race, kind, m.get('size', 1), t.get('hp', 1), t.get('atk', 1), t.get('def', 1), t.get('spd', 1),
                     ', '.join(P[p]['name'] for p in ps) or None, ' / '.join(f"{P[p]['name']}: {P[p]['desc']}" for p in ps) or None])

wb = openpyxl.Workbook()
wb.remove(wb.active)
sheet(wb, '층별 구성',
      ['층', '종족', '층 이름', '보스층', '적 레벨', '능력치 배율', '본대 배율\n(추가 몬스터 보정)', '1번', '2번', '3번', '4번', '5번',
       '추가 몬스터 수', '추가 몬스터 구성', '총 마릿수', '첫 클리어 보상(CA)'],
      floor_rows, [6, 11, 34, 10, 8, 10, 12, 24, 24, 24, 24, 24, 9, 60, 9, 13],
      fill_of=lambda r: BOSS_FILL if r[3] else None)
sheet(wb, '유닛 상세',
      ['층', '종족', '칸', '구분', '직업', '유닛 이름', '몬스터', '아이콘', '스킬 수', '스킬 (앞에서부터 열림)', '고유 능력',
       '체력 배율', '공격 배율', '방어 배율', '속도 배율', '몸 크기'],
      unit_rows, [6, 11, 5, 9, 9, 18, 13, 6, 7, 44, 24, 8, 8, 8, 8, 8],
      fill_of=lambda r: BOSS_FILL if r[3] == '종족 보스' else (EXTRA_FILL if r[3] == '추가' else None))
sheet(wb, '직업 편성',
      ['종족', '직업', '유닛 이름', '몬스터', '스킬 (51층 이상 기준, 열리는 순서)', '나오는 층'],
      job_rows, [12, 10, 20, 14, 60, 22],
      fill_of=lambda r: BOSS_FILL if r[2].endswith('(보스)') else None)
sheet(wb, '종족',
      ['층 범위', '종족', '구역', '종족 보스', '보스 직업', '일반 층 부대 배율', '보스층 부대 배율', '보스 체력 배율', '보스 실제 체력 배율\n(×몸집 보정 0.6 ×2)',
       '보스 실제 공격 배율\n(×직업 보정)', '나오는 몬스터', '설명'],
      race_rows, [11, 12, 16, 13, 10, 10, 10, 10, 16, 12, 40, 60])
sheet(wb, '몬스터 도감',
      ['ID', '아이콘', '이름', '종족', '구분', '몸 크기', '체력 배율', '공격 배율', '방어 배율', '속도 배율', '고유 능력', '고유 능력 설명'],
      dex_rows, [16, 6, 14, 12, 9, 8, 8, 8, 8, 8, 24, 70],
      fill_of=lambda r: BOSS_FILL if r[4] == '종족 보스' else None)
job_stat_txt = ' · '.join(f"{J[k]} 체력×{v['hp']} 공격×{v['atk']} 방어×{v['def']}" for k, v in JS.items())
sheet(wb, '규칙 참고', ['항목', '내용'], [
    ['종족', '10층마다 종족이 바뀜 (총 20종족, 200층). 각 종족의 10번째 층에 종족 보스'],
    ['부대 구성', '층 안 순서대로 10가지 프리셋: 선봉 돌격대 / 매복 사냥단 / 마법 결사대 / 혼성 공격대 / 철벽 방진 / 원거리 포격대 / 정예 수비대 / 술사 호위대 / 전면 총공세 / 보스 친위대'],
    ['직업', f"1~{D['TOWER_NEW_JOBS_FLOOR'] - 1}층: 전사·궁수·마법사·성녀 / {D['TOWER_NEW_JOBS_FLOOR']}층(거인족)부터 도적·기사·창병·저격수 / "
             f"{D['TOWER_SUPPORT_JOBS_FLOOR']}층(심해족)부터 빙결술사·주술사·음유시인도 섞임 (종족 보스 층의 추가 몬스터는 빙결·저주 없이)"],
    ['종족 보스 직업', '보스마다 어울리는 직업 (TOWER_RACES의 bossJob). 체력·공격력·방어력은 전사 기준으로 맞추고(공격이 느린 술사 보스만 공격력 보정) 직업은 싸우는 방식(사거리·공격 속도·직업 특성)만 바꿈. 스킬은 종족마다 정한 보스 스킬 목록'],
    ['직업 능력치 배율', job_stat_txt + ' (유닛 상세의 체력·공격·방어 배율에 곱해 둠, 종족 보스는 빼고)'],
    ['스킬 수', '일반: 1~10층 2개 · 11~40층 3개 · 41층부터 4개'],
    ['보스 스킬 수', '1~10층 3개 · 11~50층 4개 · 51층부터 5개'],
    ['추가 몬스터', '11층부터 1마리, 13층마다 1마리 추가 (최대 7마리). 본대와 똑같은 몬스터(이름·스킬·크기 그대로)이고, 늘어난 만큼 모두의 능력치를 본대 배율로 낮춤'],
    ['종족 보스 배율', '유닛 상세의 보스 체력·공격 배율 = 몬스터 배율 × 종족 보스 배율(몸집 보정 0.6 포함) × 체력 2배, 몸 크기 = 몬스터 크기 × 2'],
    ['적 레벨', 'round(1 + 층 × 0.95)'],
    ['하드모드', '종족 보스 층을 깨면 그 종족 10개 층 하드모드 개방: 능력치 2배 · 몸 1.5배 · 보스 상태이상 면역 · 보상 2배'],
    ['출처', 'index.html 의 TOWER_FLOORS (TOWER_RACES / TOWER_RACE_SQUADS / 부대 프리셋 / MONSTER_DEFS) 를 tools/tower_workbook_build.py 로 자동 추출'],
], [16, 120], freeze=None)
wb.save(OUT)
print('saved', OUT, len(floor_rows), 'floors', len(unit_rows), 'units', len(job_rows), 'job rows')
