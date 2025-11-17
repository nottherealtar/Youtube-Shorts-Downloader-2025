import threading
import queue
from datetime import datetime
from downloader import VideoDownloader, DownloadStatus

class DownloadTask:
    def __init__(self, video_info, output_path):
        self.video_info = video_info
        self.output_path = output_path
        self.status = DownloadStatus.QUEUED
        self.progress = 0
        self.speed = ""
        self.eta = ""
        self.error = None
        self.started_at = None
        self.completed_at = None
        
class DownloadManager:
    def __init__(self, config):
        self.config = config
        self.tasks = []
        self.queue = queue.Queue()
        self.active_downloads = {}
        self.lock = threading.Lock()
        self.running = False
        self.workers = []
        self.callbacks = {
            'task_update': None,
            'queue_update': None,
            'download_complete': None
        }
        
    def set_callback(self, event, callback):
        self.callbacks[event] = callback
    
    def add_videos(self, videos, output_path):
        """Add multiple videos to download queue"""
        with self.lock:
            for video in videos:
                task = DownloadTask(video, output_path)
                self.tasks.append(task)
                self.queue.put(task)
        
        self._notify_callback('queue_update')
        
        if not self.running:
            self.start()
    
    def start(self):
        """Start download workers"""
        if self.running:
            return
        
        self.running = True
        max_workers = self.config.get('max_concurrent')
        
        for i in range(max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop all downloads"""
        self.running = False
        
        with self.lock:
            for downloader in self.active_downloads.values():
                downloader.cancel()
        
        for worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=2)
        
        self.workers.clear()
    
    def _worker(self):
        """Worker thread that processes download queue"""
        while self.running:
            try:
                task = self.queue.get(timeout=1)
            except queue.Empty:
                continue
            
            if not self.running:
                break
            
            self._download_task(task)
            self.queue.task_done()
    
    def _download_task(self, task):
        """Download a single task"""
        task.status = DownloadStatus.DOWNLOADING
        task.started_at = datetime.now()
        self._notify_callback('task_update', task)
        
        def progress_callback(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    task.progress = int((downloaded / total) * 100)
                
                task.speed = d.get('_speed_str', '')
                task.eta = d.get('_eta_str', '')
                self._notify_callback('task_update', task)
        
        downloader = VideoDownloader(
            self.config,
            progress_callback=progress_callback
        )
        
        thread_id = threading.get_ident()
        with self.lock:
            self.active_downloads[thread_id] = downloader
        
        try:
            result = downloader.download_video(
                task.video_info['url'],
                task.output_path
            )
            
            if result['status'] == 'success':
                task.status = DownloadStatus.COMPLETED
                task.progress = 100
            elif result['status'] == 'cancelled':
                task.status = DownloadStatus.CANCELLED
            else:
                task.status = DownloadStatus.FAILED
                task.error = result.get('error', 'Unknown error')
            
        except Exception as e:
            task.status = DownloadStatus.FAILED
            task.error = str(e)
        
        finally:
            task.completed_at = datetime.now()
            with self.lock:
                self.active_downloads.pop(thread_id, None)
            
            self._notify_callback('task_update', task)
            self._notify_callback('download_complete', task)
    
    def cancel_task(self, task):
        """Cancel a specific task"""
        if task.status == DownloadStatus.QUEUED:
            task.status = DownloadStatus.CANCELLED
            self._notify_callback('task_update', task)
        elif task.status == DownloadStatus.DOWNLOADING:
            with self.lock:
                for downloader in self.active_downloads.values():
                    downloader.cancel()
    
    def get_stats(self):
        """Get download statistics"""
        with self.lock:
            total = len(self.tasks)
            completed = sum(1 for t in self.tasks if t.status == DownloadStatus.COMPLETED)
            failed = sum(1 for t in self.tasks if t.status == DownloadStatus.FAILED)
            downloading = sum(1 for t in self.tasks if t.status == DownloadStatus.DOWNLOADING)
            queued = sum(1 for t in self.tasks if t.status == DownloadStatus.QUEUED)
            
            return {
                'total': total,
                'completed': completed,
                'failed': failed,
                'downloading': downloading,
                'queued': queued
            }
    
    def clear_completed(self):
        """Remove completed tasks from list"""
        with self.lock:
            self.tasks = [t for t in self.tasks if t.status != DownloadStatus.COMPLETED]
        self._notify_callback('queue_update')
    
    def _notify_callback(self, event, *args):
        """Notify registered callback"""
        callback = self.callbacks.get(event)
        if callback:
            try:
                callback(*args)
            except Exception as e:
                print(f"Callback error: {e}")
