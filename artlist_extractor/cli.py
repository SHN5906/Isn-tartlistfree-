from curl_cffi import requests
import argparse
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
try:
    from artlist_extractor.scraper import extract_media_urls, fallback_yt_dlp
    from artlist_extractor.utils import download_file, clean_path
except ImportError:
    from scraper import extract_media_urls, fallback_yt_dlp
    from utils import download_file, clean_path

console = Console()

def display_banner():
    banner = """
    ╔═╗┬─┐┌─┐┌─┐  ╔═╗┬─┐┌┬┐┬  ┬┌─┐┌┬┐  ┌┐ ┬ ┬  ┌─┐
    ╠╣ ├┬┘├┤ ├┤   ╠═╣├┬┘ │ │  │└─┐ │   ├┴┐└┬┘  └─┐
    ╚  ┴└─└─┘└─┘  ╩ ╩┴└─ ┴ ┴─┘┴└─┘ ┴   └─┘ ┴   └─┘
    """
    console.print(Panel(banner, subtitle="Free Artlist by S", border_style="cyan"))

def run_extraction(url, output_dir):
    console.print(f"\n[bold blue][*][/bold blue] Analyse du lien : [underline]{url}[/underline]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console
        ) as progress:
            progress.add_task(description="Connexion à Artlist...", total=None)
            response = requests.get(url, impersonate="chrome110", timeout=15, allow_redirects=True)
            response.raise_for_status()
            html_content = response.text
            final_url = response.url
    except Exception as e:
        console.print(f"[bold red][!][/bold red] Erreur de connexion : {e}")
        console.print("[yellow][*][/yellow] Activation du plan de secours (yt-dlp)...")
        return fallback_yt_dlp(url, output_dir)

    audio_url, video_url = extract_media_urls(html_content)
    
    success = False
    headers_fallback = {"Referer": "https://artlist.io/", "Origin": "https://artlist.io"}
    
    if audio_url or video_url:
        is_video_context = "video" in final_url.lower() or "stock-footage" in final_url.lower()
        
        if video_url and is_video_context:
            console.print("[bold green][+][/bold green] Média détecté : [cyan]Clip Vidéo[/cyan]")
            if ".m3u8" in video_url:
                success = fallback_yt_dlp(video_url, output_dir, headers=headers_fallback)
            else:
                success = download_file(video_url, output_dir, "extraction_artlist.mp4", referer=final_url)
        elif audio_url:
            console.print("[bold green][+][/bold green] Média détecté : [cyan]Piste Audio[/cyan]")
            ext = "aac" if "aac" in audio_url or "Y29u" in audio_url else "mp3"
            success = download_file(audio_url, output_dir, f"extraction_artlist.{ext}", referer=final_url)
        elif video_url:
            console.print("[bold green][+][/bold green] Média détecté : [cyan]Vidéo (Fallback)[/cyan]")
            if ".m3u8" in video_url:
                success = fallback_yt_dlp(video_url, output_dir, headers=headers_fallback)
            else:
                success = download_file(video_url, output_dir, "extraction_artlist.mp4", referer=final_url)
    
    if not success:
        console.print("[bold yellow][!][/bold yellow] Scraping direct insuffisant. Tentative yt-dlp...")
        success = fallback_yt_dlp(final_url, output_dir, headers=headers_fallback)
        
    return success

def main():
    parser = argparse.ArgumentParser(description="Extracteur intelligent Artlist (MP3/MP4)")
    parser.add_argument("url", nargs="?", help="Lien de la page Artlist (Musique ou Vidéo)")
    parser.add_argument("-o", "--output", default="downloads", help="Répertoire de destination")
    
    args = parser.parse_args()
    output_arg = clean_path(args.output)
    
    if args.url:
        success = run_extraction(args.url, output_arg)
        sys.exit(0 if success else 1)
    else:
        display_banner()
        
        output_dir = clean_path(Prompt.ask("[bold magenta]Dossier de destination[/bold magenta]", default="downloads"))
        
        while True:
            url = Prompt.ask("[bold magenta]Entrez le lien Artlist[/bold magenta]")
            if not url:
                continue
            
            success = run_extraction(url, output_dir)
            
            if success:
                console.print("\n[bold green]✨ Téléchargement terminé avec succès ![/bold green]")
            else:
                console.print("\n[bold red]❌ Échec du téléchargement.[/bold red]")
            
            if Prompt.ask("\nEncore un autre lien ?", choices=["y", "n"], default="y") == "n":
                break
        
        console.print("[bold cyan]Au revoir ![/bold cyan]")

if __name__ == "__main__":
    main()
