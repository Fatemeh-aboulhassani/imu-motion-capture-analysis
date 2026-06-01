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
## Xsens-LSL Setup Guide

This guide explains how to set up a clean Conda environment for streaming Xsens MTw sensor data through LSL and recording it with LabRecorder.

---

## 1. Check Conda Installation

Open **Anaconda Prompt** or **PowerShell** and verify that Conda is available:

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

Install NumPy 1.x first, because the Xsens Device API wheel used in this project is not compatible with NumPy 2.x:

```bash
python -m pip install "numpy<2"
```

Install the other required packages:

```bash
python -m pip install pylsl pandas matplotlib
```

Install a pyxdf version compatible with NumPy 1.x:

```bash
python -m pip install "pyxdf<1.17"
```

Verify the installation:

```bash
python -c "import pylsl, numpy, pandas, pyxdf; print('Packages installed successfully')"
```

---

## 5. Install the Xsens Device API (XDA)

The Xsens Device API is not installed from the internet with a normal `pip install`.
It is provided by the Movella/Xsens MT SDK as a local `.whl` file.

Navigate to the SDK folder that contains the Xsens wheel files:

```bash
cd "C:\Users\abolhassni\Desktop\TU Darmstadt\Term3\ANSYMB\LSL\MT SDK\Python\x64"
```

Install the wheel file that matches Python 3.10:

```bash
python -m pip install xsensdeviceapi-2022.2.0-cp310-none-win_amd64.whl
```

Verify that Python can access the SDK:

```bash
python -c "import xsensdeviceapi as xda; print('XDA OK')"
```

Expected output:

```text
XDA OK
```

---

## 6. Add the Environment to Jupyter / VS Code

Install the Jupyter kernel package:

```bash
python -m pip install ipykernel
```

Register the environment as a Jupyter kernel:

```bash
python -m ipykernel install --user --name xsens --display-name "Python (xsens)"
```

After this, restart VS Code or Jupyter and select the kernel:

```text
Python (xsens)
```

---

## 7. Clone the Repository

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

## 8. Open the Project in VS Code

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

## 9. Connect the Awinda Station

Connect the Xsens Awinda Station via USB.

Verify that the device is recognized by the operating system.

Close MT Manager before running the Python script to avoid communication conflicts.

---

## 10. Configure the Sensor Parameters

In the Python script, define:

```python
PREFERRED_CHANNEL = 11
TARGET_RATE_HZ = 100
```

where:

```text
PREFERRED_CHANNEL = wireless communication channel
TARGET_RATE_HZ = desired sampling frequency
```

---

## 11. Start the LSL Stream

Activate the environment:

```bash
conda activate xsens
```

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

## 12. Verify the Available Streams

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

## 13. Record Data Using LabRecorder

Start LabRecorder.

Select the desired Xsens streams.

Choose an output filename.

Start recording.

The recorded data will be saved as:

```text
*.xdf
```

---

## 14. Recorded Signals

Each stream contains:

| Signal             | Description            |
| ------------------ | ---------------------- |
| `qw, qx, qy, qz`   | Quaternion orientation |
| `ax, ay, az`       | Accelerometer data     |
| `gx, gy, gz`       | Gyroscope data         |
| `mx, my, mz`       | Magnetometer data      |
| `packet_counter`   | Packet counter         |
| `sample_time_fine` | Sensor timestamp       |
