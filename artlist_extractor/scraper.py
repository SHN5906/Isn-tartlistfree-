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

    # 1. Extraction du titre (plus robuste)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # On essaie d'abord les balises meta classiques
    meta_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "title"})
    if meta_title:
        title = meta_title.get("content", title)
    else:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.text

    # Nettoyage du titre (Enlever les suffixes Artlist et les caractères interdits)
    title = re.sub(r'\s*\|\s*Artlist.*$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*-\s*Royalty Free Music.*$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[\\/*?:"<>|]', "", title).strip()

    # 2. Extraction des URLs de média
    # On cherche les patterns d'URLs CloudFront d'Artlist
    # Artlist utilise souvent des URLs encodées ou dans des structures JSON complexes
    
    # Pattern pour les fichiers audio (.mp3 ou .aac)
    audio_patterns = [
        r'https://cms-public-artifacts\.artlist\.io/[^\s"\'<>\\\]]+?\.(?:aac|mp3|wav)',
        r'sitePlayableFilePath.+?(https://cms-public-artifacts\.artlist\.io/([^\s"\'<>\\\]]+))'
    ]
    
    # On normalise le HTML en remplaçant les slashs échappés
    norm_html = html_content.replace('\\/', '/')
    
    for pattern in audio_patterns:
        matches = re.findall(pattern, norm_html)
        if matches:
            url = matches[0]
            if isinstance(url, tuple): url = url[0]
            if not url.startswith("http"):
                url = "https://cms-public-artifacts.artlist.io/" + url
            audio_url = url
            break

    # Pattern pour les fichiers vidéo (.m3u8 ou .mp4)
    video_patterns = [
        r'https://cms-public-artifacts\.artlist\.io/[^\s"\'<>\\\]]+?\.m3u8',
        r'https://cms-public-artifacts\.artlist\.io/[^\s"\'<>\\\]]+?\.mp4'
    ]
    
    for pattern in video_patterns:
        matches = re.findall(pattern, norm_html)
        if matches:
            video_url = matches[0]
            break
    
    # 3. Fallback BeautifulSoup pour les balises classiques
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

    # On utilise des options plus agressives pour contourner Cloudflare/WAF
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
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
