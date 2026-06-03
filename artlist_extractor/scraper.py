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

    # 3. Tentative d'extraction depuis JSON __NEXT_DATA__
    next_data = soup.find("script", id="__NEXT_DATA__")
    if next_data:
        try:
            data = json.loads(next_data.string)
            # Recherche récursive de liens de média dans le JSON
            data_str = json.dumps(data)
            
            # Audio patterns dans le JSON
            audio_json_matches = re.findall(r'https://[^\s"\'<>\\\]]+?\.(?:aac|mp3|wav|m4a)(?:\?[^\s"\'<>\\\]]+)?', data_str)
            if audio_json_matches:
                # On privilégie les liens qui contiennent "artifacts" ou "artlist"
                for match in audio_json_matches:
                    if "artifacts" in match or "artlist" in match:
                        audio_url = match
                        break
                if not audio_url: audio_url = audio_json_matches[0]

            # Video patterns dans le JSON
            video_json_matches = re.findall(r'https://[^\s"\'<>\\\]]+?\.(?:m3u8|mp4)(?:\?[^\s"\'<>\\\]]+)?', data_str)
            if video_json_matches:
                for match in video_json_matches:
                    if "artifacts" in match or "artlist" in match:
                        video_url = match
                        break
                if not video_url: video_url = video_json_matches[0]
        except:
            pass

    # 4. Fallback sur regex globales si non trouvé dans le JSON
    if not audio_url:
        audio_matches = re.findall(r'https://[^\s"\'<>\\\]]+?\.(?:aac|mp3|wav|m4a)(?:\?[^\s"\'<>\\\]]+)?', norm_html)
        for match in audio_matches:
            if "artifacts" in match or "artlist" in match:
                audio_url = match
                break
    
    if not video_url:
        video_matches = re.findall(r'https://[^\s"\'<>\\\]]+?\.(?:m3u8|mp4)(?:\?[^\s"\'<>\\\]]+)?', norm_html)
        for match in video_matches:
            if "artifacts" in match or "artlist" in match:
                video_url = match
                break

    # 5. Fallback ultime BeautifulSoup
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
