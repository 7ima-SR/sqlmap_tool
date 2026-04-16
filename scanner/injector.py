# scanner/injector.py
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs
from utils.request_handler import RequestHandler
from analyzer.response_analyzer import ResponseAnalyzer
from utils.payloads import PayloadGenerator
from scanner.detection_engine import DetectionEngine
from utils.logger import Logger

class SQLiInjector:
    """
    Advanced SQL injection scanner with multiple detection techniques
    - Error-based SQLi
    - Boolean-based blind SQLi
    - Time-based blind SQLi
    - UNION-based SQLi
    """
    
    def __init__(self, request_handler, response_analyzer, payload_gen, max_workers=5):
        self.request_handler = request_handler
        self.response_analyzer = response_analyzer
        self.payload_gen = payload_gen
        self.detection_engine = DetectionEngine(request_handler, response_analyzer)
        self.logger = Logger("injector.log")
        self.max_workers = max_workers
        self.vulnerabilities = []
        
    def scan(self, url, method="GET", data=None, headers=None, parameters=None):
        """
        Comprehensive SQLi scan on target URL
        Returns: list of vulnerabilities found
        """
        self.logger.info(f"Starting SQL injection scan on {url}")
        start_time = time.time()
        
        if headers is None:
            headers = {}
        
        # Extract parameters to test
        params_to_test = parameters or self._extract_parameters(url, method, data, headers)
        
        self.logger.info(f"Found {len(params_to_test)} parameters to test")
        
        # Test each parameter with thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._test_parameter, param, url, method, data, headers): param
                for param in params_to_test
            }
            
            for future in as_completed(futures):
                param = futures[future]
                try:
                    result = future.result()
                    if result:
                        self.vulnerabilities.append(result)
                except Exception as e:
                    self.logger.error(f"Error testing parameter {param.get('name')}: {str(e)}")
        
        elapsed = time.time() - start_time
        self.logger.info(f"Scan completed in {elapsed:.2f}s. Found {len(self.vulnerabilities)} vulnerabilities")
        
        return self.vulnerabilities

    def _test_parameter(self, param, url, method, data, headers):
        """
        Test single parameter for SQL injection using multiple techniques
        Returns: vulnerability dict if found, None otherwise
        """
        param_name = param.get("name")
        param_type = param.get("type", "string")
        injection_point = param.get("injection_point", "url")
        
        self.logger.debug(f"Testing parameter: {param_name} ({param_type}, {injection_point})")
        
        # Get baseline for comparison
        baseline, baseline_time = self.request_handler.send_request(url, method, data, headers)
        if not baseline or baseline_time is None:
            self.logger.warning(f"Could not establish baseline for {param_name}")
            return None
        
        # 1. Test Error-Based SQLi
        is_vuln, payload, confidence, details = self.detection_engine.test_error_based(
            url, param_name, method, data, headers, dbms="mysql", retries=2
        )
        if is_vuln:
            return {
                "parameter": param_name,
                "type": "error-based",
                "payload": payload,
                "confidence": confidence,
                "injection_point": injection_point,
                "details": details
            }
        
        # 2. Test Boolean-Based Blind SQLi
        is_vuln, true_payload, false_payload, confidence, details = self.detection_engine.test_boolean_based(
            url, param_name, method, data, headers, dbms="mysql", baseline=baseline
        )
        if is_vuln:
            return {
                "parameter": param_name,
                "type": "boolean-based blind",
                "payload": true_payload,
                "confidence": confidence,
                "injection_point": injection_point,
                "details": details
            }
        
        # 3. Test Time-Based Blind SQLi
        is_vuln, payload, confidence, details = self.detection_engine.test_time_based(
            url, param_name, method, data, headers, dbms="mysql", delay=5, threshold=3.0
        )
        if is_vuln:
            return {
                "parameter": param_name,
                "type": "time-based blind",
                "payload": payload,
                "confidence": confidence,
                "injection_point": injection_point,
                "details": details
            }
        
        # 4. Test UNION-Based SQLi
        is_vuln, cols, payload, confidence = self.detection_engine.test_union_based(
            url, param_name, method, data, headers, dbms="mysql"
        )
        if is_vuln:
            return {
                "parameter": param_name,
                "type": "UNION-based",
                "payload": payload,
                "confidence": confidence,
                "columns": cols,
                "injection_point": injection_point
            }
        
        self.logger.debug(f"No SQLi found in parameter: {param_name}")
        return None

    def _extract_parameters(self, url, method, data, headers):
        """
        Extract parameters from URL, POST data, cookies, and headers
        Returns: list of dicts with parameter info
        """
        parameters = []
        
        # Extract URL parameters (GET)
        parsed_url = urlparse(url)
        if parsed_url.query:
            query_params = parse_qs(parsed_url.query)
            for param_name, values in query_params.items():
                parameters.append({
                    "name": param_name,
                    "type": self._infer_param_type(values[0]),
                    "injection_point": "url",
                    "value": values[0]
                })
        
        # Extract POST parameters
        if method.upper() == "POST" and data:
            if isinstance(data, dict):
                for param_name, value in data.items():
                    parameters.append({
                        "name": param_name,
                        "type": self._infer_param_type(value),
                        "injection_point": "post",
                        "value": value
                    })
            elif isinstance(data, str):
                # URL-encoded POST data
                post_params = parse_qs(data)
                for param_name, values in post_params.items():
                    parameters.append({
                        "name": param_name,
                        "type": self._infer_param_type(values[0]),
                        "injection_point": "post",
                        "value": values[0]
                    })
        
        # Extract Cookie parameters
        if headers and "Cookie" in headers:
            cookie_parts = headers["Cookie"].split(";")
            for cookie in cookie_parts:
                if "=" in cookie:
                    name, value = cookie.strip().split("=", 1)
                    parameters.append({
                        "name": name,
                        "type": self._infer_param_type(value),
                        "injection_point": "cookie",
                        "value": value
                    })
        
        return parameters

    def _infer_param_type(self, value):
        """Infer parameter type (numeric or string)"""
        try:
            int(value)
            return "numeric"
        except ValueError:
            return "string"

    def get_vulnerabilities(self):
        """Return list of found vulnerabilities"""
        return self.vulnerabilities
