import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from config import Config
from downloader import VideoDownloader, DownloadStatus
from download_manager import DownloadManager
from pathlib import Path
import traceback

class ModernYTDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        self.config = Config()
        self.download_manager = DownloadManager(self.config)
        
        self.download_manager.set_callback('task_update', self.on_task_update)
        self.download_manager.set_callback('queue_update', self.on_queue_update)
        self.download_manager.set_callback('download_complete', self.on_download_complete)
        
        self.setup_styles()
        self.create_widgets()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.videos_to_download = []
        self.tree_items = {}
    
    def setup_styles(self):
        """Clean, readable color scheme - prioritizing functionality"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Professional color scheme - high contrast for readability
        bg_main = "#f5f5f5"  # Light gray background
        bg_widget = "#ffffff"  # White for input areas
        fg_main = "#2c3e50"  # Dark blue-gray text
        accent = "#3498db"  # Professional blue
        accent_hover = "#2980b9"  # Darker blue
        success = "#27ae60"  # Green
        error = "#e74c3c"  # Red
        border = "#bdc3c7"  # Light border
        
        # Configure base styles
        style.configure(".", background=bg_main, foreground=fg_main, font=("Segoe UI", 9))
        style.configure("TFrame", background=bg_main)
        style.configure("TLabel", background=bg_main, foreground=fg_main, font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=accent)
        style.configure("Section.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#7f8c8d")
        
        # Button styles
        style.configure("TButton", 
                       background=accent, 
                       foreground="white",
                       borderwidth=0,
                       focuscolor='none',
                       font=("Segoe UI", 9, "bold"),
                       padding=(15, 8))
        style.map("TButton", 
                 background=[("active", accent_hover), ("disabled", "#95a5a6")])
        
        style.configure("Success.TButton", background=success)
        style.map("Success.TButton", background=[("active", "#229954")])
        
        # Entry and Combobox
        style.configure("TEntry", 
                       fieldbackground=bg_widget,
                       foreground=fg_main,
                       borderwidth=1,
                       relief="solid")
        style.configure("TCombobox",
                       fieldbackground=bg_widget,
                       background=bg_widget,
                       foreground=fg_main,
                       borderwidth=1)
        
        # LabelFrame
        style.configure("TLabelframe", 
                       background=bg_main,
                       borderwidth=2,
                       relief="groove")
        style.configure("TLabelframe.Label",
                       background=bg_main,
                       foreground=fg_main,
                       font=("Segoe UI", 10, "bold"))
        
        # Treeview
        style.configure("Treeview",
                       background=bg_widget,
                       foreground=fg_main,
                       fieldbackground=bg_widget,
                       borderwidth=1,
                       font=("Segoe UI", 9))
        style.configure("Treeview.Heading",
                       background=accent,
                       foreground="white",
                       borderwidth=0,
                       font=("Segoe UI", 9, "bold"))
        style.map("Treeview.Heading",
                 background=[("active", accent_hover)])
        
        self.root.configure(bg=bg_main)
    
    def create_widgets(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ===== HEADER =====
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(header_frame, text="YouTube Downloader Pro", style="Header.TLabel")
        title.pack(side=tk.LEFT)
        
        # ===== INPUT SECTION =====
        input_frame = ttk.LabelFrame(main_container, text=" Add Download ", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # URL Input
        url_container = ttk.Frame(input_frame)
        url_container.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(url_container, text="YouTube URL:", style="Section.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        url_input_frame = ttk.Frame(url_container)
        url_input_frame.pack(fill=tk.X)
        
        self.url_entry = ttk.Entry(url_input_frame, font=("Segoe UI", 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=5)
        self.url_entry.bind('<Return>', lambda e: self.fetch_info())
        
        self.fetch_btn = ttk.Button(url_input_frame, text="Fetch Info", command=self.fetch_info, width=12)
        self.fetch_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Settings Row
        settings_frame = ttk.Frame(input_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quality Selection
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(quality_frame, text="Quality:").pack(anchor=tk.W, pady=(0, 3))
        self.quality_var = tk.StringVar(value=self.config.get('quality'))
        quality_combo = ttk.Combobox(quality_frame, 
                                     textvariable=self.quality_var,
                                     values=['best', '1080p', '720p', '480p', 'audio'],
                                     state='readonly',
                                     width=15,
                                     font=("Segoe UI", 9))
        quality_combo.pack(fill=tk.X, ipady=3)
        quality_combo.bind('<<ComboboxSelected>>', lambda e: self.config.set('quality', self.quality_var.get()))
        
        # Concurrent Downloads
        concurrent_frame = ttk.Frame(settings_frame)
        concurrent_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(concurrent_frame, text="Concurrent:").pack(anchor=tk.W, pady=(0, 3))
        self.concurrent_var = tk.StringVar(value=str(self.config.get('max_concurrent')))
        concurrent_combo = ttk.Combobox(concurrent_frame,
                                       textvariable=self.concurrent_var,
                                       values=['1', '2', '3', '4', '5'],
                                       state='readonly',
                                       width=15,
                                       font=("Segoe UI", 9))
        concurrent_combo.pack(fill=tk.X, ipady=3)
        concurrent_combo.bind('<<ComboboxSelected>>', 
                             lambda e: self.config.set('max_concurrent', int(self.concurrent_var.get())))
        
        # Save Path
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, text="Save to:").pack(anchor=tk.W, pady=(0, 3))
        
        path_input_frame = ttk.Frame(path_frame)
        path_input_frame.pack(fill=tk.X)
        
        self.path_var = tk.StringVar(value=self.config.get('download_path'))
        path_entry = ttk.Entry(path_input_frame, textvariable=self.path_var, state='readonly', font=("Segoe UI", 9))
        path_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=5)
        
        browse_btn = ttk.Button(path_input_frame, text="Browse", command=self.browse_folder, width=12)
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Action Buttons
        action_frame = ttk.Frame(input_frame)
        action_frame.pack(fill=tk.X)
        
        self.download_btn = ttk.Button(action_frame, 
                                       text="Download All", 
                                       command=self.download_all,
                                       state='disabled',
                                       style="Success.TButton")
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_selected_btn = ttk.Button(action_frame,
                                               text="Download Selected",
                                               command=self.download_selected,
                                               state='disabled',
                                               style="Success.TButton")
        self.download_selected_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(action_frame, text="Clear Completed", command=self.clear_completed)
        self.clear_btn.pack(side=tk.LEFT)
        
        # ===== STATUS BAR =====
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready to download", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        self.stats_label = ttk.Label(status_frame, text="", style="Status.TLabel")
        self.stats_label.pack(side=tk.RIGHT)
        
        # ===== DOWNLOAD QUEUE =====
        queue_frame = ttk.LabelFrame(main_container, text=" Download Queue ", padding="10")
        queue_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        tree_frame = ttk.Frame(queue_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('title', 'duration', 'views', 'date', 'tags', 'status', 'progress')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=15)
        
        self.tree.heading('#0', text='#')
        self.tree.heading('title', text='Title')
        self.tree.heading('duration', text='Duration')
        self.tree.heading('views', text='Views')
        self.tree.heading('date', text='Upload Date')
        self.tree.heading('tags', text='Tags')
        self.tree.heading('status', text='Status')
        self.tree.heading('progress', text='Progress')
        
        self.tree.column('#0', width=40, stretch=False, anchor=tk.CENTER)
        self.tree.column('title', width=300)
        self.tree.column('duration', width=80, stretch=False, anchor=tk.CENTER)
        self.tree.column('views', width=100, stretch=False)
        self.tree.column('date', width=100, stretch=False, anchor=tk.CENTER)
        self.tree.column('tags', width=150)
        self.tree.column('status', width=100, stretch=False)
        self.tree.column('progress', width=80, stretch=False, anchor=tk.CENTER)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.path_var.get())
        if folder:
            self.path_var.set(folder)
            self.config.set('download_path', folder)
    
    def fetch_info(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please enter a YouTube URL")
            return
        
        self.fetch_btn.config(state='disabled', text="Fetching...")
        self.status_label.config(text="Fetching video information...")
        self.url_entry.config(state='disabled')
        
        def fetch_thread():
            try:
                downloader = VideoDownloader(self.config)
                videos = downloader.get_videos_from_url(url)
                
                if not videos:
                    self.root.after(0, lambda: messagebox.showwarning("No Videos", "No videos found at this URL"))
                else:
                    self.root.after(0, lambda: self.display_videos(videos))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch info:\n\n{error_msg}"))
                self.root.after(0, lambda: self.status_label.config(text="Error fetching video info"))
            finally:
                self.root.after(0, lambda: self.fetch_btn.config(state='normal', text="Fetch Info"))
                self.root.after(0, lambda: self.url_entry.config(state='normal'))
        
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def display_videos(self, videos):
        self.videos_to_download = videos
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree_items.clear()
        
        # Add videos to tree with full metadata
        for idx, video in enumerate(videos, 1):
            # Format tags
            tags_str = ' '.join(video.get('tags', [])[:3])  # Show first 3 tags
            if len(video.get('tags', [])) > 3:
                tags_str += '...'
            
            item_id = self.tree.insert('', 'end', 
                                       text=str(idx),
                                       values=(
                                           video['title'],
                                           video.get('duration_str', '0:00'),
                                           video.get('view_count_str', '0 views'),
                                           video.get('upload_date', 'Unknown'),
                                           tags_str,
                                           'Ready',
                                           '0%'
                                       ))
            self.tree_items[video['id']] = item_id
        
        self.download_btn.config(state='normal')
        self.download_selected_btn.config(state='normal')
        self.status_label.config(text=f"Found {len(videos)} video(s) - Ready to download")
        self.url_entry.delete(0, tk.END)
    
    def download_all(self):
        if not self.videos_to_download:
            return
        
        output_path = self.path_var.get()
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        self.download_btn.config(state='disabled')
        self.download_selected_btn.config(state='disabled')
        self.status_label.config(text=f"Starting download of {len(self.videos_to_download)} video(s)...")
        
        self.download_manager.add_videos(self.videos_to_download, output_path)
        self.videos_to_download = []
    
    def download_selected(self):
        """Download only selected videos from the tree"""
        selected_items = self.tree.selection()
        
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select videos to download")
            return
        
        if not self.videos_to_download:
            return
        
        # Get selected video IDs
        selected_videos = []
        for item_id in selected_items:
            values = self.tree.item(item_id, 'values')
            if values and values[5] == 'Ready':  # Only download if status is Ready
                # Find the video by title
                title = values[0]
                for video in self.videos_to_download:
                    if video['title'] == title:
                        selected_videos.append(video)
                        break
        
        if not selected_videos:
            messagebox.showinfo("No Videos", "No ready videos selected")
            return
        
        output_path = self.path_var.get()
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        self.download_btn.config(state='disabled')
        self.download_selected_btn.config(state='disabled')
        self.status_label.config(text=f"Starting download of {len(selected_videos)} selected video(s)...")
        
        self.download_manager.add_videos(selected_videos, output_path)
        
        # Remove downloaded videos from the list
        for video in selected_videos:
            if video in self.videos_to_download:
                self.videos_to_download.remove(video)
    
    def on_task_update(self, task):
        def update():
            video_id = task.video_info['id']
            item_id = self.tree_items.get(video_id)
            
            if item_id and self.tree.exists(item_id):
                progress_text = f"{task.progress}%"
                
                # Get existing values
                current_values = self.tree.item(item_id, 'values')
                
                # Update only status and progress, keep metadata
                self.tree.item(item_id, values=(
                    current_values[0],  # title
                    current_values[1],  # duration
                    current_values[2],  # views
                    current_values[3],  # date
                    current_values[4],  # tags
                    task.status,        # status
                    progress_text       # progress
                ))
            
            self.update_stats()
        
        self.root.after(0, update)
    
    def on_queue_update(self):
        self.root.after(0, self.update_stats)
    
    def on_download_complete(self, task):
        def notify():
            if task.status == DownloadStatus.FAILED:
                error_msg = task.error if task.error else "Unknown error"
                self.status_label.config(text=f"Failed: {task.video_info['title'][:50]}...")
        
        self.root.after(0, notify)
    
    def update_stats(self):
        stats = self.download_manager.get_stats()
        
        if stats['total'] == 0:
            self.stats_label.config(text="")
            return
        
        parts = []
        if stats['downloading'] > 0:
            parts.append(f"Downloading: {stats['downloading']}")
        if stats['queued'] > 0:
            parts.append(f"Queued: {stats['queued']}")
        if stats['completed'] > 0:
            parts.append(f"Completed: {stats['completed']}")
        if stats['failed'] > 0:
            parts.append(f"Failed: {stats['failed']}")
        
        text = f"Total: {stats['total']} | " + " | ".join(parts)
        self.stats_label.config(text=text)
        
        if stats['downloading'] == 0 and stats['queued'] == 0 and stats['total'] > 0:
            self.status_label.config(text="All downloads completed")
            self.download_btn.config(state='normal')
    
    def clear_completed(self):
        self.download_manager.clear_completed()
        
        # Remove completed items from tree
        for item_id in list(self.tree.get_children()):
            if self.tree.exists(item_id):
                values = self.tree.item(item_id, 'values')
                if values and values[5] == DownloadStatus.COMPLETED:  # Status is now at index 5
                    self.tree.delete(item_id)
        
        self.update_stats()
    
    def on_closing(self):
        stats = self.download_manager.get_stats()
        if stats['downloading'] > 0 or stats['queued'] > 0:
            if not messagebox.askokcancel("Quit", "Downloads in progress. Stop all downloads and quit?"):
                return
        
        self.download_manager.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ModernYTDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
