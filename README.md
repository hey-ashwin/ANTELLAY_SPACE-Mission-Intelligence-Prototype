# ANTELLAY Mission Intelligence Prototype

A small prototype demonstrating the mission-intelligence workflow:

**Telemetry → Monitor → Anomaly Detection → Prediction → Recommendation**

It simulates a satellite generating temperature, battery, communication-signal,
altitude, and CPU-load telemetry, and shows a Streamlit dashboard that
detects anomalies, forecasts battery behavior, and recommends operator
actions.

## Project structure

```
.
├── app.py                     # Streamlit dashboard (entry point)
├── requirements.txt
├── data/
│   └── telemetry.csv          # generated synthetic dataset (not committed; see below)
└── src/
    ├── __init__.py
    ├── data_generator.py      # creates the synthetic telemetry dataset
    ├── anomaly_detection.py   # threshold + trend + composite anomaly rules
    ├── prediction.py          # linear battery-threshold forecast
    └── recommendations.py     # anomaly code -> recommended action
```

## Setup

```bash
# 1. Create and activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Running the prototype

```bash
# 1. Generate the synthetic telemetry dataset (writes data/telemetry.csv)
python src/data_generator.py

# 2. Launch the dashboard
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`. It will show:

- **Mission Status** banner (NORMAL / WARNING / CRITICAL)
- **Latest Telemetry** metric tiles
- **Telemetry Trends** — per-channel time-series charts
- **Anomaly Detection** — list of currently active anomalies with severity
- **Battery Prediction** — actual vs. forecast battery curve and estimated
  time to the critical threshold
- **Recommended Actions** — one action per active anomaly (or one combined
  action for a composite condition)

You can also run each module standalone for a quick console check:

```bash
python src/anomaly_detection.py   # prints detected anomalies for the current dataset
python src/prediction.py          # prints the battery threshold-crossing forecast
```

## How it works (brief)

- **Data generation**: five channels with a realistic baseline (sinusoidal
  drift, slow discharge, sensor noise) for the first ~65% of the run, then a
  compounding power/thermal/communication degradation is injected for the
  remainder so the detector, predictor, and recommender have something
  meaningful to act on.
- **Anomaly detection**: each parameter is checked against an absolute
  WARNING/CRITICAL threshold *and* a rolling-window trend (recent vs.
  preceding average), plus one composite rule that fires when CPU stress
  co-occurs with thermal or battery stress.
- **Prediction**: a linear fit over the most recent battery readings is
  extrapolated to estimate time remaining until the battery crosses a
  critical threshold — chosen for interpretability and because it needs no
  training data.
- **Recommendation**: each anomaly code maps to a concrete suggested
  operator action; composite conditions suppress their component
  recommendations so the operator sees one coherent action.

## Known limitations

- Thresholds and the injected fault magnitude are hand-picked synthetic
  values, not calibrated to a real spacecraft bus.
- The trend detector uses a simple rolling-average difference, which is
  sensitive to noise and to non-monotonic signals; a regression-based slope
  would be more robust.
- The battery forecast assumes a constant discharge rate and will be
  inaccurate if real degradation is nonlinear.
