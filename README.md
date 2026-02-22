# SafeDrive — Detecteur de Somnolence et de Distractions

Systeme de detection de somnolence et de distractions au volant utilisant la vision par ordinateur et MediaPipe.

## Fonctionnalites

- **Yeux fermes** — minuteur configurable (defaut 20 s) avant alarme sonore
- **Baillements** — ratio d'aspect de la bouche (MAR), compteur de baillements consecutifs
- **Position de la tete** — rotation horizontale et inclinaison verticale
- **Telephone** — detection heuristique de la main tenant un telephone
- **Alertes** — 3 niveaux (NORMAL / WARNING / DANGER) avec son et couleur

## Structure du projet

```
SafeDrive/
|-- main.py                  # Point d'entree
|-- config.yaml              # Configuration utilisateur (optionnel)
|-- config_default.yaml      # Reference avec tous les defauts
|-- requirements.txt
|-- requirements-dev.txt     # pytest
|-- safedrive/
|   |-- __init__.py
|   |-- config.py            # Dataclasses + chargement YAML
|   |-- constants.py         # Indices landmarks MediaPipe
|   |-- alert_system.py      # Alertes sonores (pygame)
|   |-- display.py           # Affichage HUD (cv2)
|   |-- logger.py            # Logging Python standard
|   |-- detectors/
|       |-- __init__.py
|       |-- eye_detector.py
|       |-- mouth_detector.py
|       |-- head_detector.py
|       |-- phone_detector.py
|-- tests/
|   |-- conftest.py
|   |-- test_eye_detector.py
|   |-- test_mouth_detector.py
|   |-- test_head_detector.py
|   |-- test_phone_detector.py
|   |-- test_alert_system.py
|   |-- test_config.py
|-- data/
|   |-- alarm.wav
```

## Installation

```bash
git clone <URL_DU_REPO>
cd SafeDrive

# Environnement virtuel
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

# Dependances
pip install -r requirements.txt

# Fichier son d'alarme (au choix)
python create_alarm.py     # genere un ton 440 Hz
python download_alarm.py   # telecharge depuis OpenCV samples
```

## Utilisation

```bash
# Avec les defauts
python main.py

# Avec une configuration personnalisee
python main.py --config config.yaml
```

Copiez `config_default.yaml` vers `config.yaml` et modifiez les valeurs souhaitees. Si aucun fichier n'est fourni, les defauts s'appliquent.

### Commandes

- **q** — quitter

## Configuration

Tous les parametres sont configurables via `config.yaml` :

| Parametre | Defaut | Description |
|-----------|--------|-------------|
| `detection.eye_closed_threshold` | 0.02 | Sensibilite yeux fermes |
| `detection.mouth_open_threshold` | 0.4 | Seuil baillement |
| `detection.mouth_aspect_ratio_threshold` | 0.6 | MAR baillement |
| `detection.head_rotation_threshold` | 0.2 | Rotation tete |
| `detection.head_tilt_threshold` | 0.1 | Inclinaison tete |
| `detection.eyes_closed_time_threshold` | 20.0 | Secondes avant alarme |
| `detection.phone_detection_threshold` | 5.0 | Secondes avant alerte telephone |
| `camera.index` | 0 | Index camera OpenCV |
| `alert.alarm_path` | data/alarm.wav | Chemin du fichier son |

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Deploiement VPS

Voir [deployment.md](deployment.md) pour le guide complet.

```bash
sudo ./deploy.sh
```

## Depannage

1. **Camera non detectee** — essayez un autre index dans `config.yaml`
2. **Detection imprecise** — ameliorez l'eclairage, ajustez les seuils
3. **Faux positifs telephone** — augmentez `phone_detection_threshold`

## Securite

Ce systeme est une aide a la vigilance et ne remplace pas une conduite responsable, des pauses regulieres et le respect du code de la route.

## Licence

MIT — voir le fichier `LICENSE`.
