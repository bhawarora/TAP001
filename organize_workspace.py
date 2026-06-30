import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]
REPORTS = ROOT / 'Reports'
TESTS = ROOT / 'Tests'
DATA = ROOT / 'Data'

REPORTS.mkdir(exist_ok=True)
TESTS.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

# Patterns to move
report_patterns = ['*.html', '*.csv', '*.json', 'QA_Test_Report.html', 'QA_Test_Results_With_Status.csv', 'test_execution_results.json']
test_patterns = ['test_*.py', '*test*.py']
data_patterns = ['*.csv', '*.xls', '*.xlsx', '*.json']

# Move report-like files from root into Reports
for p in ROOT.glob('*'):
    if p.is_file():
        lower = p.name.lower()
        if any(p.suffix == ext for ext in ['.html', '.csv', '.json']):
            try:
                shutil.move(str(p), str(REPORTS / p.name))
                print(f"Moved report: {p.name} -> Reports/")
            except Exception as e:
                print(f"Failed to move {p.name}: {e}")

# Move tests into Tests folder
for p in ROOT.glob('test_*.py'):
    try:
        shutil.move(str(p), str(TESTS / p.name))
        print(f"Moved test file: {p.name} -> Tests/")
    except Exception as e:
        print(f"Failed to move {p.name}: {e}")

# Move obvious data files into Data (avoid moving Tests/Test folders)
for p in ROOT.glob('*'):
    if p.is_file() and p.suffix in ['.csv', '.xls', '.xlsx', '.json']:
        if p.parent != DATA and p.parent != REPORTS:
            try:
                shutil.move(str(p), str(DATA / p.name))
                print(f"Moved data file: {p.name} -> Data/")
            except Exception as e:
                print(f"Failed to move {p.name}: {e}")

print('Organization complete.')

