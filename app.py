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

        # Fenêtre principale
        self.title("Artlist Downloader")
        self.geometry("650x550")
        
        # Thème Artlist : Sombre avec des touches de Jaune/Or
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue") # On va surcharger les couleurs manuellement

        # Couleurs personnalisées
        self.yellow_artlist = "#FFD700"
        self.bg_dark = "#1A1A1A"
        self.text_gray = "#AAAAAA"

        self.configure(fg_color=self.bg_dark)

        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        
        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="ew")
        
        self.label_title = ctk.CTkLabel(
            self.header_frame, 
            text="ARTLIST", 
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
            text_color=self.yellow_artlist
        )
        self.label_title.pack(side="left")
        
        self.label_subtitle = ctk.CTkLabel(
            self.header_frame, 
            text=" DOWNLOADER", 
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
            text_color="white"
        )
        self.label_subtitle.pack(side="left")

        self.label_disclaimer = ctk.CTkLabel(
            self, 
            text="Usage personnel & éducatif uniquement", 
            font=ctk.CTkFont(size=11, slant="italic"), 
            text_color=self.text_gray
        )
        self.label_disclaimer.grid(row=1, column=0, padx=30, pady=(0, 20), sticky="w")

        # --- INPUT SECTION ---
        self.input_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=15)
        self.input_frame.grid(row=2, column=0, padx=30, pady=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.label_url = ctk.CTkLabel(self.input_frame, text="LIEN DE LA MUSIQUE OU VIDÉO", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_gray)
        self.label_url.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.entry_url = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="https://artlist.io/song/...", 
            height=45, 
            fg_color="#333333", 
            border_color="#444444",
            text_color="white"
        )
        self.entry_url.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # --- FOLDER SECTION ---
        self.folder_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=15)
        self.folder_frame.grid(row=3, column=0, padx=30, pady=20, sticky="ew")
        self.folder_frame.grid_columnconfigure(0, weight=1)

        self.label_dest = ctk.CTkLabel(self.folder_frame, text="DOSSIER DE DESTINATION", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_gray)
        self.label_dest.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.entry_dest = ctk.CTkEntry(self.folder_frame, height=40, fg_color="#333333", border_color="#444444")
        self.entry_dest.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")
        self.entry_dest.insert(0, os.path.join(os.getcwd(), "downloads"))

        self.btn_browse = ctk.CTkButton(
            self.folder_frame, 
            text="PARCOURIR", 
            width=100, 
            height=40,
            fg_color="#444444",
            hover_color="#555555",
            command=self.browse_folder
        )
        self.btn_browse.grid(row=1, column=1, padx=(0, 20), pady=(0, 20))

        # --- ACTION SECTION ---
        self.btn_download = ctk.CTkButton(
            self, 
            text="TÉLÉCHARGER MAINTENANT", 
            command=self.start_download_thread, 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.yellow_artlist,
            text_color="black",
            hover_color="#E6C200"
        )
        self.btn_download.grid(row=4, column=0, padx=30, pady=10, sticky="ew")

        # --- PROGRESS & STATUS ---
        self.progress_bar = ctk.CTkProgressBar(self, height=4, fg_color="#333333", progress_color=self.yellow_artlist)
        self.progress_bar.grid(row=5, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="Prêt pour l'extraction", font=ctk.CTkFont(size=12), text_color=self.text_gray)
        self.status_label.grid(row=6, column=0, padx=30, pady=(5, 10))

        # --- LOG BOX ---
        self.log_box = ctk.CTkTextbox(self, height=80, fg_color="#121212", border_color="#333333", border_width=1, text_color="#00FF00", font=ctk.CTkFont(family="Courier", size=11))
        self.log_box.grid(row=7, column=0, padx=30, pady=(0, 30), sticky="ew")
        self.log_box.configure(state="disabled")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_dest.delete(0, "end")
            self.entry_dest.insert(0, folder)

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_status(self, text, color="#AAAAAA"):
        self.status_label.configure(text=text, text_color=color)

    def start_download_thread(self):
        url = self.entry_url.get().strip()
        dest = self.entry_dest.get().strip()
        
        if not url:
            self.update_status("ERREUR : URL MANQUANTE", "#FF4444")
            return

        self.btn_download.configure(state="disabled", text="TRAITEMENT EN COURS...")
        self.update_status("Analyse d'Artlist...", self.yellow_artlist)
        self.progress_bar.set(0.2)
        self.log(f"Analyse : {url}")
        
        thread = threading.Thread(target=self.run_download, args=(url, dest), daemon=True)
        thread.start()

    def run_download(self, url, output_dir):
        try:
            output_dir = clean_path(output_dir)
            if not output_dir:
                output_dir = os.path.join(os.getcwd(), "downloads")

            self.progress_bar.set(0.4)
            response = requests.get(url, impersonate="chrome110", timeout=15, allow_redirects=True)
            response.raise_for_status()
            html_content = response.text
            final_url = response.url

            info = extract_media_info(html_content)
            audio_url = info["audio_url"]
            video_url = info["video_url"]
            title = info["title"]
            
            self.progress_bar.set(0.6)
            self.log(f"Fichier détecté : {title}")
            
            success = False
            headers_fallback = {"Referer": "https://artlist.io/", "Origin": "https://artlist.io"}
            
            if audio_url or video_url:
                is_video_context = "video" in final_url.lower() or "stock-footage" in final_url.lower()
                
                if video_url and is_video_context:
                    if ".m3u8" in video_url:
                        success = fallback_yt_dlp(video_url, output_dir, headers=headers_fallback)
                    else:
                        success = download_file(video_url, output_dir, f"{title}.mp4", referer=final_url)
                elif audio_url:
                    ext = "aac" if "aac" in audio_url or "Y29u" in audio_url else "mp3"
                    success = download_file(audio_url, output_dir, f"{title}.{ext}", referer=final_url)
                elif video_url:
                    if ".m3u8" in video_url:
                        success = fallback_yt_dlp(video_url, output_dir, headers=headers_fallback)
                    else:
                        success = download_file(video_url, output_dir, f"{title}.mp4", referer=final_url)
            
            if not success:
                self.log("Scraping direct échoué. Passage en mode secours...")
                success = fallback_yt_dlp(final_url, output_dir, headers=headers_fallback)

            if success:
                self.progress_bar.set(1.0)
                self.update_status("TERMINÉ AVEC SUCCÈS", "#00FF00")
                self.log(f"Terminé : {title}")
            else:
                self.progress_bar.set(0)
                self.update_status("ÉCHEC DU TÉLÉCHARGEMENT", "#FF4444")
                self.log("Erreur : Impossible de récupérer le fichier.")

        except Exception as e:
            self.log(f"Erreur système : {str(e)}")
            self.update_status("ERREUR SYSTÈME", "#FF4444")
            self.progress_bar.set(0)
        
        finally:
            self.btn_download.configure(state="normal", text="TÉLÉCHARGER MAINTENANT")

if __name__ == "__main__":
    app = ArtlistApp()
    app.mainloop()
