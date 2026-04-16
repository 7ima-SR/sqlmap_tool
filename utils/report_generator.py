# utils/report_generator.py
import json
import os
from datetime import datetime

class ReportGenerator:
    """Generate reports in JSON and HTML formats"""
    
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.report_data = {
            "scan_info": {
                "timestamp": datetime.now().isoformat(),
                "target_url": None,
                "method": None,
                "tool_version": "2.0"
            },
            "vulnerabilities": [],
            "databases": [],
            "tables": [],
            "data_dumps": [],
            "statistics": {
                "total_parameters_tested": 0,
                "vulnerabilities_found": 0,
                "scan_duration": 0
            }
        }

    def add_scan_info(self, url, method="GET"):
        """Add scan metadata"""
        self.report_data["scan_info"]["target_url"] = url
        self.report_data["scan_info"]["method"] = method

    def add_vulnerability(self, param_name, vulnerability_type, payload, confidence, dbms=None, details=None):
        """Add vulnerability to report"""
        vuln = {
            "parameter": param_name,
            "type": vulnerability_type,
            "payload": payload,
            "confidence": confidence,
            "dbms": dbms,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.report_data["vulnerabilities"].append(vuln)
        self.report_data["statistics"]["vulnerabilities_found"] += 1

    def add_databases(self, databases):
        """Add extracted databases"""
        self.report_data["databases"] = databases

    def add_tables(self, database, tables):
        """Add extracted tables"""
        self.report_data["tables"].append({
            "database": database,
            "tables": tables
        })

    def add_data_dump(self, database, table, columns, rows):
        """Add dumped table data"""
        self.report_data["data_dumps"].append({
            "database": database,
            "table": table,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        })

    def set_statistics(self, total_params, scan_duration):
        """Set scan statistics"""
        self.report_data["statistics"]["total_parameters_tested"] = total_params
        self.report_data["statistics"]["scan_duration"] = scan_duration

    def export_json(self, filename=None):
        """Export report as JSON"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        return filepath

    def export_html(self, filename=None):
        """Export report as HTML"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        html_content = self._generate_html()
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return filepath

    def _generate_html(self):
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SQL Injection Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }}
        .stat-card {{ background-color: white; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }}
        .vulnerable {{ border-left-color: #e74c3c; }}
        .section {{ background-color: white; margin: 20px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th {{ background-color: #34495e; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background-color: #f9f9f9; }}
        .payload {{ background-color: #ecf0f1; padding: 5px 10px; border-radius: 3px; font-family: monospace; }}
        .confidence-high {{ color: #e74c3c; font-weight: bold; }}
        .confidence-medium {{ color: #f39c12; font-weight: bold; }}
        .confidence-low {{ color: #27ae60; }}
        .footer {{ text-align: center; margin-top: 30px; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SQL Injection Security Scan Report</h1>
        <p>Tool: SQLMap V2.0 | Generated: {self.report_data['scan_info']['timestamp']}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>Target URL</h3>
            <p>{self.report_data['scan_info'].get('target_url', 'N/A')}</p>
        </div>
        <div class="stat-card">
            <h3>Parameters Tested</h3>
            <p>{self.report_data['statistics']['total_parameters_tested']}</p>
        </div>
        <div class="stat-card vulnerable">
            <h3>Vulnerabilities Found</h3>
            <p>{self.report_data['statistics']['vulnerabilities_found']}</p>
        </div>
        <div class="stat-card">
            <h3>Scan Duration</h3>
            <p>{self.report_data['statistics']['scan_duration']:.2f}s</p>
        </div>
    </div>

    <div class="section">
        <h2>Vulnerabilities</h2>
        {self._generate_vulnerabilities_html()}
    </div>

    {self._generate_databases_html()}
    {self._generate_data_dumps_html()}

    <div class="footer">
        <p><strong>Disclaimer:</strong> This tool is for authorized security testing only. Unauthorized access to computer systems is illegal.</p>
    </div>
</body>
</html>
"""
        return html

    def _generate_vulnerabilities_html(self):
        """Generate vulnerabilities section HTML"""
        if not self.report_data["vulnerabilities"]:
            return "<p>No vulnerabilities found.</p>"
        
        html = "<table><thead><tr><th>Parameter</th><th>Type</th><th>Confidence</th><th>Payload</th><th>DBMS</th></tr></thead><tbody>"
        
        for vuln in self.report_data["vulnerabilities"]:
            confidence_class = "confidence-high" if vuln["confidence"] > 0.8 else ("confidence-medium" if vuln["confidence"] > 0.5 else "confidence-low")
            
            html += f"""
            <tr>
                <td>{vuln['parameter']}</td>
                <td>{vuln['type']}</td>
                <td class="{confidence_class}">{vuln['confidence']:.2%}</td>
                <td><code class="payload">{vuln['payload'][:50]}...</code></td>
                <td>{vuln['dbms'] or 'Unknown'}</td>
            </tr>
            """
        
        html += "</tbody></table>"
        return html

    def _generate_databases_html(self):
        """Generate databases section HTML"""
        if not self.report_data["databases"]:
            return ""
        
        html = '<div class="section"><h2>Extracted Databases</h2><ul>'
        
        for db in self.report_data["databases"]:
            html += f"<li>{db}</li>"
        
        html += "</ul></div>"
        return html

    def _generate_data_dumps_html(self):
        """Generate data dumps section HTML"""
        if not self.report_data["data_dumps"]:
            return ""
        
        html = '<div class="section"><h2>Data Dumps</h2>'
        
        for dump in self.report_data["data_dumps"]:
            html += f"<h3>{dump['database']}.{dump['table']}</h3>"
            html += "<table><thead><tr>"
            
            for col in dump["columns"]:
                html += f"<th>{col}</th>"
            
            html += "</tr></thead><tbody>"
            
            for row in dump["rows"]:
                html += "<tr>"
                for col in dump["columns"]:
                    html += f"<td>{row.get(col, 'N/A')}</td>"
                html += "</tr>"
            
            html += "</tbody></table>"
        
        html += "</div>"
        return html

    def print_summary(self):
        """Print summary to console"""
        print("\n" + "="*60)
        print("SQL INJECTION SCAN SUMMARY")
        print("="*60)
        print(f"Target: {self.report_data['scan_info'].get('target_url', 'N/A')}")
        print(f"Parameters Tested: {self.report_data['statistics']['total_parameters_tested']}")
        print(f"Vulnerabilities Found: {self.report_data['statistics']['vulnerabilities_found']}")
        print(f"Scan Duration: {self.report_data['statistics']['scan_duration']:.2f}s")
        print("="*60)
        
        if self.report_data["vulnerabilities"]:
            print("\nVULNERABILITIES DETECTED:")
            print("-"*60)
            for i, vuln in enumerate(self.report_data["vulnerabilities"], 1):
                print(f"\n{i}. Parameter: {vuln['parameter']}")
                print(f"   Type: {vuln['type']}")
                print(f"   Confidence: {vuln['confidence']:.2%}")
                print(f"   Payload: {vuln['payload'][:80]}")
                if vuln['dbms']:
                    print(f"   DBMS: {vuln['dbms']}")
        
        if self.report_data["databases"]:
            print("\nEXTRACTED DATABASES:")
            print("-"*60)
            for db in self.report_data["databases"][:10]:
                print(f"  - {db}")
        
        print("\n" + "="*60 + "\n")
