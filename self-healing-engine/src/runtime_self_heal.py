#!/usr/bin/env python3

import argparse
import json
import os
import re
import smtplib
import subprocess
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path


SAFE_NAMESPACES = {"devsecops"}
REQUIRED_DEMO_LABEL_KEY = "self-heal-demo"
REQUIRED_DEMO_LABEL_VALUE = "true"


def run_command(command):
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )

    return {
        "command": command,
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def extract_value(line, key):
    match = re.search(rf"{re.escape(key)}=([^ ]+)", line)
    return match.group(1) if match else None


def detect_severity(line):
    if "Critical" in line:
        return "critical"
    if "Warning" in line:
        return "warning"
    if "Notice" in line:
        return "notice"
    return "unknown"


def detect_rule(line):
    if "Sensitive file opened for reading" in line:
        return "Sensitive file opened for reading by non-trusted program"

    if "Unexpected connection to K8s API Server" in line:
        return "Unexpected connection to K8s API Server from container"

    if "shell" in line.lower():
        return "Shell activity detected inside container"

    return "Falco runtime security event"


def parse_falco_events(log_path):
    events = []

    if not log_path.exists():
        return events

    for line in log_path.read_text(errors="ignore").splitlines():
        line = line.strip()

        if not line:
            continue

        if not any(keyword in line for keyword in ["Warning", "Notice", "Critical"]):
            continue

        event = {
            "raw_event": line,
            "severity": detect_severity(line),
            "detected_rule": detect_rule(line),
            "namespace": extract_value(line, "k8s_ns_name"),
            "pod": extract_value(line, "k8s_pod_name"),
            "container": extract_value(line, "container_name"),
            "image": extract_value(line, "container_image_repository"),
            "image_tag": extract_value(line, "container_image_tag"),
            "process": extract_value(line, "process"),
            "file": extract_value(line, "file"),
            "command": extract_value(line, "command"),
        }

        events.append(event)

    return events


def build_decision(event):
    namespace = event.get("namespace")
    pod = event.get("pod")
    rule = event.get("detected_rule")
    severity = event.get("severity")

    decision = {
        "event": event,
        "risk_level": "LOW",
        "action": "NO_ACTION",
        "reason": "No automated remediation required.",
        "safe_to_execute": False,
    }

    if not namespace or not pod:
        decision.update({
            "risk_level": "UNKNOWN",
            "action": "MANUAL_REVIEW",
            "reason": "Falco event does not contain Kubernetes namespace or pod name.",
            "safe_to_execute": False,
        })
        return decision

    if namespace not in SAFE_NAMESPACES:
        decision.update({
            "risk_level": "MEDIUM",
            "action": "MANUAL_REVIEW",
            "reason": f"Event occurred outside approved demo namespace: {namespace}.",
            "safe_to_execute": False,
        })
        return decision

    if rule == "Sensitive file opened for reading by non-trusted program":
        decision.update({
            "risk_level": "HIGH",
            "action": "DELETE_POD_IF_DEMO_LABEL_PRESENT",
            "reason": "Sensitive file access was detected inside a Kubernetes container.",
            "safe_to_execute": True,
        })
        return decision

    if severity in {"warning", "critical"}:
        decision.update({
            "risk_level": "MEDIUM",
            "action": "MANUAL_REVIEW",
            "reason": "Falco warning or critical event requires investigation.",
            "safe_to_execute": False,
        })
        return decision

    decision.update({
        "risk_level": "LOW",
        "action": "MONITOR_ONLY",
        "reason": "Low-risk runtime event. Monitoring only.",
        "safe_to_execute": False,
    })

    return decision


def pod_has_required_demo_label(namespace, pod):
    command = (
        f"kubectl get pod {pod} -n {namespace} "
        f"-o jsonpath='{{.metadata.labels.{REQUIRED_DEMO_LABEL_KEY}}}'"
    )

    result = run_command(command)

    return {
        "has_label": result["stdout"] == REQUIRED_DEMO_LABEL_VALUE,
        "check": result,
    }


def execute_decision(decision, execute):
    event = decision["event"]
    namespace = event.get("namespace")
    pod = event.get("pod")

    execution = {
        "mode": "execute" if execute else "dry-run",
        "executed": False,
        "checks": [],
        "commands": [],
    }

    if decision["action"] != "DELETE_POD_IF_DEMO_LABEL_PRESENT":
        execution["checks"].append("No automated delete action selected.")
        return execution

    label_check = pod_has_required_demo_label(namespace, pod)
    execution["commands"].append(label_check["check"])

    required_label = f"{REQUIRED_DEMO_LABEL_KEY}={REQUIRED_DEMO_LABEL_VALUE}"

    if not label_check["has_label"]:
        execution["checks"].append(
            f"Pod was not deleted because it does not have required safety label: {required_label}"
        )
        return execution

    execution["checks"].append(f"Required safety label found: {required_label}")

    delete_command = f"kubectl delete pod {pod} -n {namespace}"

    if not execute:
        execution["checks"].append(f"Dry-run mode: would run `{delete_command}`")
        return execution

    delete_result = run_command(delete_command)
    execution["commands"].append(delete_result)
    execution["executed"] = delete_result["exit_code"] == 0

    if execution["executed"]:
        execution["checks"].append("Pod deletion remediation executed successfully.")
    else:
        execution["checks"].append("Pod deletion remediation failed.")

    return execution


def build_email_body(decisions, executions):
    high_risk = [
        decision for decision in decisions
        if decision.get("risk_level") in {"HIGH", "CRITICAL"}
    ]

    lines = [
        "Autonomous DevSecOps Runtime Security Alert",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        f"Total Events Analyzed: {len(decisions)}",
        f"High Risk Events: {len(high_risk)}",
        "",
        "Summary:",
        "Falco runtime security events were analyzed by the self-healing engine.",
        "",
        "Decisions:",
    ]

    for index, decision in enumerate(decisions, start=1):
        event = decision["event"]
        lines.extend([
            "",
            f"Event {index}:",
            f"- Rule: {event.get('detected_rule')}",
            f"- Severity: {event.get('severity')}",
            f"- Namespace: {event.get('namespace')}",
            f"- Pod: {event.get('pod')}",
            f"- Container: {event.get('container')}",
            f"- Process: {event.get('process')}",
            f"- File: {event.get('file')}",
            f"- Risk Level: {decision.get('risk_level')}",
            f"- Action: {decision.get('action')}",
            f"- Reason: {decision.get('reason')}",
        ])

    lines.extend([
        "",
        "Execution:",
    ])

    for index, execution in enumerate(executions, start=1):
        lines.extend([
            "",
            f"Execution {index}:",
            f"- Mode: {execution.get('mode')}",
            f"- Executed: {execution.get('executed')}",
        ])

        for check in execution.get("checks", []):
            lines.append(f"- Check: {check}")

    return "\n".join(lines)


def send_email_alert(subject, body):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("ALERT_EMAIL_FROM")
    email_to = os.getenv("ALERT_EMAIL_TO")

    missing = [
        name for name, value in {
            "SMTP_HOST": smtp_host,
            "SMTP_USERNAME": smtp_username,
            "SMTP_PASSWORD": smtp_password,
            "ALERT_EMAIL_FROM": email_from,
            "ALERT_EMAIL_TO": email_to,
        }.items()
        if not value
    ]

    if missing:
        return {
            "sent": False,
            "reason": f"SMTP environment variables missing: {', '.join(missing)}",
        }

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = email_from
    message["To"] = email_to
    message.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        return {
            "sent": True,
            "reason": "Email alert sent successfully.",
        }

    except Exception as exc:
        return {
            "sent": False,
            "reason": f"Email alert failed: {exc}",
        }


def write_reports(decisions, executions, output_dir, send_email):
    output_dir.mkdir(parents=True, exist_ok=True)

    email_body = build_email_body(decisions, executions)

    high_risk_count = sum(
        1 for decision in decisions
        if decision["risk_level"] in {"HIGH", "CRITICAL"}
    )

    subject_prefix = "BLOCKED" if high_risk_count > 0 else "INFO"
    email_subject = f"[{subject_prefix}] DevSecOps Runtime Security Alert"

    email_status = {
        "sent": False,
        "reason": "Email sending not requested. Email alert file generated only.",
    }

    if send_email:
        email_status = send_email_alert(email_subject, email_body)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "runtime-self-healing-engine",
        "mode": executions[0]["mode"] if executions else "dry-run",
        "total_events": len(decisions),
        "high_risk_events": high_risk_count,
        "email_subject": email_subject,
        "email_status": email_status,
        "decisions": decisions,
        "executions": executions,
    }

    json_path = output_dir / "self-healing-summary.json"
    md_path = output_dir / "self-healing-report.md"
    email_path = output_dir / "email-alert-preview.txt"

    json_path.write_text(json.dumps(summary, indent=2))
    email_path.write_text(f"Subject: {email_subject}\n\n{email_body}")

    lines = [
        "# Runtime Self-Healing Report",
        "",
        f"Generated At: {summary['generated_at']}",
        f"Mode: {summary['mode']}",
        f"Total Events Analyzed: {summary['total_events']}",
        f"High Risk Events: {summary['high_risk_events']}",
        f"Email Subject: {summary['email_subject']}",
        f"Email Sent: {summary['email_status']['sent']}",
        f"Email Status: {summary['email_status']['reason']}",
        "",
        "## Decisions",
        "",
    ]

    for index, decision in enumerate(decisions, start=1):
        event = decision["event"]
        lines.extend([
            f"### Event {index}",
            "",
            f"- Rule: {event.get('detected_rule')}",
            f"- Severity: {event.get('severity')}",
            f"- Namespace: {event.get('namespace')}",
            f"- Pod: {event.get('pod')}",
            f"- Container: {event.get('container')}",
            f"- Image: {event.get('image')}:{event.get('image_tag')}",
            f"- Process: {event.get('process')}",
            f"- File: {event.get('file')}",
            f"- Risk Level: {decision.get('risk_level')}",
            f"- Action: {decision.get('action')}",
            f"- Reason: {decision.get('reason')}",
            f"- Safe To Execute: {decision.get('safe_to_execute')}",
            "",
        ])

    lines.extend([
        "## Execution Summary",
        "",
    ])

    for index, execution in enumerate(executions, start=1):
        lines.extend([
            f"### Execution {index}",
            "",
            f"- Mode: {execution['mode']}",
            f"- Executed: {execution['executed']}",
        ])

        for check in execution["checks"]:
            lines.append(f"- Check: {check}")

        lines.append("")

    lines.extend([
        "## Generated Files",
        "",
        f"- JSON Summary: `{json_path}`",
        f"- Markdown Report: `{md_path}`",
        f"- Email Preview: `{email_path}`",
        "",
    ])

    md_path.write_text("\n".join(lines))

    print(f"Self-healing summary written to: {json_path}")
    print(f"Self-healing report written to: {md_path}")
    print(f"Email alert preview written to: {email_path}")
    print(f"Email sent: {email_status['sent']}")
    print(f"Email status: {email_status['reason']}")


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous runtime self-healing engine for Falco events."
    )

    parser.add_argument(
        "--input",
        default="self-healing-engine/input/falco-runtime-detection-evidence.txt",
        help="Path to Falco runtime event input file.",
    )

    parser.add_argument(
        "--output-dir",
        default="self-healing-engine/output",
        help="Directory for generated reports.",
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute safe remediation actions. Default mode is dry-run.",
    )

    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Send email alert using SMTP environment variables.",
    )

    args = parser.parse_args()

    events = parse_falco_events(Path(args.input))
    decisions = [build_decision(event) for event in events]
    executions = [execute_decision(decision, args.execute) for decision in decisions]

    write_reports(decisions, executions, Path(args.output_dir), args.send_email)

    high_risk_count = sum(
        1 for decision in decisions
        if decision["risk_level"] in {"HIGH", "CRITICAL"}
    )

    print(f"Events analyzed: {len(events)}")
    print(f"High-risk events: {high_risk_count}")
    print(f"Mode: {'execute' if args.execute else 'dry-run'}")


if __name__ == "__main__":
    main()
