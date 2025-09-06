"""Action functions for the security agent."""

import logging
import sys
import os
from typing import Dict, Any, List

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from actions.slack import send_notification

logger = logging.getLogger(__name__)


async def scan_vulnerabilities(target: str, scan_type: str) -> List[Dict[str, Any]]:
    """Scan target for security vulnerabilities.
    
    Args:
        target: Target system/URL/repository
        scan_type: Type of scan to perform
        
    Returns:
        List of vulnerability findings
    """
    try:
        logger.info(f"Scanning {target} for vulnerabilities")
        
        # Mock vulnerability scanning - in production would integrate with security tools
        vulnerabilities = []
        
        # Common vulnerability categories
        common_vulns = [
            {
                "id": "VULN-001",
                "title": "SQL Injection",
                "description": "Input validation bypass allowing SQL injection attacks",
                "severity": "high",
                "cvss_score": 8.1,
                "category": "injection",
                "location": "/api/users",
                "recommendation": "Implement parameterized queries and input validation"
            },
            {
                "id": "VULN-002", 
                "title": "Cross-Site Scripting (XSS)",
                "description": "Stored XSS vulnerability in user comments",
                "severity": "medium",
                "cvss_score": 6.1,
                "category": "xss",
                "location": "/comments/view",
                "recommendation": "Sanitize user input and implement CSP headers"
            },
            {
                "id": "VULN-003",
                "title": "Insecure Direct Object Reference",
                "description": "Missing authorization checks on sensitive endpoints",
                "severity": "high",
                "cvss_score": 7.5,
                "category": "access_control",
                "location": "/admin/users",
                "recommendation": "Implement proper authorization checks"
            },
            {
                "id": "VULN-004",
                "title": "Sensitive Data Exposure",
                "description": "Debug information exposed in production",
                "severity": "medium",
                "cvss_score": 5.3,
                "category": "information_disclosure",
                "location": "/debug/info",
                "recommendation": "Disable debug mode in production"
            },
            {
                "id": "VULN-005",
                "title": "Security Misconfiguration",
                "description": "Default credentials still in use",
                "severity": "critical",
                "cvss_score": 9.8,
                "category": "configuration",
                "location": "Database connection",
                "recommendation": "Change default passwords immediately"
            }
        ]
        
        # Select vulnerabilities based on scan type and target
        if scan_type == "comprehensive":
            vulnerabilities = common_vulns
        elif scan_type == "web":
            vulnerabilities = [v for v in common_vulns if v["category"] in ["injection", "xss"]]
        elif scan_type == "infrastructure":
            vulnerabilities = [v for v in common_vulns if v["category"] in ["configuration", "access_control"]]
        else:
            vulnerabilities = common_vulns[:3]  # Limited scan
        
        logger.info(f"Found {len(vulnerabilities)} vulnerabilities")
        return vulnerabilities
        
    except Exception as e:
        logger.error(f"Vulnerability scan failed: {e}")
        return []


async def check_compliance(target: str, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check compliance against security standards.
    
    Args:
        target: Target system
        vulnerabilities: List of found vulnerabilities
        
    Returns:
        Compliance status and scores
    """
    try:
        logger.info(f"Checking compliance for {target}")
        
        # Calculate compliance scores based on vulnerabilities
        total_vulns = len(vulnerabilities)
        critical_vulns = len([v for v in vulnerabilities if v.get("severity") == "critical"])
        high_vulns = len([v for v in vulnerabilities if v.get("severity") == "high"])
        medium_vulns = len([v for v in vulnerabilities if v.get("severity") == "medium"])
        low_vulns = len([v for v in vulnerabilities if v.get("severity") == "low"])
        
        # OWASP Top 10 compliance
        owasp_categories = {
            "injection": len([v for v in vulnerabilities if v.get("category") == "injection"]),
            "authentication": len([v for v in vulnerabilities if v.get("category") == "authentication"]),
            "data_exposure": len([v for v in vulnerabilities if v.get("category") == "information_disclosure"]),
            "xxe": len([v for v in vulnerabilities if v.get("category") == "xxe"]),
            "access_control": len([v for v in vulnerabilities if v.get("category") == "access_control"]),
            "security_config": len([v for v in vulnerabilities if v.get("category") == "configuration"]),
            "xss": len([v for v in vulnerabilities if v.get("category") == "xss"]),
            "deserialization": len([v for v in vulnerabilities if v.get("category") == "deserialization"]),
            "components": len([v for v in vulnerabilities if v.get("category") == "components"]),
            "logging": len([v for v in vulnerabilities if v.get("category") == "logging"])
        }
        
        # Calculate overall compliance score
        max_deduction = 100
        deductions = 0
        deductions += critical_vulns * 25  # Critical vulns = 25 points each
        deductions += high_vulns * 15     # High vulns = 15 points each
        deductions += medium_vulns * 8    # Medium vulns = 8 points each
        deductions += low_vulns * 3       # Low vulns = 3 points each
        
        overall_score = max(0, 100 - min(deductions, max_deduction))
        
        # Industry-specific compliance
        compliance_frameworks = {
            "owasp_top_10": {
                "score": max(0, 100 - (sum(1 for v in owasp_categories.values() if v > 0) * 10)),
                "issues": [k for k, v in owasp_categories.items() if v > 0]
            },
            "pci_dss": {
                "score": max(0, 100 - (critical_vulns * 30 + high_vulns * 20)),
                "issues": ["Data protection", "Access control"] if critical_vulns + high_vulns > 0 else []
            },
            "iso_27001": {
                "score": max(0, 100 - (total_vulns * 5)),
                "issues": ["Information security management"] if total_vulns > 5 else []
            },
            "nist_cybersecurity": {
                "score": max(0, 100 - (critical_vulns * 25 + high_vulns * 15)),
                "issues": ["Identify", "Protect", "Detect"] if critical_vulns + high_vulns > 0 else []
            }
        }
        
        compliance_status = {
            "overall_score": round(overall_score, 1),
            "total_vulnerabilities": total_vulns,
            "severity_breakdown": {
                "critical": critical_vulns,
                "high": high_vulns,
                "medium": medium_vulns,
                "low": low_vulns
            },
            "frameworks": compliance_frameworks,
            "recommendations": []
        }
        
        # Add compliance recommendations
        if overall_score < 70:
            compliance_status["recommendations"].append("Immediate remediation required for critical security issues")
        if critical_vulns > 0:
            compliance_status["recommendations"].append("Address all critical vulnerabilities within 24 hours")
        if high_vulns > 3:
            compliance_status["recommendations"].append("Implement security monitoring and alerting")
        
        compliance_status["recommendations"].extend([
            "Conduct regular penetration testing",
            "Implement security training for development team",
            "Establish incident response procedures"
        ])
        
        logger.info(f"Compliance check completed: {overall_score}% overall score")
        return compliance_status
        
    except Exception as e:
        logger.error(f"Compliance check failed: {e}")
        return {"overall_score": 0, "error": str(e)}


async def generate_security_report(
    target: str, 
    vulnerabilities: List[Dict[str, Any]], 
    compliance_status: Dict[str, Any],
    executive_summary: str = ""
) -> str:
    """Generate comprehensive security report.
    
    Args:
        target: Target system
        vulnerabilities: List of vulnerabilities
        compliance_status: Compliance status
        executive_summary: Executive summary from LLM
        
    Returns:
        Formatted security report
    """
    try:
        logger.info("Generating security report")
        
        report = f"""
# Security Assessment Report

**Target:** {target}  
**Date:** 2024-01-01  
**Assessment Type:** Comprehensive Security Scan  

## Executive Summary

{executive_summary}

## Key Findings

- **Total Vulnerabilities:** {len(vulnerabilities)}
- **Overall Compliance Score:** {compliance_status.get('overall_score', 0)}%
- **Critical Issues:** {compliance_status.get('severity_breakdown', {}).get('critical', 0)}
- **High Priority Issues:** {compliance_status.get('severity_breakdown', {}).get('high', 0)}

## Vulnerability Details

"""
        
        # Add vulnerability details
        for i, vuln in enumerate(vulnerabilities[:10], 1):  # Limit to top 10
            report += f"""
### {i}. {vuln.get('title', 'Unknown Vulnerability')}

- **Severity:** {vuln.get('severity', 'Unknown').title()}
- **CVSS Score:** {vuln.get('cvss_score', 'N/A')}
- **Location:** {vuln.get('location', 'Unknown')}
- **Description:** {vuln.get('description', 'No description available')}
- **Recommendation:** {vuln.get('recommendation', 'No specific recommendation')}

"""
        
        # Add compliance section
        report += f"""
## Compliance Assessment

### Overall Score: {compliance_status.get('overall_score', 0)}%

### Framework Scores:
"""
        
        frameworks = compliance_status.get('frameworks', {})
        for framework, data in frameworks.items():
            score = data.get('score', 0)
            status = "✅ Compliant" if score >= 80 else "⚠️ Needs Attention" if score >= 60 else "❌ Non-Compliant"
            report += f"- **{framework.upper()}:** {score}% {status}\n"
        
        # Add recommendations
        report += """
## Recommendations

### Immediate Actions (0-24 hours)
"""
        
        critical_vulns = [v for v in vulnerabilities if v.get('severity') == 'critical']
        for vuln in critical_vulns:
            report += f"- Address {vuln.get('title', 'critical vulnerability')}: {vuln.get('recommendation', 'No specific guidance')}\n"
        
        report += """
### Short-term Actions (1-30 days)
"""
        
        high_vulns = [v for v in vulnerabilities if v.get('severity') == 'high']
        for vuln in high_vulns:
            report += f"- Resolve {vuln.get('title', 'high-priority vulnerability')}\n"
        
        report += """
### Long-term Actions (30+ days)
- Implement continuous security monitoring
- Establish regular penetration testing schedule
- Enhance security awareness training
- Develop incident response procedures
- Implement automated security scanning in CI/CD

## Conclusion

This assessment has identified significant security issues that require immediate attention. 
Priority should be given to addressing critical and high-severity vulnerabilities to improve 
the overall security posture and compliance standing.

Regular security assessments and continuous monitoring are recommended to maintain and 
improve security over time.
"""
        
        # Send report notification
        await send_notification(
            "#security",
            "Security Assessment Complete",
            f"Security assessment completed for {target}\n"
            f"Overall Score: {compliance_status.get('overall_score', 0)}%\n"
            f"Critical Issues: {compliance_status.get('severity_breakdown', {}).get('critical', 0)}\n"
            f"Total Vulnerabilities: {len(vulnerabilities)}"
        )
        
        logger.info("Security report generated successfully")
        return report
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return f"Error generating report: {str(e)}"