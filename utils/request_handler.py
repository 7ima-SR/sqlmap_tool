# utils/request_handler.py
import requests
import time
from utils.logger import Logger
from urllib.parse import urljoin
import json

class RequestHandler:
    """Advanced HTTP request handler with retry, timing, and error handling"""
    
    def __init__(self, proxy=None, timeout=10, retry_count=2):
        self.proxy = proxy
        self.timeout = timeout
        self.retry_count = retry_count
        self.logger = Logger("request_handler.log")
        self.session = requests.Session()
        
    def send_request(self, url, method="GET", data=None, headers=None, payload_injection=None):
        """
        Send HTTP request with retry mechanism
        Returns: (response, elapsed_time) tuple
        """
        if headers is None:
            headers = {}
        
        # Inject payload if specified
        if payload_injection:
            url, data, headers = self._inject_payload(
                url, data, headers, 
                payload_injection["param"],
                payload_injection["payload"],
                payload_injection.get("injection_point", "url")
            )
        
        for attempt in range(self.retry_count):
            try:
                start_time = time.time()
                
                if method.upper() == "GET":
                    response = self.session.get(
                        url, 
                        headers=headers,
                        proxies=self._get_proxies(),
                        timeout=self.timeout,
                        allow_redirects=False
                    )
                elif method.upper() == "POST":
                    response = self.session.post(
                        url,
                        data=data,
                        headers=headers,
                        proxies=self._get_proxies(),
                        timeout=self.timeout,
                        allow_redirects=False
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                elapsed_time = time.time() - start_time
                
                self.logger.debug(
                    f"[{method}] {url} - Status: {response.status_code}, "
                    f"Time: {elapsed_time:.2f}s, Size: {len(response.content)} bytes"
                )
                
                return response, elapsed_time
                
            except requests.Timeout:
                if attempt == self.retry_count - 1:
                    self.logger.error(f"Request timeout after {self.retry_count} attempts: {url}")
                    return None, None
                time.sleep(1)
                continue
                
            except requests.RequestException as e:
                if attempt == self.retry_count - 1:
                    self.logger.error(f"Request failed: {str(e)}")
                    return None, None
                time.sleep(1)
                continue
        
        return None, None

    def _inject_payload(self, url, data, headers, param_name, payload, injection_point):
        """Inject payload into URL, POST data, Cookie, or JSON"""
        import urllib.parse
        
        if injection_point == "url":
            # Inject into GET parameter
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{param_name}={urllib.parse.quote(payload)}"
            
        elif injection_point == "post":
            # Inject into POST data
            if data:
                if isinstance(data, dict):
                    data[param_name] = payload
                else:
                    # Handle URL-encoded data
                    data = f"{data}&{param_name}={urllib.parse.quote(payload)}"
            else:
                data = f"{param_name}={urllib.parse.quote(payload)}"
                
        elif injection_point == "cookie":
            # Inject into cookies
            if "Cookie" not in headers:
                headers["Cookie"] = ""
            headers["Cookie"] += f"; {param_name}={payload}"
            
        elif injection_point == "json":
            # Inject into JSON body
            if isinstance(data, str):
                data = json.loads(data)
            data[param_name] = payload
            data = json.dumps(data)
        
        return url, data, headers

    def _get_proxies(self):
        """Get proxy configuration"""
        if self.proxy:
            return {"http": self.proxy, "https": self.proxy}
        return None

    def get_baseline(self, url, method="GET", data=None, headers=None, trials=3):
        """
        Get baseline response metrics (average time and content)
        Returns: dict with avg_time, content_hash, content_length
        """
        times = []
        contents = []
        
        for _ in range(trials):
            response, elapsed = self.send_request(url, method, data, headers)
            if response and elapsed:
                times.append(elapsed)
                contents.append(response.content)
            time.sleep(0.2)  # Brief delay between requests
        
        if not times:
            return None
        
        avg_time = sum(times) / len(times)
        content_hash = hash(min(contents, key=len))  # Use shortest response as baseline
        content_length = len(min(contents, key=len))
        
        self.logger.debug(
            f"Baseline: avg_time={avg_time:.3f}s, "
            f"content_length={content_length}, trials={len(times)}"
        )
        
        return {
            "avg_time": avg_time,
            "content_hash": content_hash,
            "content_length": content_length,
            "max_time": max(times),
            "min_time": min(times)
        }