# Isn't Artlist Free?

Un outil simple pour extraire et télécharger des médias depuis Artlist.

## 🚀 Guide de lancement (macOS / Linux)

1.  **Téléchargez et décompressez** le projet.
2.  **Lancez le programme** :
    *   **Double-cliquez sur `run.command`**
    *   *Ou dans un terminal :* `./run.command`

*Le script vérifiera si Python est installé et installera les dépendances automatiquement.*

---

## 📖 Installation manuelle

### 1. Prérequis (Installer Python)

Ouvrez un terminal et collez la commande correspondant à votre système :

*   **macOS** : `brew install python`
*   **Linux** : `sudo apt update && sudo apt install python3`

### 2. Lancement

Une fois Python installé, tapez ces commandes dans le dossier du projet :
```bash
pip3 install -r requirements.txt
python3 -m artlist_extractor.cli
```
