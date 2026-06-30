import json, csv

with open('test_execution_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

by_id = {}
for r in results:
    tid = r['test_id']
    if tid not in by_id:
        by_id[tid] = {'name': r['test_name'], 'steps': [], 'status': 'PASS'}
    by_id[tid]['steps'].append(r)
    if r['status'] == 'FAIL':
        by_id[tid]['status'] = 'FAIL'

with open('QA_Test_Results_With_Status.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Test ID', 'Test Case Name', 'QA Status', 'Total Steps', 'Passed Steps', 'Failed Steps', 'Pass Rate'])
    for tid in sorted(by_id.keys()):
        t = by_id[tid]
        total = len(t['steps'])
        passed = sum(1 for s in t['steps'] if s['status'] == 'PASS')
        failed = total - passed
        rate = (passed / total * 100) if total > 0 else 0
        writer.writerow([tid, t['name'], t['status'], total, passed, failed, f"{rate:.1f}%"])

print('CSV generated: QA_Test_Results_With_Status.csv')

