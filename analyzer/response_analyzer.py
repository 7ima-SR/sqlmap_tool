# analyzer/response_analyzer.py
import difflib
import hashlib
from collections import Counter

class ResponseAnalyzer:
    """Advanced response analysis with similarity comparison and false positive reduction"""
    
    def __init__(self, similarity_threshold=0.7):
        # SQL error keywords for different DBMS
        self.error_keywords = {
            "mysql": ["mysql", "sql", "syntax", "error", "warning", "exception", "near"],
            "postgresql": ["postgres", "sql", "syntax", "error", "warning", "exception", "near"],
            "mssql": ["mssql", "sql", "syntax", "error", "unclosed", "quoted identifier"],
            "generic": ["error", "sql", "syntax", "warning", "exception", "invalid", "syntax error"]
        }
        
        self.similarity_threshold = similarity_threshold
        
    def compare_responses(self, baseline_response, test_response, comparison_type="advanced"):
        """
        Compare two responses to detect differences
        Returns: dict with similarity metrics
        """
        if not baseline_response or not test_response:
            return {"is_different": False, "confidence": 0, "reason": "Response missing"}
        
        result = {
            "is_different": False,
            "confidence": 0,
            "similarity": 0,
            "length_diff": 0,
            "hash_diff": False,
            "keyword_diff": False,
            "reason": "No significant difference detected"
        }
        
        # Get response content
        baseline_content = baseline_response.text if hasattr(baseline_response, 'text') else str(baseline_response)
        test_content = test_response.text if hasattr(test_response, 'text') else str(test_response)
        
        # Content similarity ratio (0-1)
        similarity = difflib.SequenceMatcher(None, baseline_content, test_content).ratio()
        result["similarity"] = similarity
        
        # Length difference
        length_diff = abs(len(baseline_content) - len(test_content))
        result["length_diff"] = length_diff
        
        # Hash comparison for significant content changes
        baseline_hash = hashlib.md5(baseline_content.encode()).hexdigest()
        test_hash = hashlib.md5(test_content.encode()).hexdigest()
        result["hash_diff"] = baseline_hash != test_hash
        
        # Determine if responses are significantly different
        if similarity < self.similarity_threshold:
            result["is_different"] = True
            result["confidence"] = 1 - similarity
            result["reason"] = f"Content similarity: {similarity:.2%}"
        
        # Large length difference (potential injection effect)
        elif length_diff > max(len(baseline_content) * 0.15, 50):  # 15% or 50 bytes
            result["is_different"] = True
            result["confidence"] = min(length_diff / len(baseline_content), 1.0)
            result["reason"] = f"Length difference: {length_diff} bytes"
        
        return result

    def detect_error_response(self, response, dbms="generic"):
        """
        Detect SQL error in response
        Returns: (is_error, confidence)
        """
        if not response:
            return False, 0
        
        content = response.text.lower() if hasattr(response, 'text') else str(response).lower()
        keywords = self.error_keywords.get(dbms, self.error_keywords["generic"])
        
        # Count matching error keywords
        matches = sum(1 for kw in keywords if kw in content)
        
        if matches > 0:
            confidence = min(matches / len(keywords), 1.0)
            return True, confidence
        
        return False, 0

    def detect_boolean_difference(self, true_response, false_response, sensitivity=0.1):
        """
        Detect boolean-based SQLi by comparing true and false responses
        Returns: (is_vulnerable, confidence, metric_used)
        """
        if not true_response or not false_response:
            return False, 0, "Missing response"
        
        true_content = true_response.text if hasattr(true_response, 'text') else str(true_response)
        false_content = false_response.text if hasattr(false_response, 'text') else str(false_response)
        
        # 1. Content length difference
        length_diff = abs(len(true_content) - len(false_content))
        length_ratio = length_diff / max(len(true_content), len(false_content), 1)
        
        if length_ratio > sensitivity:
            return True, length_ratio, "Length difference"
        
        # 2. HTTP status code difference
        if hasattr(true_response, 'status_code') and hasattr(false_response, 'status_code'):
            if true_response.status_code != false_response.status_code:
                return True, 0.9, "Status code difference"
        
        # 3. Content similarity
        similarity = difflib.SequenceMatcher(None, true_content, false_content).ratio()
        
        if similarity < 0.95:  # Significant content difference
            return True, 1 - similarity, "Content similarity"
        
        # 4. Response time difference (more than 500ms)
        if hasattr(true_response, 'elapsed') and hasattr(false_response, 'elapsed'):
            time_diff = abs(true_response.elapsed.total_seconds() - false_response.elapsed.total_seconds())
            if time_diff > 0.5:
                return True, time_diff, "Response time difference"
        
        return False, 0, "No difference detected"

    def detect_time_delay(self, baseline_time, test_time, threshold=3.0, trials=1):
        """
        Detect time-based SQLi delay
        Returns: (is_delayed, confidence, delay_time)
        threshold: minimum delay in seconds
        trials: number of trials for statistical confidence
        """
        time_diff = test_time - baseline_time
        confidence = 0
        
        # Raw time difference
        if time_diff > threshold:
            # Calculate confidence based on threshold
            confidence = min(time_diff / (threshold * 2), 1.0)
            return True, confidence, time_diff
        
        # If close to threshold but not quite, lower confidence
        if time_diff > threshold * 0.75:
            confidence = time_diff / threshold
            return True, confidence * 0.5, time_diff
        
        return False, 0, 0

    def get_response_metrics(self, response):
        """Extract detailed metrics from response"""
        if not response:
            return None
        
        content = response.text if hasattr(response, 'text') else str(response)
        
        metrics = {
            "status_code": getattr(response, 'status_code', None),
            "content_length": len(content),
            "content_hash": hashlib.md5(content.encode()).hexdigest(),
            "header_count": len(getattr(response, 'headers', {})),
            "lines": len(content.split('\n')),
            "words": len(content.split()),
            "encoding": getattr(response, 'encoding', 'unknown'),
            "elapsed_time": getattr(getattr(response, 'elapsed', None), 'total_seconds', lambda: 0)()
        }
        
        return metrics

    def compare_multiple_responses(self, responses):
        """
        Compare multiple responses to find patterns
        Useful for statistical analysis
        Returns: dict with statistics
        """
        if not responses or len(responses) < 2:
            return None
        
        content_lengths = [len(r.text) if hasattr(r, 'text') else len(str(r)) for r in responses]
        status_codes = [getattr(r, 'status_code', None) for r in responses]
        
        stats = {
            "avg_length": sum(content_lengths) / len(content_lengths),
            "min_length": min(content_lengths),
            "max_length": max(content_lengths),
            "length_variance": max(content_lengths) - min(content_lengths),
            "status_code_distribution": Counter(status_codes),
            "consistent": len(set(content_lengths)) == 1
        }
        
        return stats

    def fingerprint_dbms(self, response):
        """
        Try to fingerprint DBMS from response
        Returns: (dbms_name, confidence)
        """
        if not response:
            return "unknown", 0
        
        content = response.text.lower() if hasattr(response, 'text') else str(response).lower()
        
        dbms_signatures = {
            "mysql": ["mysql", "mariadb", "phpmyadmin"],
            "postgresql": ["postgres", "psql", "pg"],
            "mssql": ["microsoft sql", "mssql"],
            "oracle": ["oracle", "oracle database"],
            "sqlite": ["sqlite"],
        }
        
        for dbms, signatures in dbms_signatures.items():
            matches = sum(sig in content for sig in signatures)
            if matches > 0:
                confidence = min(matches / len(signatures), 1.0)
                return dbms, confidence
        
        return "unknown", 0