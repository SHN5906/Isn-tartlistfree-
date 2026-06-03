#!/bin/bash
cd "$(dirname "$0")"

# 1. Vérification de Python
if ! command -v python3 &> /dev/null
then
    echo "Python n'est pas installe."
    if command -v brew &> /dev/null
    then
        echo "Installation de Python via Homebrew..."
        brew install python
    else
        echo "Veuillez installer Python (brew install python)"
        exit
    fi
fi

# 2. Vérification de Tkinter (souvent manquant sur Homebrew Python)
python3 -c "import _tkinter" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Support graphique (Tkinter) manquant. Installation..."
    if command -v brew &> /dev/null
    then
        # On essaie d'installer python-tk (version générique ou spécifique)
        brew install python-tk
    else
        echo "Erreur : Tkinter est absent. Veuillez l'installer manuellement."
        exit
    fi
fi

# 3. Gestion de l'environnement virtuel (VENV)
if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv .venv
fi

# 4. Activation de l'environnement virtuel
source .venv/bin/activate

# 5. Installation/Mise à jour des dépendances
echo "Vérification des dépendances..."
pip install -r requirements.txt --quiet

# 6. Lancement de l'application
echo "Lancement de l'application..."
python app.py

deactivate
