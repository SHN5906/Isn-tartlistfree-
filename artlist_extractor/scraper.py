import yt_dlp
from bs4 import BeautifulSoup
import os
import re
import json
import base64

def extract_media_info(html_content):
    """
    Analyse le contenu HTML pour trouver les URLs de média et le titre.
    """
    audio_url = None
    video_url = None
    title = "extraction_artlist"

    # 1. Extraction du titre
    soup = BeautifulSoup(html_content, 'html.parser')
    meta_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "title"})
    if meta_title:
        title = meta_title.get("content", title)
    else:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.text

    title = re.sub(r'\s*\|\s*Artlist.*$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*-\s*Royalty Free Music.*$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[\\/*?:"<>|]', "", title).strip()

    # 2. Normalisation du HTML
    norm_html = html_content.replace('\\/', '/')

    # 3. Tentative d'extraction depuis JSON __NEXT_DATA__ ou scripts
    scripts = soup.find_all("script")
    potential_json_str = ""
    for script in scripts:
        if script.string and ("https://" in script.string) and (".mp3" in script.string or ".aac" in script.string or ".m3u8" in script.string):
            potential_json_str += script.string

    # Recherche large de patterns de médias dans tout le code source
    def find_best_match(patterns, text, priority_keywords=["artifacts", "artlist", "cloudfront"]):
        matches = re.findall(patterns, text)
        if not matches: return None
        # Priorité aux liens officiels Artlist
        for match in matches:
            if any(k in match.lower() for k in priority_keywords):
                return match
        return matches[0]

    audio_url = find_best_match(r'https://[^\s"\'<>\\\]]+?\.(?:aac|mp3|wav|m4a)(?:\?[^\s"\'<>\\\]]+)?', norm_html + potential_json_str)
    video_url = find_best_match(r'https://[^\s"\'<>\\\]]+?\.(?:m3u8|mp4)(?:\?[^\s"\'<>\\\]]+)?', norm_html + potential_json_str)

    # 4. Fallback ultime BeautifulSoup
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
    Méthode de repli utilisant yt-dlp.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
        'extract_flat': False,
        'ignoreerrors': True,
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
            # On force l'extraction même si le site semble bloqué
            result = ydl.extract_info(url, download=True)
            return True if result else False
    except Exception as e:
        print(f"[!] Erreur yt-dlp : {e}")
        return False
