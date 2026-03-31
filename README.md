# PatOpenCV — Superposition Visage en Temps Réel

![macOS](https://img.shields.io/badge/macOS-11%2B-black?logo=apple)
![Windows](https://img.shields.io/badge/Windows-10%2B-blue?logo=windows)
![Python](https://img.shields.io/badge/Python-3.9%2B-yellow?logo=python)
![CPU only](https://img.shields.io/badge/CPU-only-green)

Détecte les visages en temps réel via webcam et superpose un GIF animé rotatif calé sur l'angle du visage. Ajoutez optionnellement votre photo en petit cercle à gauche du GIF.

---

## Fonctionnalités

- Détection visage temps réel via modèle UltraFace (ONNX)
- GIF animé rotatif synchronisé avec l'inclinaison de la tête (landmarks LBF)
- Image optionnelle affichée en cercle masqué à gauche du GIF
- GUI moderne tkinter avec effets de survol, zone de sélection et indicateur de statut
- Compilable en exécutable autonome — aucun Python requis pour l'utilisateur final

---

## Installation — macOS

### 1. Prérequis
- Python 3.9+ (`python3 --version`)
- Git

### 2. Cloner le dépôt
```bash
git clone https://github.com/TheArabicMonster/PatOpenCV.git
cd PatOpenCV
```

### 3. Environnement virtuel & dépendances
```bash
python3 -m venv venv
source venv/bin/activate
pip install opencv-contrib-python onnxruntime numpy Pillow
```

> **tkinter manquant ?**
> ```bash
> brew install python-tk@3.14
> ```

### 4. Télécharger les modèles
```bash
curl -L -o ultra_light_320.onnx \
  "https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB/raw/master/models/onnx/version-RFB-320.onnx"

curl -L -o lbfmodel.yaml \
  "https://raw.githubusercontent.com/kurnianggoro/GSOC2017/master/data/lbfmodel.yaml"
```

### 5. Lancer
```bash
python gui.py
```

---

## Installation — Windows

### 1. Prérequis
- [Python 3.9+](https://www.python.org/downloads/) — cocher **"Add Python to PATH"** et **"tcl/tk"** à l'installation
- [Git pour Windows](https://git-scm.com/download/win)

### 2. Cloner le dépôt
```bat
git clone https://github.com/TheArabicMonster/PatOpenCV.git
cd PatOpenCV
```

### 3. Environnement virtuel & dépendances
```bat
python -m venv venv
venv\Scripts\activate
pip install opencv-contrib-python onnxruntime numpy Pillow
```

### 4. Télécharger les modèles

**Option A — curl (Windows 10+) :**
```bat
curl -L -o ultra_light_320.onnx "https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB/raw/master/models/onnx/version-RFB-320.onnx"
curl -L -o lbfmodel.yaml "https://raw.githubusercontent.com/kurnianggoro/GSOC2017/master/data/lbfmodel.yaml"
```

**Option B — PowerShell :**
```powershell
Invoke-WebRequest -Uri "https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB/raw/master/models/onnx/version-RFB-320.onnx" -OutFile ultra_light_320.onnx
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kurnianggoro/GSOC2017/master/data/lbfmodel.yaml" -OutFile lbfmodel.yaml
```

### 5. Lancer
```bat
python gui.py
```

---

## Utilisation

**GUI (recommandé)**
1. `python gui.py`
2. Cliquer sur la zone de sélection pour choisir une image (optionnel)
3. Cliquer **Démarrer avec image** ou **GIF seul**
4. La fenêtre webcam s'ouvre — visage détecté → GIF superposé
5. **ESC** pour fermer la webcam

**CLI**
```bash
python app.py                            # GIF seul
python app.py --image ermmmactually.jpg  # GIF + image
```

---

## Compiler en exécutable autonome

Permet de distribuer l'app sans que l'utilisateur installe Python.

### Prérequis
```bash
pip install pyinstaller
```

### macOS → `.app`
```bash
bash build.sh
# Résultat : dist/PatOpenCV.app  (double-clic pour lancer)
```

### Windows → `.exe`
```bat
build.bat
REM Résultat : dist\PatOpenCV.exe  (double-clic pour lancer)
```

> **Important :** le build doit être lancé sur chaque OS séparément. PyInstaller ne fait pas de cross-compilation.

Pour distribuer : zipper le dossier `dist/`.

---

## Dépannage

| Problème | macOS | Windows |
|---|---|---|
| `No module '_tkinter'` | `brew install python-tk@3.14` | Réinstaller Python en cochant "tcl/tk" |
| Permission caméra refusée | Préférences Système → Sécurité → Caméra | Paramètres → Confidentialité → Caméra |
| Modèle introuvable | Relancer les commandes `curl` | Relancer curl ou PowerShell |
| App lente | Réduire `intra_op_num_threads = 2` dans `app.py` | Idem |
| `.exe` bloqué | — | Ajouter une exception dans Windows Defender |
| Webcam non détectée | Vérifier `cv2.VideoCapture(0)` → essayer `1` | Idem |

---

## Fichiers du projet

| Fichier | Description |
|---|---|
| `app.py` | Script principal (CLI + importable) |
| `gui.py` | GUI native tkinter |
| `gui_streamlit.py` | GUI web alternative (fallback) |
| `patHand.gif` | GIF animé par défaut |
| `ermmmactually.jpg` | Image d'exemple incluse |
| `ultra_light_320.onnx` | Modèle détection visage (à télécharger) |
| `lbfmodel.yaml` | Modèle landmarks faciaux (à télécharger) |
| `PatOpenCV.spec` | Configuration PyInstaller (build) |
| `build.sh` | Script de compilation macOS |
| `build.bat` | Script de compilation Windows |
| `entitlements.plist` | Permissions webcam pour macOS |
