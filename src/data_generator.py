import numpy as np
import pandas as pd

def generate_telemetry(num_points=300, seed=42):
    """
    Generate synthetic satellite telemetry.

    Parameters
    ----------
    num_points : int
        Number of telemetry observations to generate.

    seed : int
        Random seed so that we get the same dataset every time.

    Returns
    -------
    pd.DataFrame
        Synthetic telemetry dataset.
    """

    np.random.seed(seed)

    # One telemetry reading every minute.
    timestamps = pd.date_range(
        start="2026-01-01 00:00:00",
        periods=num_points,
        freq="min"
    )

    time = np.arange(num_points)

    # ---------------------------------------------------------
    # NORMAL TEMPERATURE
    #
    # We use a small sinusoidal pattern to represent natural
    # variation during the mission, plus random sensor noise.
    # ---------------------------------------------------------
    temperature = (
        22
        + 1.5 * np.sin(time / 20)
        + np.random.normal(0.0, 0.4, num_points)
    )

    # ---------------------------------------------------------
    # BATTERY
    #
    # Normally the battery slowly changes around a healthy
    # operating level.
    # ---------------------------------------------------------
    battery = (
        92
        - 0.01 * time
        + np.random.normal(0.0, 0.15, num_points)
    )

    # ---------------------------------------------------------
    # COMMUNICATION SIGNAL
    #
    # Signal strength is represented in dBm.
    # Around -70 dBm is our normal synthetic operating point.
    # ---------------------------------------------------------
    signal_strength = (
        -70
        + np.random.normal(0.0, 1.0, num_points)
    )

    # ---------------------------------------------------------
    # ALTITUDE
    #
    # We assume a nominal orbit around 400 km with small
    # fluctuations.
    # ---------------------------------------------------------
    altitude = (
        400
        + 0.3 * np.sin(time / 30)
        + np.random.normal(0.0, 0.05, num_points)
    )

    # ---------------------------------------------------------
    # CPU LOAD
    #
    # Represents the percentage of onboard CPU utilization.
    # Normally it fluctuates around a moderate operating level.
    # ---------------------------------------------------------
    cpu_load = (
            35
            + 5 * np.sin(time / 15)
            + np.random.normal(0, 2, num_points)
    )

    '''
    =========================================================
    INJECT AN ABNORMAL SCENARIO
    =========================================================

    Starting at this point in the mission, we simulate a
    degrading power/thermal situation.

    Battery starts falling faster.
    Temperature starts rising.
    Signal becomes weaker.

    This gives our later anomaly detector something meaningful
    to identify.
    =========================================================
    '''


    anomaly_start = int(num_points * 0.65)

    anomaly_time = np.arange(num_points - anomaly_start)
    # CURRENTLY, the anomaly is between t = 195 and t = 300

    # Battery degradation accelerates.
    battery[anomaly_start:] -= 0.08 * anomaly_time

    # Temperature gradually rises.
    temperature[anomaly_start:] += 0.6 * anomaly_time

    # Communication signal gradually degrades.
    signal_strength[anomaly_start:] -= 0.4 * anomaly_time

    # CPU utilization increases during the abnormal scenario.
    cpu_load[anomaly_start:] += 0.5 * anomaly_time

    # ---------------------------------------------------------
    # Build one DataFrame containing all telemetry.
    # ---------------------------------------------------------
    telemetry = pd.DataFrame({
        "timestamp": timestamps,
        "temperature": temperature,
        "battery": battery,
        "signal_strength": signal_strength,
        "altitude": altitude,
        "cpu_load": cpu_load
    })

    # NOTES: we don't imply that high CPU load necessarily causes all of
    #  these effects in a real spacecraft. In our prototype, we are
    #  assuming a synthetic relationship between increased computational activity,
    #  power consumption, and thermal load.

    return telemetry


if __name__ == "__main__":
    telemetry = generate_telemetry()

    # Save the generated data so that the dashboard can use
    # exactly the same dataset during development.
    # (index=False prevents pandas from adding an extra row-number column)
    telemetry.to_csv("data/telemetry.csv", index=False)

    print("Telemetry generated successfully.")
    print(telemetry.head())
    print("\nDataset shape:", telemetry.shape)