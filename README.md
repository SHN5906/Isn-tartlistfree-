# Isn't Artlist Free?

Un outil simple pour extraire et télécharger des médias depuis Artlist.

## 🚀 Guide ultra-rapide (Double-clic)

1.  **Téléchargez et décompressez** le projet (bouton vert "Code" > "Download ZIP").
2.  **Lancez le programme** :
    *   **Sur Windows** : Double-cliquez sur `run.bat`.
    *   **Sur macOS** : Double-cliquez sur `run.sh` (ou lancez-le via un terminal avec `./run.sh`).

*Le script vérifiera si Python est là. S'il manque, il tentera de l'installer pour vous.*

---

## 📖 Guide manuel (Si le double-clic ne marche pas)

### 1. Installation de Python
*   **Windows** : `winget install -e --id Python.Python.3.12`
*   **macOS** : `brew install python`
*   **Manuel** : [python.org](https://www.python.org/downloads/) (Cochez bien **"Add Python to PATH"**).

### 2. Lancement
Ouvrez un terminal dans le dossier et tapez :
```bash
pip install -r requirements.txt
python -m artlist_extractor.cli
```
