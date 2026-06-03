# Isn't Artlist Free?

Un outil simple pour extraire et télécharger des médias depuis Artlist.

## 🚀 Guide de lancement (macOS / Linux)

1.  **Téléchargez et décompressez** le projet.
2.  **Lancez le programme** :
    *   Double-cliquez sur `run.sh`
    *   *Ou dans un terminal :* `./run.sh`

*Le script vérifiera si Python est installé et installera les dépendances automatiquement.*

---

## 📖 Installation manuelle

### 1. Prérequis
Assurez-vous d'avoir Python 3 installé :
```bash
brew install python  # macOS
sudo apt install python3  # Linux
```

### 2. Lancement
Ouvrez un terminal dans le dossier et tapez :
```bash
pip3 install -r requirements.txt
python3 -m artlist_extractor.cli
```