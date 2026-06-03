from curl_cffi import requests
import os

def clean_path(path):
    """
    Nettoie un chemin de fichier :
    - Enlève les espaces inutiles
    - Enlève les guillemets (simples ou doubles) au début et à la fin
    - Développe le chemin (~ pour le dossier utilisateur)
    """
    if not path:
        return path
    
    path = path.strip()
    
    # Enlever les guillemets au début et à la fin
    if (path.startswith("'") and path.endswith("'")) or (path.startswith('"') and path.endswith('"')):
        path = path[1:-1]
    
    # Gérer les cas où il n'y a qu'un guillemet au début (copier-coller malheureux)
    path = path.strip("'\"")
        
    return os.path.abspath(os.path.expanduser(path))

def download_file(url, output_dir, filename, referer="https://artlist.io/"):
    """
    Télécharge un fichier depuis une URL et l'enregistre dans le répertoire spécifié.
    Utilise curl-cffi pour contourner les protections et inclut le Referer.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, filename)
    headers = {
        "Referer": referer,
        "Origin": "https://artlist.io",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"[*] Téléchargement en cours : {url}")
        # On essaie d'abord sans impersonation si c'est un artifact S3/CloudFront
        # car l'impersonation peut parfois être bloquée par ces services
        if "cms-public-artifacts" in url:
            response = requests.get(url, headers=headers, timeout=60)
        else:
            response = requests.get(url, headers=headers, impersonate="chrome110", timeout=60)
            
        # Si on a un 403, on tente l'inverse (avec ou sans impersonation)
        if response.status_code == 403:
            print("[*] Tentative alternative pour contourner le 403...")
            if "cms-public-artifacts" in url:
                response = requests.get(url, headers=headers, impersonate="chrome110", timeout=60)
            else:
                response = requests.get(url, headers=headers, timeout=60)

        response.raise_for_status()

        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"[+] Fichier enregistré : {filepath}")
        return True
    except Exception as e:
        print(f"[!] Erreur lors du téléchargement : {e}")
        return False
