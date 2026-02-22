import os
import urllib.request

# Resolve paths relative to this file's directory
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_HERE, "data")


def download_alarm():
    url = "https://github.com/opencv/opencv/raw/4.x/samples/data/alarm.wav"
    output_path = os.path.join(_DATA_DIR, "alarm.wav")

    os.makedirs(_DATA_DIR, exist_ok=True)

    try:
        print("Telechargement du fichier audio d'alarme...")
        urllib.request.urlretrieve(url, output_path)
        print(f"Fichier audio telecharge avec succes dans {output_path}")
    except Exception as e:
        print(f"Erreur lors du telechargement : {e}")
        print("Veuillez telecharger manuellement un fichier 'alarm.wav' dans le dossier data/")


if __name__ == "__main__":
    download_alarm()
