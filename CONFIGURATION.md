# CONFIGURATION.md
# SQLMap V2 Configuration Guide

## Environment Setup

### Requirements
```bash
Python 3.7+
requests library
```

### Installation
```bash
# Install dependencies
pip install requests

# Verify installation
python -m pip list | grep requests
```

## Configuration Files

### Payload Customization
Edit `scanner/payloads.py` to customize:

#### Add Custom DBMS
```python
# In PayloadGenerator.__init__()
self.error_payloads["oracle"] = [
    "' AND EXTRACT(YEAR FROM SYSDATE)=2026-- -",
    "' UNION SELECT 1,2,3 FROM dual-- -",
]
```

#### Add Custom Bypass Techniques
```python
# In PayloadGenerator._apply_waf_bypass()
def _custom_bypass(self, payload):
    # Your custom bypass logic
    return modified_payload
```

### Response Analysis Tuning

#### Adjust Similarity Threshold
```python
# In analyzer/response_analyzer.py
analyzer = ResponseAnalyzer(similarity_threshold=0.75)
```

Lower = more sensitive (may increase false positives)  
Higher = less sensitive (may miss real vulnerabilities)

#### Add Error Keywords
```python
# In ResponseAnalyzer.__init__()
self.error_keywords["oracle"] = ["ora-", "sql*plus", "odci"]
```

### Request Configuration

#### Timeout Settings
```python
# In request_handler.py - RequestHandler.__init__()
self.timeout = 15  # seconds
self.retry_count = 3
```

#### Proxy Configuration
```bash
# Command line
python main.py --url "..." --proxy "http://127.0.0.1:8080"

# Burp Suite integration
--proxy "http://127.0.0.1:8080"  # Default Burp proxy

# SOCKS5 proxy
--proxy "socks5://127.0.0.1:1080"
```

### Threading Configuration

#### Adjust Thread Pool
```bash
# Default: 5 threads
python main.py --url "..." --threads 10

# Recommendations:
# Safe targets: 10-20 threads
# Behind WAF: 2-5 threads
# Rate-limited: 1-3 threads
```

### Detection Technique Settings

#### Time-Based Parameters
```bash
# Default delay: 5 seconds
python main.py --url "..." --technique time --delay 10

# Threshold: 3.0 seconds
python main.py --url "..." --delay 5 --threshold 2.0
```

#### Boolean-Based Sensitivity
```python
# In detection_engine.py - test_boolean_based()
# Adjust sensitivity parameter
is_vulnerable, confidence, metric = self.response_analyzer.detect_boolean_difference(
    true_resp, false_resp, 
    sensitivity=0.15  # Higher = more strict
)
```

## Logging Configuration

### Log Levels
```python
# In utils/logger.py
LOG_LEVELS = {
    "DEBUG": 10,      # Verbose request/response details
    "INFO": 20,       # General progress
    "WARNING": 30,    # Potential issues
    "VULNERABLE": 25, # Vulnerability found
    "ERROR": 40,      # Recoverable errors
    "CRITICAL": 50    # Fatal errors
}
```

### Enable Debug Logging
```bash
python main.py --url "..." --verbose --log-file "debug.log"
```

### Log File Locations
```
logs/
├── sqlmap_v2.log              # Main execution log
├── request_handler.log        # HTTP requests/responses
├── injector.log               # Scanning progress
├── detection_engine.log       # Technique details
├── exploitation_engine.log    # Extraction process
├── extractor.log              # High-level extraction
└── response_analyzer.log      # Analysis details
```

## Performance Tuning

### For Slow Networks
```python
# request_handler.py
self.timeout = 30
self.retry_count = 4
```

### For Fast Networks
```python
# Increase concurrency and reduce timeout
--threads 15 --timeout 5 --retries 1
```

### For Limited Bandwidth
```python
# Reduce request size and frequency
--threads 2 --dump-limit 5
```

### For High-Volume Scanning
```bash
# Use threading and filtering
python main.py --url "..." --threads 20 --timeout 8
```

## WAF Detection & Bypass

### Detect WAF
```bash
# Monitor response differences
python main.py --url "..." --verbose

# Check logs for unusual response patterns
tail -f logs/injector.log
```

### Enable WAF Bypass
```bash
python main.py --url "..." --waf-bypass
```

This enables:
- Inline comments: `/**/`
- Case randomization
- Whitespace mutations

### Custom WAF Rules
```python
# In scanner/payloads.py
def _custom_waf_bypass(self, payload):
    # Modify payload for specific WAF
    payload = payload.replace("SELECT", "SLECT")  # Example: typo bypass
    return payload
```

## DBMS-Specific Configuration

### MySQL Configuration
```bash
python main.py --url "..." --timeout 5 --threads 10
# Payload will auto-select: SLEEP(), @@version
```

### PostgreSQL
```bash
# Slower by default, use longer timeouts
python main.py --url "..." --timeout 10 --technique time --delay 10
```

### MSSQL
```bash
# Use WAITFOR DELAY
python main.py --url "..." --timeout 15 --delay 8
```

## Security Configuration

### Prevent Accidental Damage
```python
# Add safeguards before executing modification
# (Note: This tool does not modify data by default)
```

### Log Encryption
```python
# Secure sensitive data in logs
# Implement in logger.py or post-process logs
```

### Report Security
```bash
# Generated reports contain sensitive data
chmod 600 reports/*.json
chmod 600 reports/*.html
```

## Distributed Scanning

### Multiple Targets
```bash
# Scan multiple URLs sequentially
for url in "http://target1.com" "http://target2.com"; do
    python main.py --url "$url" --export-json "report-$(date +%s).json"
done
```

### Batch Processing
```bash
# Create targets.txt
cat targets.txt | while read url; do
    python main.py --url "$url" --threads 5
done
```

## Troubleshooting Configuration

### Request Failures
```bash
# Increase timeout and retries
python main.py --url "..." --timeout 20 --retries 4
```

### False Positives
```bash
# Increase similarity threshold (be more strict)
# Edit response_analyzer.py:
# similarity_threshold = 0.85
```

### False Negatives
```bash
# Decrease similarity threshold (be more sensitive)
# Also: try multiple detection techniques
--technique all
```

### Rate Limiting
```bash
# Reduce thread count and add delays
python main.py --url "..." --threads 1 --timeout 30
```

## Advanced Configurations

### Custom Payload Strategy
```python
# In scanner/injector.py._test_parameter()
# Modify test order to prioritize certain techniques
detection_order = ["union", "error", "boolean", "time"]
```

### Response Fingerprinting
```python
# In analyzer/response_analyzer.py
# Customize fingerprint detection for specific APIs
dbms_signatures = {
    "custom_app": ["v1.0", "response_header_x"]
}
```

### Extraction Optimization
```python
# In exploiter/exploitation_engine.py
# Adjust limits to prevent performance issues
max_tables = 20
max_columns = 50
max_rows = 1000
```

## Environment Variables (Optional)

```bash
export SQLMAP_TIMEOUT=15
export SQLMAP_THREADS=8
export SQLMAP_PROXY="http://127.0.0.1:8080"
```

Then modify main.py to read these:
```python
timeout = int(os.getenv('SQLMAP_TIMEOUT', 10))
threads = int(os.getenv('SQLMAP_THREADS', 5))
proxy = os.getenv('SQLMAP_PROXY', None)
```

## Performance Benchmarks

### Expected Times (on gigabit connection)
```
Error-Based Detection:       0.5 - 1 second
Boolean-Based Detection:    1 - 3 seconds  
Time-Based Detection:      15 - 45 seconds
UNION-Based Detection:     1 - 2 seconds
Database Extraction:       5 - 10 seconds
Table Extraction (5 tbl):  10 - 30 seconds
Character Extraction:      2 - 5 seconds (binary search)
Full Data Dump (100 rows):  30 - 120 seconds
```

## Recommended Settings by Scenario

### Development/Testing
```bash
--threads 10 --timeout 5 --retries 1 --verbose
```

### Production Assessment
```bash
--threads 3 --timeout 15 --retries 2 --waf-bypass
```

### Aggressive Scan
```bash
--threads 20 --timeout 3 --technique all --dump-limit 1000
```

### Conservative/Stealth
```bash
--threads 1 --timeout 30 --retries 4 --delay 10
```

---

**Need Help?**
- Check `logs/sqlmap_v2.log` for errors
- Run with `--verbose` flag for detailed debug output
- See EXAMPLES.md for common scenarios
