# Isn't Artlist Free?

Un outil simple pour extraire et télécharger des médias depuis Artlist.

## 🚀 Guide pour les débutants (Sans savoir coder)

### 1. Prérequis (À ne faire qu'une fois)
*   **Installer Python** : Téléchargez et installez la version la plus récente sur [python.org](https://www.python.org/downloads/). 
    *   **Important (Windows)** : Pendant l'installation, cochez bien la case **"Add Python to PATH"**.

### 2. Installation du programme
1.  Téléchargez ce projet (bouton vert "Code" > "Download ZIP" sur GitHub) et décompressez-le.
2.  Ouvrez un terminal (ou une invite de commande) dans le dossier du projet.
3.  Tapez la commande suivante pour installer les outils nécessaires :
    ```bash
    pip install -r requirements.txt
    ```

### 3. Utilisation
Pour lancer le programme, tapez simplement :
```bash
python -m artlist_extractor.cli
```
Ensuite, suivez les instructions qui s'affichent à l'écran (collez votre lien Artlist et choisissez le dossier de destination).

---

## 🛠 Pour les développeurs

```bash
# Installation
pip install -r requirements.txt

# Lancement
python -m artlist_extractor.cli
```


