import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import sys
from curl_cffi import requests

# Import de la logique existante
try:
    from artlist_extractor.scraper import extract_media_info, fallback_yt_dlp
    from artlist_extractor.utils import download_file, clean_path
except ImportError:
    from scraper import extract_media_info, fallback_yt_dlp
    from utils import download_file, clean_path

class ArtlistApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Isn't Artlist Free? - GUI")
        self.geometry("600x500")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        
        # Titre
        self.label_title = ctk.CTkLabel(self, text="Artlist Downloader", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 5))

        # Mention légale
        self.label_disclaimer = ctk.CTkLabel(self, text="À but personnel et éducatif uniquement", font=ctk.CTkFont(size=12, slant="italic"), text_color="orange")
        self.label_disclaimer.grid(row=1, column=0, padx=20, pady=(0, 10))

        # Lien Artlist
        self.label_url = ctk.CTkLabel(self, text="Lien Artlist (Musique ou Vidéo) :")
        self.label_url.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.entry_url = ctk.CTkEntry(self, placeholder_text="Collez votre lien ici...", width=500)
        self.entry_url.grid(row=3, column=0, padx=20, pady=(0, 20))

        # Dossier de destination
        self.label_dest = ctk.CTkLabel(self, text="Dossier de destination :")
        self.label_dest.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.dest_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dest_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.dest_frame.grid_columnconfigure(0, weight=1)

        self.entry_dest = ctk.CTkEntry(self.dest_frame, placeholder_text="Dossier par défaut : downloads")
        self.entry_dest.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_dest.insert(0, os.path.join(os.getcwd(), "downloads"))

        self.btn_browse = ctk.CTkButton(self.dest_frame, text="Parcourir", width=100, command=self.browse_folder)
        self.btn_browse.grid(row=0, column=1)

        # Bouton Télécharger
        self.btn_download = ctk.CTkButton(self, text="Télécharger", command=self.start_download_thread, height=40, font=ctk.CTkFont(size=15, weight="bold"))
        self.btn_download.grid(row=6, column=0, padx=20, pady=10)

        # Statut
        self.status_label = ctk.CTkLabel(self, text="Prêt", text_color="gray")
        self.status_label.grid(row=7, column=0, padx=20, pady=5)

        self.log_box = ctk.CTkTextbox(self, height=100, width=500)
        self.log_box.grid(row=8, column=0, padx=20, pady=(5, 20))
        self.log_box.configure(state="disabled")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_dest.delete(0, "end")
            self.entry_dest.insert(0, folder)

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_status(self, text, color="gray"):
        self.status_label.configure(text=text, text_color=color)

    def start_download_thread(self):
        url = self.entry_url.get().strip()
        dest = self.entry_dest.get().strip()
        
        if not url:
            self.update_status("Erreur : Veuillez entrer un lien", "red")
            return

        self.btn_download.configure(state="disabled")
        self.update_status("Analyse en cours...", "blue")
        self.log(f"[*] Début de l'analyse : {url}")
        
        thread = threading.Thread(target=self.run_download, args=(url, dest), daemon=True)
        thread.start()

    def run_download(self, url, output_dir):
        try:
            output_dir = clean_path(output_dir)
            if not output_dir:
                output_dir = os.path.join(os.getcwd(), "downloads")

            self.log("[*] Connexion à Artlist...")
            response = requests.get(url, impersonate="chrome110", timeout=15, allow_redirects=True)
            response.raise_for_status()
            html_content = response.text
            final_url = response.url

            info = extract_media_info(html_content)
            audio_url = info["audio_url"]
            video_url = info["video_url"]
            title = info["title"]
            
            self.log(f"[+] Titre trouvé : {title}")
            
            success = False
            headers_fallback = {"Referer": "https://artlist.io/", "Origin": "https://artlist.io"}
            
            if audio_url or video_url:
                is_video_context = "video" in final_url.lower() or "stock-footage" in final_url.lower()
                
                if video_url and is_video_context:
                    self.log("[+] Média détecté : Clip Vidéo")
                    if ".m3u8" in video_url:
                        success = fallback_yt_dlp(video_url, output_dir, headers=headers_fallback)
                    else:
                        success = download_file(video_url, output_dir, f"{title}.mp4", referer=final_url)
                elif audio_url:
                    self.log("[+] Média détecté : Piste Audio")
                    ext = "aac" if "aac" in audio_url or "Y29u" in audio_url else "mp3"
                    success = download_file(audio_url, output_dir, f"{title}.{ext}", referer=final_url)
                elif video_url:
                    self.log("[+] Média détecté : Vidéo (Fallback)")
                    if ".m3u8" in video_url:
                        success = fallback_yt_dlp(video_url, output_dir, headers=headers_fallback)
                    else:
                        success = download_file(video_url, output_dir, f"{title}.mp4", referer=final_url)
            
            if not success:
                self.log("[!] Scraping direct insuffisant. Tentative yt-dlp...")
                success = fallback_yt_dlp(final_url, output_dir, headers=headers_fallback)

            if success:
                self.update_status("Téléchargement terminé !", "green")
                self.log(f"[SUCCESS] '{title}' téléchargé avec succès.")
            else:
                self.update_status("Échec du téléchargement", "red")
                self.log("[ERROR] Impossible de télécharger le média.")

        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            self.update_status("Erreur système", "red")
        
        finally:
            self.btn_download.configure(state="normal")

if __name__ == "__main__":
    app = ArtlistApp()
    app.mainloop()
