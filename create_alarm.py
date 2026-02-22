import os

import numpy as np
from scipy.io import wavfile

# Resolve paths relative to this file's directory
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_HERE, "data")


def create_alarm():
    sample_rate = 44100
    duration = 1.0
    frequency = 440.0

    t = np.linspace(0, duration, int(sample_rate * duration))
    signal = np.sin(2 * np.pi * frequency * t)

    envelope = np.ones_like(signal)
    attack = int(0.1 * sample_rate)
    release = int(0.1 * sample_rate)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)
    signal = signal * envelope

    signal = np.int16(signal * 32767)

    os.makedirs(_DATA_DIR, exist_ok=True)
    output_path = os.path.join(_DATA_DIR, "alarm.wav")
    wavfile.write(output_path, sample_rate, signal)
    print(f"Fichier audio cree avec succes dans {output_path}")


if __name__ == "__main__":
    create_alarm()
