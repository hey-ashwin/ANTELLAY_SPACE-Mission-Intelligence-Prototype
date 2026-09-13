import pandas as pd
import numpy as np

# noinspection PyShadowingNames
def get_recent_battery_data(df, window=30):
    """
    Return the most recent battery readings used for prediction.

    We use a limited recent window rather than the entire mission
    history so that recent battery behavior has more influence
    on the forecast.
    """

    # Make sure we don't request more rows than actually exist.
    window = min(window, len(df))

    recent_data = df.tail(window)

    return recent_data[["timestamp", "battery"]].copy()


# noinspection PyShadowingNames
def fit_battery_trend(df, window=30):
    """
    Fit a simple linear model to recent battery telemetry.

    Returns:
        slope, intercept

    The model is:
        battery = slope * time + intercept
        y = mx + c
    """

    recent_data = get_recent_battery_data(df, window)

    # Create a simple numerical time axis.
    # Each index represents one telemetry interval (1 minute).
    time = np.arange(len(recent_data))

    battery = recent_data["battery"].to_numpy()

    # Fit a straight line:
    #
    # battery = slope * time + intercept
    #
    # degree=1 means we are fitting a linear equation.
    slope, intercept = np.polyfit(time, battery, 1)

    return slope, intercept

# noinspection PyShadowingNames
def predict_battery_threshold(df, threshold=40, window=30):
    """
    Estimate how long it will take for the battery
    to reach a specified threshold.

    Returns:
        Dictionary containing prediction details.
    """

    slope, intercept = fit_battery_trend(df, window)

    current_battery = df.iloc[-1]["battery"]

    if current_battery <= threshold:
        return {
            "current_battery": float(current_battery),
            "slope": float(slope),
            "threshold": threshold,
            "minutes_remaining": 0,
            "time_remaining": "0h 0m"
        }

    if slope >= 0:
        return {
            "current_battery": float(current_battery),
            "slope": float(slope),
            "threshold": threshold,
            "minutes_remaining": None,
            "time_remaining": "Not predictable"
        }

    threshold_time = (threshold - intercept) / slope

    current_time = window - 1

    minutes_remaining = max(0, threshold_time - current_time)

    return {
        "current_battery": float(current_battery),
        "slope": float(slope),
        "threshold": threshold,
        "minutes_remaining": float(minutes_remaining),
        "time_remaining": format_duration(minutes_remaining)
    }


# noinspection PyShadowingNames
def get_battery_prediction_series(df, window=30, forecast_minutes=120):
    """
    Generate future battery values using the fitted
    linear degradation trend.

    Returns:
        DataFrame containing time and predicted battery.
    """

    slope, intercept = fit_battery_trend(df, window)

    # Time values for the historical prediction window
    historical_time = np.arange(window)

    # Future time values
    future_time = np.arange(
        window,
        window + forecast_minutes + 1
    )

    # Predict battery using the fitted line.
    predicted_battery = (
        slope * future_time + intercept
    )

    return pd.DataFrame({
        "time": future_time,
        "predicted_battery": predicted_battery
    })

# noinspection PyShadowingNames
def format_duration(minutes):
    """
    Convert a duration in minutes into a human-readable
    hours and minutes format.
    """

    if minutes is None:
        return "Not predictable"

    hours = int(minutes // 60)
    remaining_minutes = int(minutes % 60)

    return f"{hours}h {remaining_minutes}m"

if __name__ == "__main__":

    df = pd.read_csv("data/telemetry.csv")

    prediction = predict_battery_threshold(df)

    print("Battery Prediction")
    print("-------------------")
    print(f"Current Battery:    {prediction['current_battery']:.2f}%")
    print(f"Battery Slope:      {prediction['slope']:.4f}%/min")
    print(f"Threshold:          {prediction['threshold']}%")
    print(f"Minutes Remaining:  {prediction['minutes_remaining']:.2f}")
    print(f"Time Remaining:     {prediction['time_remaining']}")

    prediction_series = get_battery_prediction_series(df)

    print(prediction_series.head())