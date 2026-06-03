import yt_dlp
from bs4 import BeautifulSoup
import os
import re
import json
import base64

def extract_media_info(html_content):
    """
    Analyse le contenu HTML pour trouver les URLs de média et le titre.
    Retourne un dictionnaire avec audio_url, video_url et title.
    """
    audio_url = None
    video_url = None
    title = "extraction_artlist"

    # Extraction du titre via les balises meta ou title
    soup = BeautifulSoup(html_content, 'html.parser')
    og_title = soup.find("meta", property="og:title")
    if og_title:
        title = og_title.get("content", title)
    else:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.text

    # Nettoyage du titre pour le système de fichiers
    title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    if " | Artlist" in title:
        title = title.split(" | Artlist")[0]

    # Extraction des URLs HLS pour la vidéo (.m3u8)
    video_matches = re.findall(r'https://cms-public-artifacts\.artlist\.io/([^\s"\'<>\\\]]+?\.m3u8)', html_content.replace('\\/', '/'))
    if video_matches:
        video_url = "https://cms-public-artifacts.artlist.io/" + video_matches[0]

    # Extraction de l'URL audio
    audio_matches = re.findall(r'sitePlayableFilePath.+?(https://cms-public-artifacts\.artlist\.io/([^\s"\'<>\\\]]+))', html_content.replace('\\/', '/'))
    if not audio_matches:
        audio_matches = re.findall(r'https://cms-public-artifacts\.artlist\.io/([^\s"\'<>\\\]]+?\.?(?:aac|mp3))', html_content.replace('\\/', '/'))
    
    if audio_matches:
        url = audio_matches[0]
        if isinstance(url, tuple):
            url = url[0]
        if not url.startswith("http"):
            url = "https://cms-public-artifacts.artlist.io/" + url
        audio_url = url
    
    # Fallback BeautifulSoup pour les URLs
    if not audio_url:
        audio_tag = soup.find('audio')
        if audio_tag:
            audio_url = audio_tag.get('src') or (audio_tag.find('source').get('src') if audio_tag.find('source') else None)
    
    if not video_url:
        video_tag = soup.find('video')
        if video_tag:
            video_url = video_tag.get('src') or (video_tag.find('source').get('src') if video_tag.find('source') else None)

    return {
        "audio_url": audio_url,
        "video_url": video_url,
        "title": title
    }

def fallback_yt_dlp(url, output_dir, headers=None):
    """
    Méthode de repli utilisant yt-dlp pour extraire et télécharger le média.
    """
    print(f"[*] Tentative avec yt-dlp pour : {url}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    if headers:
        ydl_opts['http_headers'] = headers
    else:
        ydl_opts['http_headers'] = {
            'Referer': 'https://artlist.io/',
            'Origin': 'https://artlist.io'
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"[!] Erreur yt-dlp : {e}")
        return False
