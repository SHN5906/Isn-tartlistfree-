#!/bin/bash
cd "$(dirname "$0")"

# 1. Vérification de Python
if ! command -v python3 &> /dev/null
then
    echo "Python n'est pas installe."
    if command -v brew &> /dev/null
    then
        echo "Installation via Homebrew..."
        brew install python
    else
        echo "Veuillez installer Python (brew install python)"
        exit
    fi
fi

# 2. Gestion de l'environnement virtuel (VENV) pour éviter l'erreur "externally-managed-environment"
if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel (une seule fois)..."
    python3 -m venv .venv
fi

# 3. Activation de l'environnement virtuel
source .venv/bin/activate

# 4. Installation/Mise à jour des dépendances
echo "Vérification des dépendances..."
pip install -r requirements.txt --quiet

# 5. Lancement de l'application
echo "Lancement de l'application..."
python app.py

# 6. Désactivation (optionnel car le terminal va se fermer)
deactivate
