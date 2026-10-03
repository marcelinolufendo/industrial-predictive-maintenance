from dataclasses import dataclass


@dataclass
class Decision:
    status: str
    reasons: list[str]


def decide(anomaly_score: float, failure_probability: float, rul: int) -> Decision:
    reasons = []

    if anomaly_score >= 0.80:
        reasons.append("high_anomaly_score")
    if failure_probability >= 0.70:
        reasons.append("high_failure_probability")
    if rul <= 20:
        reasons.append("low_rul")

    if "high_failure_probability" in reasons or "low_rul" in reasons or anomaly_score >= 0.80:
        status = "CRITICAL"
    elif anomaly_score >= 0.50 or failure_probability >= 0.30:
        status = "WARNING"
        if anomaly_score >= 0.50:
            reasons.append("elevated_anomaly_score")
        if failure_probability >= 0.30:
            reasons.append("elevated_failure_probability")
    else:
        status = "NORMAL"

    return Decision(status=status, reasons=reasons)
