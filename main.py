import os
import tkinter as tk
from tkinter import filedialog, messagebox, Button, Label, Entry, StringVar
import pygame
import requests
import io

class SubtitleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtitle Formatter")
        self.filename = ""
        self.output_dir = ""
        self.music_playing = False
        
        # Correctly initialize names_count before using it
        self.names_count = tk.StringVar(value="Actors: 0")  # Moved up before usage

        # Initialize Pygame for playing music
        pygame.mixer.init()

        # GUI Layout
        Label(root, text="Subtitle Formatter", font=('Helvetica', 16, 'bold')).pack(pady=20)
        Button(root, text="Upload .ass File", command=self.upload_file).pack(fill='x', padx=50, pady=5)
        Button(root, text="Choose Output Folder", command=self.choose_output_folder).pack(fill='x', padx=50, pady=5)
        
        # Folder name entry
        Label(root, text="Enter folder name for subtitles:", font=('Helvetica', 10)).pack(pady=2)
        self.folder_entry = Entry(root, font=('Helvetica', 10))
        self.folder_entry.pack(fill='x', padx=50, pady=5)
        self.folder_entry.insert(0, "Subtitles")  # Default folder name
        
        Button(root, text="Start", command=self.start_conversion).pack(fill='x', padx=50, pady=5)
        Button(root, text="Open Output Folder", command=self.open_output_folder).pack(fill='x', padx=50, pady=5)
        
        # Music control button
        self.music_button = Button(root, text="♫", font=("Arial", 14), width=2, command=self.toggle_music)
        self.music_button.pack(pady=10)

        # Display count of unique names
        Label(root, textvariable=self.names_count, font=('Helvetica', 10)).pack(pady=10)

        # Download and play music at startup
        self.download_and_play_music("https://cdn.pixabay.com/audio/2022/03/09/audio_ea238ed7c4.mp3")

    def download_and_play_music(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            audio_data = io.BytesIO(response.content)
            self.music = pygame.mixer.Sound(file=audio_data)
            self.music.play(loops=-1)
            self.music_playing = True
        else:
            messagebox.showerror("Error", "Failed to download music")

    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.pause()
            self.music_playing = False
        else:
            pygame.mixer.unpause()
            self.music_playing = True

    def upload_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("ASS files", "*.ass")])
        if not self.filename:
            messagebox.showinfo("Info", "No file selected.")

    def choose_output_folder(self):
        selected_directory = filedialog.askdirectory(mustexist=True, title="Select Output Directory")
        if selected_directory:
            self.output_dir = selected_directory
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, self.output_dir)
        else:
            messagebox.showinfo("Info", "No output directory selected.")

    def start_conversion(self):
        if not self.filename or not self.output_dir:
            messagebox.showerror("Error", "Please select a file and an output directory first.")
        else:
            folder_name = self.folder_entry.get()
            full_output_path = os.path.join(self.output_dir, folder_name)
            os.makedirs(full_output_path, exist_ok=True)
            names_count = parse_ass_file(self.filename, full_output_path)
            self.names_count.set(f"Actors: {names_count}")
            messagebox.showinfo("Success", "Conversion completed successfully!")

    def open_output_folder(self):
        full_output_path = os.path.join(self.output_dir, self.folder_entry.get())
        if os.path.exists(full_output_path):
            os.startfile(full_output_path)
        else:
            messagebox.showinfo("Info", "Output directory not found.")

def parse_ass_file(filename, output_dir):
    import os
    
    dialogues = {}  # Dictionary to store dialogues by character name

    # Read the .ass file and parse dialogues
    with open(filename, 'r', encoding='utf-8') as file:
        events_started = False
        for line in file:
            line = line.strip()
            if "[Events]" in line:
                events_started = True
            elif events_started and line.startswith("Format:"):
                format_parts = line.split(':')[1].split(',')
                indices = {part.strip(): idx for idx, part in enumerate(format_parts)}
            elif events_started and line.startswith("Dialogue"):
                parts = line.split(',', maxsplit=len(indices)-1)
                if 'Name' in indices and 'Text' in indices:
                    name = parts[indices['Name']].strip()
                    start = parts[indices['Start']].strip()
                    end = parts[indices['End']].strip()
                    text = parts[indices['Text']].replace('\\N', '\n').strip()  # Replacing '\N' with newline
                    
                    if name not in dialogues:
                        dialogues[name] = []

                    # Create .srt format entry
                    index = len(dialogues[name]) + 1
                    srt_entry = f"{index}\n{start} --> {end}\n{text}\n\n"
                    dialogues[name].append(srt_entry)

    # Write each character's dialogues to their respective .srt files
    for name, entries in dialogues.items():
        srt_filename = os.path.join(output_dir, f"{name}.srt")
        with open(srt_filename, 'w', encoding='utf-8') as out_file:
            out_file.writelines(entries)

    return len(dialogues)  # Return the number of unique names processed

def main():
    root = tk.Tk()
    app = SubtitleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
