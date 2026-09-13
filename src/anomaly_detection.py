# FIXME:
#  Lot of redundancy in the code, we can compress this to lesser functions.

"""
Contains threshold values for all satellite params.
NOTE: These are all synthetic values. They should be replaced/calibrated
        using mission-specific telemetry in a real system.
"""
THRESHOLDS = {
    "temperature": {
        "warning": 30,
        "critical": 35
    },

    "battery": {
        "warning": 70,
        "critical": 40
    },

    "signal_strength": {
        "warning": -75,
        "critical": -85
    },

    "altitude": {
        "warning_min": 395,
        "warning_max": 405,
        "critical_min": 390,
        "critical_max": 410
    },

    "cpu_load": {
        "warning": 70,
        "critical": 85
    }
}


"""
This is basically saying that the recent 10 min avg value MINUS 
prev(t-10 to t-20) 10 min avg value should be less than 1.0 for normal.

Previous 10 min                  Recent 10 min
───────────────                  ─────────────
24.0                            25.0
24.1                            25.2
24.2                            25.4
24.1                            25.6
...                             ...
24.3                            26.0

       average = 24.2                average = 25.5
                       │
                       ▼
                  increase = 1.3°C ---> WARNING
"""
TREND_THRESHOLDS = {
    "temperature": {
        "warning": 1.0,
        "critical": 2.0
    },

    "battery": {
        "warning": -1.0,
        "critical": -2.0
    },

    "signal_strength": {
        "warning": -1.5,
        "critical": -3.0
    },

    "cpu_load": {
        "warning": 10.0,
        "critical": 20.0
    }
}

def check_temperature(temperature):
    """
    Check current temperature against the THRESHOLDS

    Parameters
    ----------
    temperature

    Returns
    -------
    A dictionary describing the detected anomaly.
    Return None when temperature is normal.
    """

    warning_limit = THRESHOLDS["temperature"]["warning"]
    critical_limit = THRESHOLDS["temperature"]["critical"]

    if temperature > critical_limit:
        return{
            "code": "TEMP-HIGH-C",
            "severity": "CRITICAL",
            "message": "Temperature Anomaly: Temperature is critically high"
        }
    elif temperature > warning_limit:
        return{
            "code": "TEMP-HIGH-W",
            "severity": "WARNING",
            "message": "Temperature Anomaly: Temperature is above the normal range"
        }

    return None

def check_battery(battery):
    """
    Check the current battery level against configured thresholds.

    Returns:
        A dictionary describing the detected anomaly,
        or None if the battery level is normal.
    """

    warning_limit = THRESHOLDS["battery"]["warning"]
    critical_limit = THRESHOLDS["battery"]["critical"]

    if battery < critical_limit:
        return {
            "code": "BATT-LOW-C",
            "severity": "CRITICAL",
            "message": "Battery Anomaly: Battery level is critically low"
        }
    elif battery < warning_limit:
        return {
            "code": "BATT-LOW-W",
            "severity": "WARNING",
            "message": "Battery Anomaly: Battery level is below the normal range"
        }

    return None

def check_signal_strength(signal_strength):
    """
    Check the current communication signal strength.

    Signal strength is measured in dBm. Since dBm values are
    negative here, a more negative value represents a weaker signal.
    """

    warning_limit = THRESHOLDS["signal_strength"]["warning"]
    critical_limit = THRESHOLDS["signal_strength"]["critical"]

    if signal_strength < critical_limit:
        return {
            "code": "SIG-WEAK-C",
            "severity": "CRITICAL",
            "message": "Communication Anomaly: Signal strength is critically weak"
        }
    elif signal_strength < warning_limit:
        return {
            "code": "SIG-WEAK-W",
            "severity": "WARNING",
            "message": "Communication Anomaly: Signal strength is below the normal range"
        }

    return None

def check_altitude(altitude):
    """
    Check whether the current altitude is within the assumed
    nominal orbital range.
    """

    thresholds = THRESHOLDS["altitude"]

    # Critical if altitude is far outside the assumed range.
    if (
        altitude < thresholds["critical_min"]
        or altitude > thresholds["critical_max"]
    ):
        return {
            "code": "ALT-DEVIATION-C",
            "severity": "CRITICAL",
            "message": "Orbital Anomaly: Altitude is significantly outside the nominal range"
        }

    # Warning if altitude is outside the nominal range but
    # still within the wider acceptable boundary.
    elif (
        altitude < thresholds["warning_min"]
        or altitude > thresholds["warning_max"]
    ):
        return {
            "code": "ALT-DEVIATION-W",
            "severity": "WARNING",
            "message": "Orbital Anomaly: Altitude is outside the nominal range"
        }

    return None

def check_cpu_load(cpu_load):
    """
    Check current onboard CPU utilization.
    """

    warning_limit = THRESHOLDS["cpu_load"]["warning"]
    critical_limit = THRESHOLDS["cpu_load"]["critical"]

    if cpu_load > critical_limit:
        return {
            "code": "CPU-HIGH-C",
            "severity": "CRITICAL",
            "message": "Computing Anomaly: CPU utilization is critically high"
        }

    elif cpu_load > warning_limit:
        return {
            "code": "CPU-HIGH-W",
            "severity": "WARNING",
            "message": "Computing Anomaly: CPU utilization is above the normal range"
        }

    return None

# FIXME:
#  Current trend detection uses a simple difference between rolling averages.
#  This causes issues as temperature generation is sinusoidal.
#  Consider replacing this with a regression-based slope calculation.

def check_temperature_trend(dataframe, window=10):
    """
    Detect unusually rapid temperature increases.
    We compare avg temp over most recent 'window' reading with avg from prev window.

    Parameters
    ----------
    dataframe : pd.DataFrame
         Telemetry DataFrame

    window : int

    Returns
    -------
    dict or None - similar to check_temperature
    """

    if len(dataframe) < 2*window:
        return None

    # Get windows of data
    prev_window = dataframe["temperature"].iloc[-2 * window:-window]
    recent_window = dataframe["temperature"].iloc[-window:]

    # Calculate avg temp in each window
    prev_avg = prev_window.mean()
    recent_avg = recent_window.mean()

    temp_change = recent_avg - prev_avg

    warning_limit = TREND_THRESHOLDS["temperature"]["warning"]
    critical_limit = TREND_THRESHOLDS["temperature"]["critical"]

    if temp_change >= critical_limit:
        return{
            "code": "TEMP-RAPID-RISE-C",
            "severity": "CRITICAL",
            "message": "Temperature Anomaly: Temperature is rising rapidly"
        }

    elif temp_change >= warning_limit:
        return{
            "code": "TEMP-RAPID-RISE-W",
            "severity": "WARNING",
            "message": "Temperature Anomaly: Temperature is increasing faster than expected"
        }

    return None

def check_battery_trend(dataframe, window=10):
    """
    Detect unusually rapid battery discharge.

    We compare the average battery level in the most recent
    window against the preceding window.

    A negative change means the battery is discharging.
    """

    if len(dataframe) < 2 * window:
        return None

    previous_window = dataframe["battery"].iloc[-2 * window:-window]
    recent_window = dataframe["battery"].iloc[-window:]

    previous_average = previous_window.mean()
    recent_average = recent_window.mean()

    battery_change = recent_average - previous_average

    warning_limit = TREND_THRESHOLDS["battery"]["warning"]
    critical_limit = TREND_THRESHOLDS["battery"]["critical"]

    # Battery is falling, so we're interested in NEGATIVE changes.
    if battery_change <= critical_limit:
        return {
            "code": "BATT-RAPID-DROP-C",
            "severity": "CRITICAL",
            "message": "Battery Anomaly: Battery is discharging rapidly",
        }

    elif battery_change <= warning_limit:
        return {
            "code": "BATT-RAPID-DROP-W",
            "severity": "WARNING",
            "message": "Battery Anomaly: Battery is discharging faster than expected",
        }

    return None

def check_signal_trend(dataframe, window=10):
    """
    Detect unusually rapid degradation in communication signal.

    A negative change means the signal is becoming weaker.
    """

    if len(dataframe) < 2 * window:
        return None

    previous_window = dataframe["signal_strength"].iloc[-2 * window:-window]
    recent_window = dataframe["signal_strength"].iloc[-window:]

    previous_average = previous_window.mean()
    recent_average = recent_window.mean()

    signal_change = recent_average - previous_average

    warning_limit = TREND_THRESHOLDS["signal_strength"]["warning"]
    critical_limit = TREND_THRESHOLDS["signal_strength"]["critical"]

    if signal_change <= critical_limit:
        return {
            "code": "SIG-RAPID-DEGRADE-C",
            "severity": "CRITICAL",
            "message": "Communication Anomaly: Signal strength is degrading rapidly",
        }
    elif signal_change <= warning_limit:
        return {
            "code": "SIG-RAPID-DEGRADE-W",
            "severity": "WARNING",
            "message": "Communication Anomaly: Signal strength is degrading faster than expected",
        }

    return None

def check_cpu_trend(dataframe, window=10):
    """
    Detect unusually rapid increases in CPU utilization.
    """

    if len(dataframe) < 2 * window:
        return None

    previous_window = dataframe["cpu_load"].iloc[-2 * window:-window]
    recent_window = dataframe["cpu_load"].iloc[-window:]

    previous_average = previous_window.mean()
    recent_average = recent_window.mean()

    cpu_change = recent_average - previous_average

    warning_limit = TREND_THRESHOLDS["cpu_load"]["warning"]
    critical_limit = TREND_THRESHOLDS["cpu_load"]["critical"]

    if cpu_change >= critical_limit:
        return {
            "code": "CPU-RAPID-RISE-C",
            "severity": "CRITICAL",
            "message": "Computing Anomaly: CPU utilization is rising rapidly",
        }

    elif cpu_change >= warning_limit:
        return {
            "code": "CPU-RAPID-RISE-W",
            "severity": "WARNING",
            "message": "Computing Anomaly: CPU utilization is increasing faster than expected",
        }

    return None

##############################################################

def check_power_thermal_stress(anomalyList):
    """
    Detect a combined power/thermal stress condition.

    This is triggered when onboard computing activity is increasing
    while the spacecraft is also experiencing thermal or battery stress.

    Parameters:
        anomalyList: List of anomaly dictionaries produced by
                   detect_anomalies().

    Returns:
        A dictionary describing the composite anomaly,
        or None if the condition is not detected.
    """

    # noinspection PyShadowingNames
    anomaly_codes = {anomaly["code"] for anomaly in anomalyList}

    cpu_stress = (
        "CPU-HIGH-W" in anomaly_codes
        or "CPU-HIGH-C" in anomaly_codes
        or "CPU-RAPID-RISE-W" in anomaly_codes
        or "CPU-RAPID-RISE-C" in anomaly_codes
    )

    thermal_stress = (
        "TEMP-HIGH-W" in anomaly_codes
        or "TEMP-HIGH-C" in anomaly_codes
        or "TEMP-RAPID-RISE-W" in anomaly_codes
        or "TEMP-RAPID-RISE-C" in anomaly_codes
    )

    battery_stress = (
        "BATT-LOW-W" in anomaly_codes
        or "BATT-LOW-C" in anomaly_codes
        or "BATT-RAPID-DROP-W" in anomaly_codes
        or "BATT-RAPID-DROP-C" in anomaly_codes
    )

    # We need computing stress plus either
    # thermal stress or battery stress.
    if cpu_stress and (thermal_stress or battery_stress):

        critical_codes = {
            "CPU-HIGH-C",
            "CPU-RAPID-RISE-C",
            "TEMP-HIGH-C",
            "TEMP-RAPID-RISE-C",
            "BATT-LOW-C",
            "BATT-RAPID-DROP-C"
        }

        is_critical = any(
            code in anomaly_codes
            for code in critical_codes
        )

        if is_critical:
            return {
                "code": "PWR-THERMAL-STRESS-C",
                "severity": "CRITICAL",
                "message": (
                    "Mission Anomaly: High onboard computing activity "
                    "is associated with power or thermal stress"
                )
            }

        return {
            "code": "PWR-THERMAL-STRESS-W",
            "severity": "WARNING",
            "message": (
                "Mission Anomaly: Onboard computing activity "
                "is associated with increasing power or thermal stress"
            )
        }

    return None

def detect_anomalies(dataframe):
    """
    Run all anomaly detectors on the latest telemetry data.

    Returns:
        A LIST of anomaly DICTIONARIES.
    """

    latest = dataframe.iloc[-1]

    anomalyList = []

    # -------------------------
    # Current-value checks
    # -------------------------
    current_checks = [
        check_temperature(latest["temperature"]),
        check_battery(latest["battery"]),
        check_signal_strength(latest["signal_strength"]),
        check_altitude(latest["altitude"]),
        check_cpu_load(latest["cpu_load"])
    ]

    # -------------------------
    # Trend checks
    # -------------------------
    trend_checks = [
        check_temperature_trend(dataframe),
        check_battery_trend(dataframe),
        check_signal_trend(dataframe),
        check_cpu_trend(dataframe)
    ]

    # Combine all detected anomalies
    # noinspection PyShadowingNames
    for anomaly in current_checks + trend_checks:
        if anomaly is not None:
            anomalyList.append(anomaly)

    # Check for higher-level mission conditions
    composite_anomaly = check_power_thermal_stress(anomalyList)

    if composite_anomaly is not None:
        anomalyList.append(composite_anomaly)

    return anomalyList


if __name__ == "__main__":
    import pandas as pd

    df = pd.read_csv("data/telemetry.csv")

    anomalies = detect_anomalies(df)

    print("\nDetected anomalies:")

    if anomalies:
        for anomaly in anomalies:
            print(anomaly)
    else:
        print("No anomalies detected.")