# IMU Motion Capture Analysis

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

analysis of IMU and motion capture data for biomechanical movement assessment

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         imu_motion_capture_analysis and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── imu_motion_capture_analysis   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes imu_motion_capture_analysis a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

---------------------------------------------------------------------------------


## 1. Check Conda Installation

Open Anaconda Prompt or PowerShell and verify that Conda is available:

```bash
conda --version
```

If Conda is installed correctly, a version number should be displayed.

---

## 2. Create a New Conda Environment

Create a dedicated environment for the Xsens-LSL project:

```bash
conda create -n xsens python=3.10
```

Confirm the installation:

```text
Proceed ([y]/n)?
```

Type:

```text
y
```

---

## 3. Activate the Environment

Activate the newly created environment:

```bash
conda activate xsens
```

Verify that the environment is active:

```bash
python --version
where python
```

The Python path should point to:

```text
...\anaconda3\envs\xsens\
```

---

## 4. Install Required Python Packages

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the required packages:

```bash
python -m pip install pylsl numpy pandas matplotlib pyxdf
```

Verify the installation:

```bash
python -c "import pylsl, numpy, pandas; print('Packages installed successfully')"
```

---

## 5. Install the Xsens Device API (XDA)

Download and install the Xsens Device API (SDK) provided by Movella/Xsens.

After installation, verify that Python can access the SDK:

```bash
python -c "import xsensdeviceapi as xda; print('XDA OK')"
```

Expected output:

```text
XDA OK
```

---

## 6. Clone the Repository

Navigate to the desired project directory:

```bash
cd "C:\Users\Username\Documents"
```

Clone the repository:

```bash
git clone <repository-url>
```

Enter the project directory:

```bash
cd imu_motion_capture_analysis
```

---

## 7. Open the Project in VS Code

Open the project folder:

```bash
code .
```

Select the correct Python interpreter:

```text
Ctrl + Shift + P
Python: Select Interpreter
```

Choose:

```text
Python 3.10 (xsens)
```

---

## 8. Connect the Awinda Station

Connect the Xsens Awinda Station via USB.

Verify that the device is recognized by the operating system.

Close MT Manager before running the Python script to avoid communication conflicts.

---

## 9. Configure the Sensor Parameters

In the Python script, define:

```python
PREFERRED_CHANNEL = 11
TARGET_RATE_HZ = 100
```

where:

- `PREFERRED_CHANNEL` = wireless communication channel
- `TARGET_RATE_HZ` = desired sampling frequency

---

## 10. Start the LSL Stream

Run the script:

```bash
python imu_7_sensors_LSL.py
```

The script will:

1. Detect the Awinda Station
2. Switch to configuration mode
3. Set the update rate
4. Enable the radio channel
5. Connect the MTw sensors
6. Switch to measurement mode
7. Publish all sensor data as LSL streams

---

## 11. Verify the Available Streams

The following streams should appear:

```text
Xsens_MTw2_00B4D0C2
Xsens_MTw2_00B4D0D0
Xsens_MTw2_00B4D0C8
Xsens_MTw2_00B4D0BF
Xsens_MTw2_00B4D0C4
Xsens_MTw2_00B4D0BE
Xsens_MTw2_00B4D0C5
```

---

## 12. Record Data Using LabRecorder

Start LabRecorder.

Select the desired Xsens streams.

Choose an output filename.

Start recording.

The recorded data will be saved as:

```text
*.xdf
```

---

## 13. Recorded Signals

Each stream contains:

| Signal | Description |
|----------|----------|
| qw, qx, qy, qz | Quaternion orientation |
| ax, ay, az | Accelerometer |
| gx, gy, gz | Gyroscope |
| mx, my, mz | Magnetometer |
| packet_counter | Packet counter |
| sample_time_fine | Sensor timestamp |
