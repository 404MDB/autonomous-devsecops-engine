#!/usr/bin/env python3

import json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

TRIVY_REPORT = INPUT_DIR / "trivy-image-report.json"
ZAP_REPORT = INPUT_DIR / "zap-report.xml"
SBOM_REPORT = INPUT_DIR / "dummy-upi-app-cyclonedx.json"
COSIGN_REPORT = INPUT_DIR / "cosign-verification.txt"

SUMMARY_JSON = OUTPUT_DIR / "ai-security-summary.json"
REPORT_MD = OUTPUT_DIR / "ai-security-report.md"
RELEASE_DECISION = OUTPUT_DIR / "release-decision.txt"


SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_trivy_report(path: Path) -> dict:
    data = read_json(path)

    severity_counter = Counter()
    target_counter = Counter()
    fixable_counter = Counter()
    vulnerabilities = []

    for result in data.get("Results", []):
        target = result.get("Target", "Unknown target")
        result_type = result.get("Type", "Unknown type")

        for vuln in result.get("Vulnerabilities", []) or []:
            severity = vuln.get("Severity", "UNKNOWN").upper()
            vuln_id = vuln.get("VulnerabilityID", "UNKNOWN")
            package_name = vuln.get("PkgName", "UNKNOWN")
            installed_version = vuln.get("InstalledVersion", "UNKNOWN")
            fixed_version = vuln.get("FixedVersion", "")
            title = vuln.get("Title", "")

            severity_counter[severity] += 1
            target_counter[target] += 1

            if fixed_version:
                fixable_counter["fixable"] += 1
            else:
                fixable_counter["not_fixable_or_unknown"] += 1

            vulnerabilities.append(
                {
                    "id": vuln_id,
                    "severity": severity,
                    "package": package_name,
                    "installed_version": installed_version,
                    "fixed_version": fixed_version or "Not available",
                    "target": target,
                    "type": result_type,
                    "title": title,
                }
            )

    vulnerabilities.sort(
        key=lambda item: (
            SEVERITY_ORDER.index(item["severity"])
            if item["severity"] in SEVERITY_ORDER
            else len(SEVERITY_ORDER),
            item["package"],
        )
    )

    return {
        "total_vulnerabilities": sum(severity_counter.values()),
        "severity_counts": dict(severity_counter),
        "target_counts": dict(target_counter),
        "fix_status": dict(fixable_counter),
        "top_vulnerabilities": vulnerabilities[:15],
    }


def parse_zap_report(path: Path) -> dict:
    if not path.exists():
        return {
            "total_alerts": 0,
            "risk_counts": {},
            "top_alerts": [],
        }

    tree = ET.parse(path)
    root = tree.getroot()

    risk_counter = Counter()
    alerts = []

    for alert in root.findall(".//alertitem"):
        name = alert.findtext("name", default="Unknown alert")
        riskdesc = alert.findtext("riskdesc", default="Unknown")
        confidence = alert.findtext("confidence", default="Unknown")
        desc = alert.findtext("desc", default="")
        solution = alert.findtext("solution", default="")
        count = len(alert.findall(".//instance"))

        risk = riskdesc.split()[0].upper() if riskdesc else "UNKNOWN"
        risk_counter[risk] += 1

        alerts.append(
            {
                "name": name,
                "risk": risk,
                "risk_description": riskdesc,
                "confidence": confidence,
                "instances": count,
                "description": clean_html_text(desc),
                "solution": clean_html_text(solution),
            }
        )

    risk_priority = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFORMATIONAL": 3, "INFO": 3, "UNKNOWN": 4}
    alerts.sort(key=lambda item: (risk_priority.get(item["risk"], 5), item["name"]))

    return {
        "total_alerts": len(alerts),
        "risk_counts": dict(risk_counter),
        "top_alerts": alerts[:10],
    }


def clean_html_text(value: str) -> str:
    if not value:
        return ""
    replacements = {
        "<p>": "",
        "</p>": "",
        "<br>": " ",
        "<br/>": " ",
        "<br />": " ",
        "&nbsp;": " ",
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
    }
    cleaned = value
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return " ".join(cleaned.split())


def parse_sbom_report(path: Path) -> dict:
    data = read_json(path)

    components = data.get("components", []) or []
    component_type_counter = Counter()
    license_counter = Counter()

    for component in components:
        component_type_counter[component.get("type", "unknown")] += 1

        licenses = component.get("licenses", []) or []
        for item in licenses:
            license_data = item.get("license", {})
            license_name = license_data.get("id") or license_data.get("name")
            if license_name:
                license_counter[license_name] += 1

    return {
        "format": data.get("bomFormat", "Unknown"),
        "spec_version": data.get("specVersion", "Unknown"),
        "component_count": len(components),
        "component_types": dict(component_type_counter),
        "top_licenses": dict(license_counter.most_common(10)),
    }


def parse_cosign_report(path: Path) -> dict:
    text = read_text(path)

    verification_passed = (
        "Cosign Signature Verification: PASSED" in text
        and "Result: Verified OK" in text
    )

    return {
        "verification_passed": verification_passed,
        "raw_result": text.strip(),
    }


def calculate_risk_score(trivy: dict, zap: dict, cosign: dict) -> dict:
    trivy_counts = defaultdict(int, trivy.get("severity_counts", {}))
    zap_counts = defaultdict(int, zap.get("risk_counts", {}))

    score = 0
    score += trivy_counts["CRITICAL"] * 10
    score += trivy_counts["HIGH"] * 7
    score += trivy_counts["MEDIUM"] * 4
    score += trivy_counts["LOW"] * 1

    score += zap_counts["HIGH"] * 7
    score += zap_counts["MEDIUM"] * 4
    score += zap_counts["LOW"] * 1

    if not cosign.get("verification_passed"):
        score += 25

    if trivy_counts["CRITICAL"] > 0:
        decision = "BLOCK_RELEASE"
        reason = "Critical vulnerabilities are present in the container image."
    elif not cosign.get("verification_passed"):
        decision = "BLOCK_RELEASE"
        reason = "Cosign signature verification failed or evidence is missing."
    elif trivy_counts["HIGH"] > 0 or zap_counts["HIGH"] > 0:
        decision = "MANUAL_REVIEW_REQUIRED"
        reason = "High severity findings require security review."
    else:
        decision = "APPROVE_WITH_MONITORING"
        reason = "No critical blocking condition found."

    if score >= 100:
        risk_level = "CRITICAL"
    elif score >= 60:
        risk_level = "HIGH"
    elif score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "release_decision": decision,
        "decision_reason": reason,
    }


def build_recommendations(trivy: dict, zap: dict, sbom: dict, cosign: dict, risk: dict) -> list:
    recommendations = []

    severity_counts = defaultdict(int, trivy.get("severity_counts", {}))

    if severity_counts["CRITICAL"] > 0:
        recommendations.append(
            "Block release until all fixable CRITICAL container and dependency vulnerabilities are remediated."
        )

    if severity_counts["HIGH"] > 0:
        recommendations.append(
            "Prioritize HIGH vulnerabilities after CRITICAL issues and update affected packages or base images."
        )

    if trivy.get("fix_status", {}).get("fixable", 0) > 0:
        recommendations.append(
            "Use the Fixed Version values from Trivy to update vulnerable OS packages and Node.js dependencies."
        )

    if zap.get("total_alerts", 0) > 0:
        recommendations.append(
            "Review OWASP ZAP alerts and add missing security headers such as Content-Security-Policy and Permissions-Policy."
        )

    if sbom.get("component_count", 0) > 1000:
        recommendations.append(
            "Review SBOM dependency inventory and reduce unnecessary packages to minimize supply chain attack surface."
        )

    if cosign.get("verification_passed"):
        recommendations.append(
            "Keep Cosign signing and verification as a mandatory supply chain control before deployment."
        )
    else:
        recommendations.append(
            "Investigate Cosign verification failure before allowing artifact promotion."
        )

    recommendations.append(
        "Import summarized AI security output into documentation and use it as release review evidence."
    )

    return recommendations


def generate_markdown_report(summary: dict) -> str:
    trivy = summary["trivy"]
    zap = summary["zap"]
    sbom = summary["sbom"]
    cosign = summary["cosign"]
    risk = summary["risk"]
    recommendations = summary["recommendations"]

    lines = []
    lines.append("# AI Security Intelligence Report")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(
        "This report was generated by the AI Security Intelligence Layer by analyzing Trivy, OWASP ZAP, SBOM, and Cosign evidence."
    )
    lines.append("")
    lines.append(f"Risk Level: **{risk['risk_level']}**")
    lines.append(f"Risk Score: **{risk['risk_score']}**")
    lines.append(f"Release Decision: **{risk['release_decision']}**")
    lines.append(f"Decision Reason: {risk['decision_reason']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Trivy Vulnerability Summary")
    lines.append("")
    lines.append(f"Total Vulnerabilities: **{trivy['total_vulnerabilities']}**")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|---|---:|")
    for sev in SEVERITY_ORDER:
        lines.append(f"| {sev} | {trivy.get('severity_counts', {}).get(sev, 0)} |")
    lines.append("")
    lines.append("### Top Trivy Findings")
    lines.append("")
    lines.append("| Severity | CVE | Package | Installed | Fixed |")
    lines.append("|---|---|---|---|---|")
    for item in trivy.get("top_vulnerabilities", [])[:10]:
        lines.append(
            f"| {item['severity']} | {item['id']} | {item['package']} | {item['installed_version']} | {item['fixed_version']} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## OWASP ZAP DAST Summary")
    lines.append("")
    lines.append(f"Total Alerts: **{zap['total_alerts']}**")
    lines.append("")
    lines.append("| Risk | Count |")
    lines.append("|---|---:|")
    for risk_name, count in zap.get("risk_counts", {}).items():
        lines.append(f"| {risk_name} | {count} |")
    lines.append("")
    lines.append("### Top ZAP Alerts")
    lines.append("")
    lines.append("| Risk | Alert | Instances |")
    lines.append("|---|---|---:|")
    for item in zap.get("top_alerts", [])[:10]:
        lines.append(f"| {item['risk']} | {item['name']} | {item['instances']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## SBOM Summary")
    lines.append("")
    lines.append(f"Format: **{sbom['format']}**")
    lines.append(f"Spec Version: **{sbom['spec_version']}**")
    lines.append(f"Component Count: **{sbom['component_count']}**")
    lines.append("")
    lines.append("| Component Type | Count |")
    lines.append("|---|---:|")
    for comp_type, count in sbom.get("component_types", {}).items():
        lines.append(f"| {comp_type} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Cosign Verification Summary")
    lines.append("")
    if cosign["verification_passed"]:
        lines.append("Cosign Signature Verification: **PASSED**")
        lines.append("")
        lines.append("The image artifact signature was verified successfully.")
    else:
        lines.append("Cosign Signature Verification: **FAILED OR MISSING**")
        lines.append("")
        lines.append("The image artifact must not be promoted until signature verification passes.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## AI Recommendations")
    lines.append("")
    for index, recommendation in enumerate(recommendations, start=1):
        lines.append(f"{index}. {recommendation}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Release Decision")
    lines.append("")
    lines.append(f"Decision: **{risk['release_decision']}**")
    lines.append("")
    lines.append(f"Reason: {risk['decision_reason']}")
    lines.append("")
    lines.append("Generated by Phase 8 AI Security Intelligence Layer.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    trivy = parse_trivy_report(TRIVY_REPORT)
    zap = parse_zap_report(ZAP_REPORT)
    sbom = parse_sbom_report(SBOM_REPORT)
    cosign = parse_cosign_report(COSIGN_REPORT)
    risk = calculate_risk_score(trivy, zap, cosign)
    recommendations = build_recommendations(trivy, zap, sbom, cosign, risk)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "AI Security Intelligence Layer",
        "phase": "Phase 8",
        "input_files": {
            "trivy": str(TRIVY_REPORT),
            "zap": str(ZAP_REPORT),
            "sbom": str(SBOM_REPORT),
            "cosign": str(COSIGN_REPORT),
        },
        "trivy": trivy,
        "zap": zap,
        "sbom": sbom,
        "cosign": cosign,
        "risk": risk,
        "recommendations": recommendations,
    }

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    REPORT_MD.write_text(generate_markdown_report(summary), encoding="utf-8")
    RELEASE_DECISION.write_text(
        f"{risk['release_decision']}\n{risk['decision_reason']}\n",
        encoding="utf-8",
    )

    print("AI Security Intelligence analysis completed.")
    print(f"Summary JSON: {SUMMARY_JSON}")
    print(f"Markdown Report: {REPORT_MD}")
    print(f"Release Decision: {RELEASE_DECISION}")
    print(f"Risk Level: {risk['risk_level']}")
    print(f"Risk Score: {risk['risk_score']}")
    print(f"Release Decision: {risk['release_decision']}")


if __name__ == "__main__":
    main()

