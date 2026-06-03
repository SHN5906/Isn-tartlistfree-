import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import sys
import time
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

        self.title("Artlist Downloader")
        self.geometry("650x550")
        
        ctk.set_appearance_mode("Dark")
        self.yellow_artlist = "#FFD700"
        self.bg_dark = "#1A1A1A"
        self.text_gray = "#AAAAAA"

        self.configure(fg_color=self.bg_dark)
        self.grid_columnconfigure(0, weight=1)
        
        # --- UI ELEMENTS (Identiques à la version précédente mais avec de meilleurs retours) ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="ew")
        
        self.label_title = ctk.CTkLabel(self.header_frame, text="ARTLIST", font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"), text_color=self.yellow_artlist)
        self.label_title.pack(side="left")
        
        self.label_subtitle = ctk.CTkLabel(self.header_frame, text=" DOWNLOADER", font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"), text_color="white")
        self.label_subtitle.pack(side="left")

        self.label_disclaimer = ctk.CTkLabel(self, text="Usage personnel & éducatif uniquement", font=ctk.CTkFont(size=11, slant="italic"), text_color=self.text_gray)
        self.label_disclaimer.grid(row=1, column=0, padx=30, pady=(0, 20), sticky="w")

        self.input_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=15)
        self.input_frame.grid(row=2, column=0, padx=30, pady=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.label_url = ctk.CTkLabel(self.input_frame, text="LIEN DE LA MUSIQUE OU VIDÉO", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_gray)
        self.label_url.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.entry_url = ctk.CTkEntry(self.input_frame, placeholder_text="https://artlist.io/song/...", height=45, fg_color="#333333", border_color="#444444", text_color="white")
        self.entry_url.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.folder_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=15)
        self.folder_frame.grid(row=3, column=0, padx=30, pady=20, sticky="ew")
        self.folder_frame.grid_columnconfigure(0, weight=1)

        self.label_dest = ctk.CTkLabel(self.folder_frame, text="DOSSIER DE DESTINATION", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_gray)
        self.label_dest.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.entry_dest = ctk.CTkEntry(self.folder_frame, height=40, fg_color="#333333", border_color="#444444")
        self.entry_dest.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")
        self.entry_dest.insert(0, os.path.join(os.getcwd(), "downloads"))

        self.btn_browse = ctk.CTkButton(self.folder_frame, text="PARCOURIR", width=100, height=40, fg_color="#444444", hover_color="#555555", command=self.browse_folder)
        self.btn_browse.grid(row=1, column=1, padx=(0, 20), pady=(0, 20))

        self.btn_download = ctk.CTkButton(self, text="TÉLÉCHARGER MAINTENANT", command=self.start_download_thread, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color=self.yellow_artlist, text_color="black", hover_color="#E6C200")
        self.btn_download.grid(row=4, column=0, padx=30, pady=10, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self, height=4, fg_color="#333333", progress_color=self.yellow_artlist)
        self.progress_bar.grid(row=5, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="Prêt pour l'extraction", font=ctk.CTkFont(size=12), text_color=self.text_gray)
        self.status_label.grid(row=6, column=0, padx=30, pady=(5, 10))

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
        self.progress_bar.set(0.1)
        self.log(f"Analyse de {url}")
        thread = threading.Thread(target=self.run_download, args=(url, dest), daemon=True)
        thread.start()

    def run_download(self, url, output_dir):
        try:
            output_dir = clean_path(output_dir)
            if not output_dir: output_dir = os.path.join(os.getcwd(), "downloads")

            # Stratégie de contournement Cloudflare
            html_content = ""
            final_url = url
            impersonates = ["chrome110", "chrome120", "safari15_5"]
            
            for imp in impersonates:
                self.log(f"Tentative de connexion ({imp})...")
                try:
                    response = requests.get(url, impersonate=imp, timeout=20, allow_redirects=True)
                    if response.status_code == 200 and "Just a moment..." not in response.text:
                        html_content = response.text
                        final_url = response.url
                        break
                    else:
                        self.log(f"[!] Protection détectée avec {imp}. Réessai...")
                        time.sleep(2)
                except Exception as e:
                    self.log(f"[!] Erreur avec {imp}: {str(e)[:50]}")
            
            if not html_content:
                self.log("[!] Échec du contournement direct. Passage au mode intensif...")
                self.update_status("Mode Intensif (yt-dlp)...", self.yellow_artlist)
                success = fallback_yt_dlp(url, output_dir)
            else:
                self.progress_bar.set(0.5)
                info = extract_media_info(html_content)
                audio_url = info["audio_url"]
                video_url = info["video_url"]
                title = info["title"]
                
                if not audio_url and not video_url:
                    self.log("[!] Aucun média trouvé dans le code. Tentative de repli...")
                    success = fallback_yt_dlp(final_url, output_dir)
                else:
                    self.log(f"Extraction : {title}")
                    success = False
                    headers = {"Referer": "https://artlist.io/", "Origin": "https://artlist.io"}
                    
                    if audio_url:
                        ext = "aac" if "aac" in audio_url or "Y29u" in audio_url else "mp3"
                        success = download_file(audio_url, output_dir, f"{title}.{ext}", referer=final_url)
                    elif video_url:
                        if ".m3u8" in video_url:
                            success = fallback_yt_dlp(video_url, output_dir, headers=headers)
                        else:
                            success = download_file(video_url, output_dir, f"{title}.mp4", referer=final_url)

            if success:
                self.progress_bar.set(1.0)
                self.update_status("TÉLÉCHARGÉ AVEC SUCCÈS", "#00FF00")
                self.log("Opération terminée.")
            else:
                self.progress_bar.set(0)
                self.update_status("ÉCHEC (RÉESSAYEZ DANS 1 MIN)", "#FF4444")
                self.log("Le site a bloqué la requête. Attendez un peu.")

        except Exception as e:
            self.log(f"Erreur: {str(e)}")
            self.update_status("ERREUR SYSTÈME", "#FF4444")
        finally:
            self.btn_download.configure(state="normal", text="TÉLÉCHARGER MAINTENANT")

if __name__ == "__main__":
    app = ArtlistApp()
    app.mainloop()
