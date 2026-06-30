import json, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]
REPORTS_DIR = ROOT / 'Reports'
results_path = REPORTS_DIR / 'test_execution_results.json'
if not results_path.exists():
    # fallback to root
    results_path = ROOT / 'test_execution_results.json'

with open(results_path, 'r', encoding='utf-8') as f:
    results = json.load(f)

by_id = {}
for r in results:
    tid = r['test_id']
    if tid not in by_id:
        by_id[tid] = {'name': r['test_name'], 'steps': [], 'status': 'PASS'}
    by_id[tid]['steps'].append(r)
    if r['status'] == 'FAIL':
        by_id[tid]['status'] = 'FAIL'
    elif r['status'] == 'SKIP' and by_id[tid]['status'] != 'FAIL':
        by_id[tid]['status'] = 'SKIP'

out_csv = REPORTS_DIR / 'QA_Test_Results_With_Status.csv'
with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Test ID', 'Test Case Name', 'QA Status', 'Total Steps', 'Passed Steps', 'Failed Steps', 'Skipped Steps', 'Pass Rate'])
    for tid in sorted(by_id.keys()):
        t = by_id[tid]
        total = len(t['steps'])
        passed = sum(1 for s in t['steps'] if s['status'] == 'PASS')
        failed = sum(1 for s in t['steps'] if s['status'] == 'FAIL')
        skipped = total - passed - failed
        rate = (passed / total * 100) if total > 0 else 0
        writer.writerow([tid, t['name'], t['status'], total, passed, failed, skipped, f"{rate:.1f}%"])

print('CSV generated: QA_Test_Results_With_Status.csv')

