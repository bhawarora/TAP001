import json
from datetime import datetime

def generate_html_report(results_file=None, output_file=None):
    """Generate comprehensive HTML report from test results"""
    
    ROOT = Path(__file__).resolve().parents[0]
    REPORTS_DIR = ROOT / 'Reports'
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if results_file is None:
        results_file = REPORTS_DIR / 'test_execution_results.json'
        if not results_file.exists():
            results_file = ROOT / 'test_execution_results.json'

    # Load results
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Calculate summary
    total_steps = len(results)
    passed_steps = sum(1 for r in results if r["status"] == "PASS")
    failed_steps = total_steps - passed_steps
    
    # Group by test_id
    tests_by_id = {}
    for result in results:
        test_id = result["test_id"]
        if test_id not in tests_by_id:
            tests_by_id[test_id] = {
                "name": result["test_name"],
                "status": "PASS",
                "steps": []
            }
        tests_by_id[test_id]["steps"].append(result)
        if result["status"] == "FAIL":
            tests_by_id[test_id]["status"] = "FAIL"
    
    # Calculate test stats
    total_tests = len(tests_by_id)
    passed_tests = sum(1 for t in tests_by_id.values() if t["status"] == "PASS")
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # HTML content
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Extractor V2 - QA Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.95;
            margin-bottom: 5px;
        }}
        
        .header .date {{
            font-size: 0.95em;
            opacity: 0.85;
        }}
        
        .summary-section {{
            padding: 50px 40px;
            background: linear-gradient(to bottom, #f8f9fa, #ffffff);
            border-bottom: 3px solid #667eea;
        }}
        
        .summary-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 30px;
            font-weight: 600;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border-top: 5px solid #667eea;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }}
        
        .card.pass {{
            border-top-color: #28a745;
        }}
        
        .card.fail {{
            border-top-color: #dc3545;
        }}
        
        .card h3 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .card.pass h3 {{
            color: #28a745;
        }}
        
        .card.fail h3 {{
            color: #dc3545;
        }}
        
        .card p {{
            color: #666;
            font-size: 1em;
            font-weight: 500;
        }}
        
        .progress-container {{
            margin-top: 30px;
        }}
        
        .progress-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-weight: 600;
            color: #333;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 40px;
            background: #e9ecef;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1em;
            transition: width 0.3s ease;
        }}
        
        .test-results {{
            padding: 50px 40px;
        }}
        
        .results-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 30px;
            font-weight: 600;
        }}
        
        .test-result {{
            margin-bottom: 25px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
        }}
        
        .test-result:hover {{
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
            border-color: #667eea;
        }}
        
        .test-header {{
            padding: 20px;
            background: linear-gradient(to right, #f8f9fa, #ffffff);
            border-bottom: 2px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }}
        
        .test-header:hover {{
            background: linear-gradient(to right, #f1f3f5, #f8f9fa);
        }}
        
        .test-id-title {{
            flex-grow: 1;
        }}
        
        .test-id {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.15em;
        }}
        
        .test-name {{
            color: #555;
            margin-top: 5px;
            font-size: 0.95em;
        }}
        
        .badge {{
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .badge.pass {{
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724;
            box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
        }}
        
        .badge.fail {{
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            color: #721c24;
            box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
        }}
        
        .test-body {{
            padding: 20px;
            display: none;
        }}
        
        .test-body.show {{
            display: block;
        }}
        
        .steps-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 0;
        }}
        
        .steps-table thead {{
            background: #f8f9fa;
        }}
        
        .steps-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #dee2e6;
            font-size: 0.95em;
        }}
        
        .steps-table td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .steps-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .step-num {{
            font-weight: bold;
            color: #667eea;
            width: 60px;
        }}
        
        .action {{
            color: #333;
        }}
        
        .expected {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .actual {{
            font-weight: 600;
        }}
        
        .actual.pass {{
            color: #28a745;
        }}
        
        .actual.fail {{
            color: #dc3545;
        }}
        
        .footer {{
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 40px;
            text-align: center;
            border-top: 3px solid #667eea;
            color: #666;
        }}
        
        .footer p {{
            margin-bottom: 10px;
        }}
        
        .footer .timestamp {{
            color: #999;
            font-size: 0.9em;
        }}
        
        .issues-section {{
            background: #fff3cd;
            padding: 30px 40px;
            border-left: 5px solid #ffc107;
            margin: 40px;
            border-radius: 8px;
        }}
        
        .issues-section h3 {{
            color: #856404;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .bug-list {{
            margin-left: 20px;
        }}
        
        .bug-list li {{
            color: #856404;
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        
        .recommendations-section {{
            background: #e7f3ff;
            padding: 30px 40px;
            border-left: 5px solid #0066cc;
            margin: 40px;
            border-radius: 8px;
        }}
        
        .recommendations-section h3 {{
            color: #004085;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .recommendations-section ul {{
            margin-left: 20px;
            color: #004085;
        }}
        
        .recommendations-section li {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        
        .expand-icon {{
            display: inline-block;
            margin-left: 10px;
            font-weight: bold;
            color: #667eea;
            transition: transform 0.3s ease;
        }}
        
        .test-result.expanded .expand-icon {{
            transform: rotate(180deg);
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Data Extractor V2 - QA Test Report</h1>
            <div class="subtitle">Automated Test Execution Report</div>
            <div class="date">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <!-- Summary Section -->
        <div class="summary-section">
            <div class="summary-title">📈 Test Execution Summary</div>
            <div class="summary-cards">
                <div class="card">
                    <h3>{total_tests}</h3>
                    <p>Total Test Cases</p>
                </div>
                <div class="card pass">
                    <h3>{passed_tests}</h3>
                    <p>Passed Tests</p>
                </div>
                <div class="card fail">
                    <h3>{failed_tests}</h3>
                    <p>Failed Tests</p>
                </div>
                <div class="card">
                    <h3>{total_steps}</h3>
                    <p>Total Test Steps</p>
                </div>
                <div class="card pass">
                    <h3>{passed_steps}</h3>
                    <p>Steps Passed</p>
                </div>
                <div class="card fail">
                    <h3>{failed_steps}</h3>
                    <p>Steps Failed</p>
                </div>
            </div>
            
            <div class="progress-container">
                <div class="progress-label">
                    <span>Overall Pass Rate</span>
                    <span>{pass_rate:.1f}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {pass_rate}%;">{pass_rate:.1f}%</div>
                </div>
            </div>
        </div>
        
        <!-- Test Results -->
        <div class="test-results">
            <div class="results-title">🧪 Test Case Results</div>
"""
    
    # Add test results
    for test_id in sorted(tests_by_id.keys()):
        test = tests_by_id[test_id]
        status_class = test["status"].lower()
        
        html += f"""
            <div class="test-result" onclick="toggleTest(this)">
                <div class="test-header">
                    <div class="test-id-title">
                        <div class="test-id">TC {test_id}: {test['name']}</div>
                    </div>
                    <div class="badge {status_class}">{test['status']}</div>
                    <span class="expand-icon">▼</span>
                </div>
                <div class="test-body">
                    <table class="steps-table">
                        <thead>
                            <tr>
                                <th style="width: 80px;">Step</th>
                                <th style="width: 25%;">Action</th>
                                <th style="width: 25%;">Expected Result</th>
                                <th style="width: 50%;">Actual Result</th>
                            </tr>
                        </thead>
                        <tbody>
"""
        
        for step in test["steps"]:
            status_class = "pass" if step["status"] == "PASS" else "fail"
            html += f"""
                            <tr>
                                <td class="step-num">{step['step']}</td>
                                <td class="action">{step['expected']}</td>
                                <td class="expected">{step['expected']}</td>
                                <td class="actual {status_class}">{step['actual']}</td>
                            </tr>
"""
        
        html += """
                        </tbody>
                    </table>
                </div>
            </div>
"""
    
    # Issues and Recommendations
    html += f"""
        </div>
        
        <!-- Issues Section -->
        <div style="padding: 40px;">
            <h2 style="color: #333; margin-bottom: 20px;">⚠️ Issues Identified</h2>
            <div class="issues-section">
                <h3>Authentication & Session Management</h3>
                <ul class="bug-list">
                    <li><strong>Status:</strong> ✅ RESOLVED - Using automated authentication from create_auth_state.py</li>
                    <li><strong>Details:</strong> Session is automatically created using embedded credentials</li>
                    <li><strong>Impact:</strong> Tests can run in succession without re-authentication</li>
                </ul>
            </div>
"""
    
    if failed_tests > 0:
        html += """
            <div class="issues-section">
                <h3>Test Failures</h3>
                <ul class="bug-list">
                    <li><strong>Root Cause:</strong> PowerApps iframe loading delays or element locator timeouts</li>
                    <li><strong>Impact:</strong> Some test steps may not complete within expected timeframes</li>
                    <li><strong>Recommendation:</strong> Increase timeout values in locator operations</li>
                </ul>
            </div>
"""
    
    html += """
        </div>
        
        <!-- Recommendations -->
        <div class="recommendations-section">
            <h3>✅ Recommendations for Future Test Runs</h3>
            <ul>
                <li>Implement proper wait mechanisms for PowerApps iframe rendering</li>
                <li>Add screenshot capture on test failures for enhanced debugging</li>
                <li>Use longer timeout values for cloud-based applications</li>
                <li>Implement retry logic with exponential backoff for flaky tests</li>
                <li>Add comprehensive error logging and reporting</li>
                <li>Run tests in headless mode for CI/CD pipelines once validated</li>
                <li>Implement parallel execution for faster test runs</li>
                <li>Add performance metrics to test results</li>
            </ul>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>Data Extractor V2 - QA Test Report</strong></p>
            <p>Test Execution Environment: Automated via Playwright</p>
            <p class="timestamp">Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
    </div>
    
    <script>
        function toggleTest(element) {{
            element.classList.toggle('expanded');
            const body = element.querySelector('.test-body');
            body.classList.toggle('show');
        }}
    </script>
</body>
</html>
"""
    
    if output_file is None:
        output_file = REPORTS_DIR / 'QA_Test_Report.html'

    # Write HTML to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ HTML Report generated: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_html_report()

