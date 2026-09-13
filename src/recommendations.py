RECOMMENDATIONS = {
    "TEMP-HIGH-W":
        "Reduce non-critical thermal load and monitor temperature closely.",

    "TEMP-HIGH-C":
        "Immediately reduce thermal load and prioritize thermal stabilization.",

    "TEMP-RAPID-RISE-W":
        "Investigate the source of increasing thermal load and monitor temperature closely.",

    "TEMP-RAPID-RISE-C":
        "Reduce non-critical processing immediately and prioritize thermal stabilization.",

    "BATT-LOW-W":
        "Reduce non-critical power consumption to preserve remaining battery capacity.",

    "BATT-LOW-C":
        "Enter power-conservation mode and disable non-essential systems.",

    "BATT-RAPID-DROP-W":
        "Investigate abnormal power consumption and reduce non-critical activity.",

    "BATT-RAPID-DROP-C":
        "Aggressively reduce non-critical power consumption and investigate the source of rapid discharge.",

    "SIG-WEAK-W":
        "Monitor the communication link and consider reducing non-essential data transmission.",

    "SIG-WEAK-C":
        "Prioritize communication reliability and reduce non-essential transmissions.",

    "SIG-RAPID-DEGRADE-W":
        "Monitor communication degradation and prepare for reduced-link operations.",

    "SIG-RAPID-DEGRADE-C":
        "Prioritize critical communications and prepare for loss of communication link.",

    "ALT-DEVIATION-W":
        "Monitor orbital state closely and assess the cause of the altitude deviation.",

    "ALT-DEVIATION-C":
        "Prioritize orbital-state assessment and initiate appropriate mission-level response.",

    "CPU-HIGH-W":
        "Reduce non-critical onboard computational tasks.",

    "CPU-HIGH-C":
        "Suspend non-essential processing to reduce power and thermal load.",

    "CPU-RAPID-RISE-W":
        "Investigate increasing computational load and reduce non-critical processing.",

    "CPU-RAPID-RISE-C":
        "Immediately reduce non-essential computational activity.",

    "PWR-THERMAL-STRESS-W":
        "Reduce non-critical onboard processing to conserve power and control thermal load.",

    "PWR-THERMAL-STRESS-C":
        "Immediately reduce non-critical processing and prioritize power and thermal stabilization."
}

def get_recommendations(anomalies):
    """
    Generate recommendations from the complete list of
    detected anomalies.

    Composite mission-level anomalies are prioritized over
    their individual component anomalies.

    Parameters:
        anomalies: List of anomaly dictionaries produced
                   by anomaly_detection.py.

    Returns:
        List of recommendation dictionaries.
    """

    if not anomalies:
        return []

    anomaly_codes = {anomaly["code"] for anomaly in anomalies}

    recommendations = []

    # ---------------------------------------------------------
    # Composite conditions get priority.
    #
    # If a mission-level condition exists, we don't want to
    # overwhelm the operator with several lower-level messages
    # describing the same underlying problem.
    # ---------------------------------------------------------

    composite_codes = {
        "PWR-THERMAL-STRESS-C",
        "PWR-THERMAL-STRESS-W"
    }

    for code in anomaly_codes:

        if code in composite_codes:

            recommendations.append({
                "code": code,
                "severity": next(
                    anomaly["severity"]
                    for anomaly in anomalies
                    if anomaly["code"] == code
                ),
                "action": RECOMMENDATIONS[code]
            })

    # ---------------------------------------------------------
    # Add individual recommendations that are NOT already
    # represented by a composite condition.
    # ---------------------------------------------------------

    for anomaly in anomalies:

        code = anomaly["code"]

        if code in composite_codes:
            continue

        recommendation = RECOMMENDATIONS.get(code)

        if recommendation is not None:
            recommendations.append({
                "code": code,
                "severity": anomaly["severity"],
                "action": recommendation
            })

    return recommendations


