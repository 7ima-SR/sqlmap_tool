# 🧪 SQL Injection Testing Tool

A production-grade, modular SQL Injection testing and exploitation framework for security professionals. Built with advanced detection logic, real exploitation capabilities, and comprehensive reporting.

![Built With](https://img.shields.io/badge/Built%20With-Python-blue?style=flat-square)
![Library](https://img.shields.io/badge/Library-Scapy-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![Author](https://img.shields.io/badge/Author-Hima-red?style=flat-square)

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Performance & Methodology](#performance--methodology)
- [Security & Disclaimer](#security--disclaimer)

---

## Overview

SQLMap Tool v2 is a sophisticated SQL Injection (SQLi) detection and exploitation framework designed for:
- **Security Researchers:** Advanced detection techniques with multi-metric validation
- **Penetration Testers:** Real data extraction with DBMS-specific payloads and WAF evasion
- **Developers:** Modular, extensible codebase for custom integration and testing
- **Teams:** Structured reporting (JSON/HTML), logging, and collaboration-friendly output

Unlike basic SQLi scanners, this tool implements advanced techniques:
- **Similarity-Based Detection** using difflib for reduced false positives
- **Multi-Metric Response Analysis** (status, length, time, headers, content)
- **DBMS Fingerprinting** to identify database systems and version
- **Binary Search Data Extraction** for efficient and accurate dumping
- **Boolean, Error, Time-Based, and Union-Based** SQLi detection
- **WAF Bypass Techniques** and adaptive payload generation

---

## Key Features

### 🔍 Advanced Detection
- Multi-metric response analysis (similarity, status code, response length, timing)
- DBMS-specific fingerprinting and version detection
- Baseline comparison to reduce false positives
- Support for error-based, boolean-based, time-based, and union-based SQLi
- Per-parameter testing with granular injection points

### 💥 Real Exploitation
- Binary search algorithm for efficient data extraction
- Multi-trial validation to ensure accuracy
- DBMS-specific payloads (MySQL, PostgreSQL, Oracle, SQL Server, SQLite)
- WAF and IDS evasion techniques
- Comment stripping, encoding, and payload obfuscation

### 🏗️ Modular Architecture
- **Scanner:** Injection and detection engine
- **Analyzer:** Response analysis and fingerprinting
- **Exploiter:** Data extraction and exploitation
- **Utils:** Logging, HTTP handling, reporting
- Easy to extend, test, and integrate

### 📊 Professional Reporting
- Structured JSON reports with full exploitation details
- HTML reports for stakeholder presentation
- Findings summary with confidence scores
- Extracted data organized by database/table/column

### 🔐 Structured Logging
- 6-level logging framework (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output with timestamps
- Detailed operation tracking for debugging and auditing

### ⚡ Performance
- Multi-threaded scanning and exploitation
- Concurrent parameter testing
- Configurable thread pool and timeouts
- Efficient binary search extraction (logarithmic complexity)

---

## Requirements

- **Python:** 3.7 or higher
- **Libraries:** `requests` (for HTTP handling)
- **Optional:** Modern browser (for viewing HTML reports)
- **Permissions:** Authorized testing target only

---

## Installation

### 1. Clone or Download
```bash
git clone <repo-url> sqlmap_tool
cd sqlmap_tool
```

### 2. Install Dependencies
```bash
pip install requests
```

Or using a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install requests
```

### 3. Verify Installation
```bash
python3 main.py --help
```

---

## Quick Start

### Basic Scan (Automatic Detection)
```bash
python3 main.py -u "http://target.com/page?id=1"
```

### Full Exploitation with Reporting
```bash
python3 main.py \
  -u "http://target.com/page?id=1" \
  --techniques=all \
  --threads=10 \
  --report=reports/target.json \
  --html
```

### Verbose Output with Logging
```bash
python3 main.py -u "http://target.com/page?id=1" --log-level=DEBUG
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

---

## Architecture

### Directory Structure
```
sqlmap_tool/
├── main.py                           # CLI entry point and orchestrator
├── scanner/
│   ├── __init__.py
│   ├── detection_engine.py          # Detection logic (error, boolean, time, union)
│   ├── injector.py                  # Multi-threaded injection orchestrator
│   └── payloads.py                  # Payload library (40+ payloads)
├── analyzer/
│   ├── __init__.py
│   ├── response_analyzer.py         # Response analysis and fingerprinting
├── exploiter/
│   ├── __init__.py
│   ├── exploitation_engine.py       # Binary search extraction engine
│   └── extractor.py                 # Full exploitation workflow
├── utils/
│   ├── __init__.py
│   ├── logger.py                    # Structured logging framework
│   ├── request_handler.py           # HTTP handling with retry logic
│   ├── payloads.py                  # Payload utilities
│   └── report_generator.py          # JSON/HTML report generation
├── logs/                            # Log files
├── reports/                         # Generated reports
└── *.md                             # Comprehensive documentation
```

### Module Overview

| Module | Purpose |
|--------|---------|
| **scanner.detection_engine** | Error, Boolean, Time, Union-based detection |
| **scanner.injector** | Multi-threaded test orchestration |
| **scanner.payloads** | DBMS-specific payload library |
| **analyzer.response_analyzer** | Similarity, fingerprinting, multi-metric analysis |
| **exploiter.exploitation_engine** | Binary search data extraction |
| **exploiter.extractor** | Full exploitation workflow coordination |
| **utils.logger** | Structured logging (6 levels, file+console) |
| **utils.request_handler** | HTTP requests with retry, timeout, injection |
| **utils.report_generator** | JSON/HTML reporting |

---

## Usage Examples

### Example 1: Basic Detection
```bash
python3 main.py -u "http://dvwa.local/login.php?login=admin" \
  --parameter=login \
  --techniques=error
```

### Example 2: Full Test with Threading
```bash
python3 main.py -u "http://target.com/product?id=123&category=books" \
  --techniques=all \
  --threads=15 \
  --timeout=10 \
  --log-level=INFO
```

### Example 3: Data Extraction with Reporting
```bash
python3 main.py -u "http://target.com/page?id=1" \
  --detect \
  --extract \
  --database=test_db \
  --table=users \
  --column=password \
  --report=reports/extraction.json \
  --html \
  --threads=10
```

See [EXAMPLES.md](EXAMPLES.md) for 20+ advanced scenarios.

---

## Configuration

The tool supports extensive CLI arguments and configuration:

| Argument | Description |
|----------|-------------|
| `-u, --url` | Target URL (required) |
| `--technique` | Injection technique (error, boolean, time, union, all) |
| `--threads` | Number of concurrent threads (default: 5) |
| `--parameter` | Target parameter (auto-detect if omitted) |
| `--detect` | Run detection phase only |
| `--extract` | Run extraction phase |
| `--database` | Database name (for extraction) |
| `--table` | Table name (for extraction) |
| `--column` | Column name (for extraction) |
| `--timeout` | Request timeout in seconds (default: 10) |
| `--report` | Save JSON report to file |
| `--html` | Generate HTML report alongside JSON |
| `--log-level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

See [CONFIGURATION.md](CONFIGURATION.md) for complete options.

---

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** — Installation, setup, and basic usage
- **[EXAMPLES.md](EXAMPLES.md)** — 20+ real-world usage scenarios
- **[CONFIGURATION.md](CONFIGURATION.md)** — All CLI arguments and settings
- **[UPGRADE_NOTES.md](UPGRADE_NOTES.md)** — Version history and migration guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** — Technical architecture and algorithms
- **[DELIVERY_SUMMARY.md](DELIVERY_SUMMARY.md)** — Delivery checklist and roadmap

---

## Performance & Methodology

### Detection Methodology
1. **Baseline Establishment:** Extract baseline response (status, length, headers)
2. **Payload Injection:** Test DBMS-specific payloads
3. **Response Analysis:** Compare against baseline using:
   - Similarity (difflib)
   - Status code changes
   - Response length variance
   - Timing analysis
   - Error messages
4. **Multi-Metric Validation:** Combine metrics for accurate detection
5. **Fingerprinting:** Identify DBMS and version via error patterns

### Extraction Methodology
1. **Binary Search:** Efficiently extract one character at a time
2. **Multi-Trial Validation:** Confirm each character with multiple tests
3. **Adaptive Payloads:** Use DBMS-specific queries for accuracy
4. **Progress Tracking:** Resume interrupted extractions

### Performance Characteristics
- **Threading:** O(n/t) where n = tests, t = threads
- **Binary Search:** O(log n) queries per character
- **Typical Execution:** ~5-15 seconds for detection, ~1-5 minutes for full extraction

---

## Security & Disclaimer

### ⚠️ Important
This tool is intended **exclusively** for:
- ✅ Authorized penetration testing
- ✅ Security research on systems you own
- ✅ Educational purposes in controlled environments

### Legal Compliance
- **Obtain written authorization** before testing any system you don't own
- **Comply with local laws** regarding penetration testing and cybersecurity
- **Responsible disclosure:** Report findings responsibly
- **No malicious use:** This tool must not be used for unauthorized access or data theft

### Best Practices
- Use a dedicated VPN/proxy for testing
- Test in isolated environments first
- Maintain logs of all testing activities
- Document findings professionally
- Clean up after testing

---

## Support & Contribution

- **Issues:** Report bugs via GitHub issues
- **Documentation:** See wikis and guides in `*.md` files
- **Contribution:** Fork, test locally, submit PRs
- **Roadmap:** See `DELIVERY_SUMMARY.md` for Version 3 features

---

## License

This tool is for authorized security testing only. Users are responsible for ensuring compliance with applicable laws and obtaining proper authorization before use.

---

## Roadmap (Version 3)

Planned enhancements for future releases:
- UI dashboard for real-time monitoring
- Machine learning-based detection
- Distributed scanning capabilities
- Advanced CAPTCHA handling
- Database schema enumeration
- Automated remediation suggestions

See full roadmap in [DELIVERY_SUMMARY.md](DELIVERY_SUMMARY.md).

---

**Version 2.0 — Professional Edition — April 2026**

---

## 📜 License

- This project is licensed under the MIT License.

---

## 📧 Contact

- Made with ❤️ by 7ima-SR

- 🌐 Website: https://ibrahim-elsaied.netlify.app/
