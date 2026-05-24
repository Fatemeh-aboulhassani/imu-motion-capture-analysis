



import time
import threading
import os
import subprocess
from collections import deque

import xsensdeviceapi as xda
from pylsl import StreamInfo, StreamOutlet, local_clock


# ---------- USER SETTINGS ----------
# Leave empty to accept ALL MTw that connect.
MTW_IDS_ALLOWLIST = ["00B4D0C2", "00B4D0D0","00B4D0C8","00B4D0BF","00B4D0C4","00B4D0BE","00B4D0C5"]

PREFERRED_CHANNEL = 11          # Wireless channel (as in MT Manager)
TARGET_RATE_HZ    = 100         # What you want (matches MT Manager "Rate (Hz)")

LSL_PREFIX = "Xsens_MTw2"
LSL_TYPE   = "IMU"
# ----------------------------------


# ---------- QUALISYS LSL APP SETTINGS ----------
# This opens the official Qualisys LSL App GUI.
# You will still press Start manually inside that GUI.
AUTO_OPEN_QUALISYS_LSL_APP = True

QUALISYS_LSL_APP_DIR = r"C:\Users\abolhassni\Desktop\TU Darmstadt\Term3\ANSYMB\LSL\qualisys_lsl_app"
QUALISYS_PYTHON_EXE = r"C:\Users\abolhassni\anaconda3\envs\qualisys_lsl\python.exe"
# -----------------------------------------------


# ---------- LABRECORDER SETTINGS ----------
# This opens LabRecorder only.
# Stream selection and Start Recording stay manual.
AUTO_OPEN_LABRECORDER = True

LABRECORDER_EXE = r"C:\Users\abolhassni\Desktop\TU Darmstadt\Term3\ANSYMB\Software\LabRecorder\LabRecorder.exe"
# -----------------------------------------



def start_qualisys_lsl_app():
    """
    Opens the official Qualisys LSL App GUI.
    You still press Start manually inside the Qualisys window.
    """
    if not AUTO_OPEN_QUALISYS_LSL_APP:
        return None

    if not os.path.isdir(QUALISYS_LSL_APP_DIR):
        print(f"[QTM ERROR] Folder not found: {QUALISYS_LSL_APP_DIR}")
        return None

    if not os.path.exists(QUALISYS_PYTHON_EXE):
        print(f"[QTM ERROR] Python exe not found: {QUALISYS_PYTHON_EXE}")
        print("[QTM ERROR] Check it with: conda activate qualisys_lsl  then  where python")
        return None

    print("[QTM] Opening Qualisys LSL App...")

    try:
        process = subprocess.Popen(
            [QUALISYS_PYTHON_EXE, "-m", "qlsl.gui"],
            cwd=QUALISYS_LSL_APP_DIR,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("[QTM] Qualisys LSL App opened.")
        return process

    except Exception as e:
        print(f"[QTM ERROR] Could not open Qualisys LSL App: {e}")
        return None


def start_labrecorder():
    """
    Opens LabRecorder only.
    Stream selection and Start Recording stay manual.
    """
    if not AUTO_OPEN_LABRECORDER:
        return None

    if not os.path.exists(LABRECORDER_EXE):
        print(f"[LabRecorder ERROR] File not found: {LABRECORDER_EXE}")
        print("[LabRecorder ERROR] Please fix LABRECORDER_EXE path.")
        return None

    print("[LabRecorder] Opening LabRecorder...")

    try:
        process = subprocess.Popen([LABRECORDER_EXE])
        print("[LabRecorder] LabRecorder opened.")
        return process

    except Exception as e:
        print(f"[LabRecorder ERROR] Could not open LabRecorder: {e}")
        return None


class PacketBuffer(xda.XsCallback):
    def __init__(self, maxlen=65536):
        super().__init__()
        self._lock = threading.Lock()
        self._q = deque(maxlen=maxlen)
        self.total = 0

    def onLiveDataAvailable(self, dev, packet):
        try:
            src = packet.deviceId().toXsString().upper()
        except Exception:
            src = dev.deviceId().toXsString().upper()

        with self._lock:
            self._q.append((src, xda.XsDataPacket(packet)))
            self.total += 1

    def pop(self):
        with self._lock:
            if not self._q:
                return None
            return self._q.popleft()


def make_outlet(device_id_str: str):
    labels = [
        "qw","qx","qy","qz",
        "ax","ay","az",
        "gx","gy","gz",
        "mx","my","mz",
        "packet_counter","sample_time_fine"
    ]
    info = StreamInfo(
        name=f"{LSL_PREFIX}_{device_id_str}",
        type=LSL_TYPE,
        channel_count=len(labels),
        nominal_srate=float(TARGET_RATE_HZ),   # what we *intend* to run at
        channel_format="float32",
        source_id=f"{LSL_PREFIX}_{device_id_str}",
    )
    ch = info.desc().append_child("channels")
    for lab in labels:
        ch.append_child("channel").append_child_value("label", lab)
    return StreamOutlet(info, chunk_size=0, max_buffered=360)


def packet_to_sample(pkt: xda.XsDataPacket):
    # Quaternion
    if pkt.containsOrientation():
        q = pkt.orientationQuaternion()
        qw, qx, qy, qz = map(float, q[:4])
    else:
        qw = qx = qy = qz = float("nan")

    # Acc
    if pkt.containsCalibratedAcceleration():
        a = pkt.calibratedAcceleration()
        ax, ay, az = float(a[0]), float(a[1]), float(a[2])
    else:
        ax = ay = az = float("nan")

    # Gyro
    if pkt.containsCalibratedGyroscopeData():
        g = pkt.calibratedGyroscopeData()
        gx, gy, gz = float(g[0]), float(g[1]), float(g[2])
    else:
        gx = gy = gz = float("nan")

    # Magnetometer
    if pkt.containsCalibratedMagneticField():
        m = pkt.calibratedMagneticField()
        mx, my, mz = float(m[0]), float(m[1]), float(m[2])
    else:
        mx = my = mz = float("nan")

    # Timestamps
    try:
        pc = float(pkt.packetCounter())
    except Exception:
        pc = float("nan")

    try:
        stf = float(pkt.sampleTimeFine())
    except Exception:
        stf = float("nan")

    return [
        qw,qx,qy,qz,
        ax,ay,az,
        gx,gy,gz,
        mx,my,mz,
        pc, stf
    ]


def find_awinda_master(control: "xda.XsControl"):
    ports = xda.XsScanner_scanPorts()
    for i in range(ports.size()):
        pi = ports[i]
        if pi.baudrate() < 460800:
            continue

        if not control.openPort(pi.portName(), pi.baudrate()):
            continue

        dev = control.device(pi.deviceId())
        try:
            pc = dev.productCode()
        except Exception:
            pc = ""

        if isinstance(pc, str) and pc.upper().startswith("AW-"):
            return pi, dev

        control.closePort(pi.portName())

    raise RuntimeError("No Awinda station found. Close MT Manager completely and retry.")


def try_set_master_rate(master, target_hz: int) -> bool:
    """
    MT Manager's Wireless Config 'Rate (Hz)' corresponds to the AW-A2 updateRate.
    This must be done in CONFIG and preferably with radio disabled.
    """
    try:
        cur = int(master.updateRate())
    except Exception:
        cur = None

    try:
        supported = [int(master.supportedUpdateRates()[i]) for i in range(master.supportedUpdateRates().size())]
    except Exception:
        supported = []

    print(f"Master current updateRate = {cur}")
    if supported:
        print(f"Master supportedUpdateRates = {supported}")
    else:
        print("Master supportedUpdateRates = (could not read)")

    if cur == target_hz:
        print(f"Master updateRate already {target_hz} Hz.")
        return True

    print(f"Setting master updateRate -> {target_hz} Hz ...")
    ok = False
    try:
        ok = bool(master.setUpdateRate(target_hz))
    except Exception as e:
        print(f"[WARN] master.setUpdateRate({target_hz}) threw: {e}")
        ok = False

    try:
        newv = int(master.updateRate())
    except Exception:
        newv = None

    print(f"master.setUpdateRate returned {ok}, master.updateRate now = {newv}")
    return ok and (newv == target_hz)


def main():
    qtm_lsl_process = start_qualisys_lsl_app()

    if AUTO_OPEN_QUALISYS_LSL_APP:
        input(
            "\n[STEP] If the Qualisys LSL App opened, press Start inside that window. "
            "When the Qualisys stream is running, press ENTER here...\n"
        )

    labrecorder_process = start_labrecorder()

    print(
        "\n[INFO] LabRecorder is opened only. "
        "Select Xsens and Qualisys streams manually, then press Start Recording manually.\n"
    )

    control = xda.XsControl_construct()
    if control == 0:
        raise RuntimeError("Failed to construct XsControl")

    pi, master = find_awinda_master(control)
    master_id = master.deviceId().toXsString().upper()

    print(f"Awinda master opened: {pi.portName()} @ {pi.baudrate()}  product={master.productCode()}  id={master_id}")

    cb = PacketBuffer()
    master.addCallbackHandler(cb)

    # --- CONFIG MODE ---
    print("Going to CONFIG...")
    if not master.gotoConfig():
        print("[WARN] master.gotoConfig() returned False (continuing)")

    # Make sure radio is disabled before changing rate (less flaky)
    try:
        if master.isRadioEnabled():
            print("Radio is enabled -> disabling radio first...")
            master.disableRadio()
            time.sleep(0.3)
    except Exception:
        pass

    # --- SET MASTER RATE (THIS IS THE KEY) ---
    rate_ok = try_set_master_rate(master, TARGET_RATE_HZ)
    if not rate_ok:
        print("[WARN] Could not confirm master updateRate set to target. You may stay at ~40 Hz.")

    # --- ENABLE RADIO ---
    # If your station already has a channel configured, you could read master.radioChannel(),
    # but we just force PREFERRED_CHANNEL like MT Manager.
    print(f"Enabling radio on channel {PREFERRED_CHANNEL} ...")
    if not master.enableRadio(PREFERRED_CHANNEL):
        raise RuntimeError("enableRadio(channel) failed")

    print("\nUndock sensors now and move them slightly for 25–30 seconds.\n")

    # Encourage connections (MT Manager effectively does repeated accept)
    t0 = time.time()
    accept_window = 30.0
    while time.time() - t0 < accept_window:
        if MTW_IDS_ALLOWLIST:
            for did in MTW_IDS_ALLOWLIST:
                try:
                    master.acceptConnection(did)
                except Exception:
                    pass
        time.sleep(0.2)

    # --- MEASUREMENT MODE ---
    print("Starting measurement on wireless master ...")
    if not master.gotoMeasurement():
        raise RuntimeError("master.gotoMeasurement() failed")

    print("\nStreaming to LSL. Open LabRecorder. Ctrl+C to stop.\n")

    outlets = {}
    last_seen = {}
    n_samples = {}

    # arrival-rate estimate
    last_report_t = time.time()
    last_report_n = {}

    # packetCounter-based estimate
    pc_last = {}
    pc_t_last = {}
    hz_pc = {}

    try:
        while True:
            item = cb.pop()
            if item is not None:
                src_id, pkt = item

                # ignore master packets
                if src_id == master_id:
                    continue

                # allowlist filter (optional)
                if MTW_IDS_ALLOWLIST and (src_id not in [x.upper() for x in MTW_IDS_ALLOWLIST]):
                    continue

                if src_id not in outlets:
                    outlets[src_id] = make_outlet(src_id)
                    last_seen[src_id] = 0.0
                    n_samples[src_id] = 0
                    last_report_n[src_id] = 0
                    print(f"[NEW] LSL stream created: {LSL_PREFIX}_{src_id}")

                # push to LSL
                outlets[src_id].push_sample(packet_to_sample(pkt), local_clock())

                now = time.time()
                last_seen[src_id] = now
                n_samples[src_id] += 1

                # compute Hz from packetCounter
                try:
                    pc = int(pkt.packetCounter())
                except Exception:
                    pc = None

                if pc is not None:
                    if src_id in pc_last:
                        dt = now - pc_t_last[src_id]
                        dpc = pc - pc_last[src_id]
                        if dt > 0.2 and dpc >= 0:
                            hz_pc[src_id] = dpc / dt
                    pc_last[src_id] = pc
                    pc_t_last[src_id] = now

            # periodic stats
            now = time.time()
            if now - last_report_t >= 2.0:
                if not outlets:
                    print(f"[STAT] No MTw packets yet. callback_total={cb.total}")
                else:
                    for did in outlets.keys():
                        dt = now - last_report_t
                        dn = n_samples[did] - last_report_n.get(did, 0)
                        arrival_hz = dn / dt if dt > 0 else float("nan")

                        age = now - last_seen[did] if last_seen[did] else float("inf")
                        pc_hz_txt = f"{hz_pc.get(did, float('nan')):0.2f} Hz (pc)" if did in hz_pc else "n/a (pc)"

                        print(f"[STAT] {did}: samples={n_samples[did]} last_age={age:0.2f}s | {arrival_hz:0.2f} Hz (arrival) | {pc_hz_txt}")

                        last_report_n[did] = n_samples[did]

                last_report_t = now

            time.sleep(0.001)

    except KeyboardInterrupt:
        print("Stopping...")

    # cleanup
    try:
        master.gotoConfig()
    except Exception:
        pass
    try:
        master.disableRadio()
    except Exception:
        pass

    try:
        control.closePort(pi.portName())
    except Exception:
        pass
    try:
        control.close()
    except Exception:
        pass

    print("Closed.")


if __name__ == "__main__":
    main()
