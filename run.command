#!/bin/bash
cd "$(dirname "$0")"
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
echo "Vérification des dépendances..."
pip3 install -r requirements.txt --quiet
echo "Lancement de l'application..."
python3 app.py
