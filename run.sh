#!/bin/bash
if ! command -v python3 &> /dev/null
then
    echo "Python n'est pas installe."
    if command -v brew &> /dev/null
    then
        echo "Installation via Homebrew..."
        brew install python
    else
        echo "Veuillez installer Python via https://www.python.org/downloads/"
        exit
    fi
fi
pip3 install -r requirements.txt --quiet
python3 -m artlist_extractor.cli