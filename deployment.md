# Guide de Deploiement sur VPS

## Prerequis VPS

- Ubuntu 20.04 ou plus recent
- Au moins 2 GB de RAM
- 20 GB d'espace disque
- Acces SSH root ou sudo

## 1. Installation des Dependances Systeme

```bash
sudo apt update
sudo apt upgrade -y

sudo apt install -y python3-pip python3-opencv libopencv-dev python3-venv ffmpeg
sudo apt install -y libsm6 libxext6 libxrender-dev libglib2.0-0
```

## 2. Configuration de l'Environnement

```bash
mkdir -p /opt/drowsiness_detector
cd /opt/drowsiness_detector

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configuration du Service Systemd

Creez le fichier service :

```bash
sudo nano /etc/systemd/system/drowsiness_detector.service
```

Contenu :
```ini
[Unit]
Description=Drowsiness Detector Service
After=network.target

[Service]
Type=simple
User=drowsiness
WorkingDirectory=/opt/drowsiness_detector
Environment=DISPLAY=:0
Environment=PYTHONPATH=/opt/drowsiness_detector
ExecStart=/opt/drowsiness_detector/venv/bin/python main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

> **Note :** Le service tourne sous l'utilisateur `drowsiness` (et non `root`) pour des raisons de securite.

## 4. Configuration de X11 (affichage)

```bash
sudo apt install -y xorg x11vnc xvfb

sudo nano /etc/X11/xorg.conf
```

Contenu de xorg.conf :
```conf
Section "Device"
    Identifier "Dummy Driver"
    Driver "dummy"
EndSection

Section "Monitor"
    Identifier "Dummy Monitor"
EndSection

Section "Screen"
    Identifier "Dummy Screen"
    Device "Dummy Driver"
    Monitor "Dummy Monitor"
    DefaultDepth 24
    SubSection "Display"
        Depth 24
        Modes "1920x1080"
    EndSubSection
EndSection
```

## 5. Script de Deploiement

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

Le script `deploy.sh` automatise toutes les etapes ci-dessus.

## 6. Commandes de Gestion

```bash
sudo systemctl start drowsiness_detector
sudo systemctl stop drowsiness_detector
sudo systemctl restart drowsiness_detector
sudo journalctl -u drowsiness_detector -f
sudo systemctl status drowsiness_detector
```

## 7. Configuration de la Camera

Pour une camera IP ou webcam reseau, creez un fichier `config.yaml` :

```yaml
camera:
  index: 0  # ou une URL RTSP : "rtsp://user:pass@ip:554/stream1"
```

## 8. Securite

Le script `deploy.sh` applique automatiquement :

1. **Pare-feu** — SSH est autorise *avant* l'activation de ufw pour eviter le verrouillage :
   ```bash
   sudo ufw allow ssh
   sudo ufw --force enable
   ```

2. **Utilisateur dedie** — le service tourne sous `drowsiness`, pas `root` :
   ```bash
   sudo useradd -m -s /bin/bash drowsiness
   sudo usermod -a -G video drowsiness
   ```

3. **Permissions** :
   ```bash
   sudo chown -R drowsiness:drowsiness /opt/drowsiness_detector
   sudo chmod -R 755 /opt/drowsiness_detector
   ```

## 9. Surveillance

```bash
sudo apt install -y htop
sudo apt install -y netdata
```

## 10. Sauvegarde

Le script `backup.sh` est cree automatiquement par `deploy.sh` dans `/opt/drowsiness_detector/`.

```bash
sudo -u drowsiness /opt/drowsiness_detector/backup.sh
```

## Depannage

1. Affichage :
   ```bash
   export DISPLAY=:0
   sudo Xvfb :0 -screen 0 1920x1080x24 &
   ```

2. Camera non detectee :
   ```bash
   ls -l /dev/video*
   sudo usermod -a -G video drowsiness
   ```

3. Service ne demarre pas :
   ```bash
   sudo systemctl status drowsiness_detector
   sudo journalctl -u drowsiness_detector -n 50
   ```
