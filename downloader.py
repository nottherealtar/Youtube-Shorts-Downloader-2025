import yt_dlp
import os
from pathlib import Path
import threading
import re

class DownloadStatus:
    QUEUED = "Queued"
    DOWNLOADING = "Downloading"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

class VideoDownloader:
    def __init__(self, config, progress_callback=None):
        self.config = config
        self.progress_callback = progress_callback
        self.cancel_flag = threading.Event()
        
    def get_ydl_opts(self, output_path):
        quality = self.config.get('quality')
        
        format_string = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        if quality == '1080p':
            format_string = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]'
        elif quality == '720p':
            format_string = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]'
        elif quality == '480p':
            format_string = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]'
        elif quality == 'audio':
            format_string = 'bestaudio[ext=m4a]/bestaudio'
        
        opts = {
            'format': format_string,
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'ignoreerrors': True,
            'nocheckcertificate': True,
        }
        
        if self.config.get('embed_thumbnail'):
            opts['writethumbnail'] = True
            opts['postprocessors'] = [{
                'key': 'EmbedThumbnail',
            }, {
                'key': 'FFmpegMetadata',
            }]
        
        return opts
    
    def _progress_hook(self, d):
        if self.cancel_flag.is_set():
            raise yt_dlp.utils.DownloadError("Download cancelled by user")
        
        if self.progress_callback:
            self.progress_callback(d)
    
    def normalize_channel_url(self, url):
        """Convert any channel URL to shorts URL"""
        # Extract channel handle or ID
        if '/@' in url:
            # Handle format: youtube.com/@username
            match = re.search(r'/@([^/\?]+)', url)
            if match:
                username = match.group(1)
                return f'https://www.youtube.com/@{username}/shorts'
        elif '/channel/' in url:
            # Handle format: youtube.com/channel/UC...
            match = re.search(r'/channel/([^/\?]+)', url)
            if match:
                channel_id = match.group(1)
                return f'https://www.youtube.com/channel/{channel_id}/shorts'
        elif '/c/' in url:
            # Handle format: youtube.com/c/channelname
            match = re.search(r'/c/([^/\?]+)', url)
            if match:
                channel_name = match.group(1)
                return f'https://www.youtube.com/c/{channel_name}/shorts'
        
        # If already a shorts URL or playlist, return as is
        if '/shorts' in url or '/playlist' in url or 'watch?v=' in url:
            return url
        
        # Default: assume it's a channel and append /shorts
        return url.rstrip('/') + '/shorts'
    
    def extract_shorts_info(self, url):
        """Extract shorts info with full metadata"""
        # Normalize URL to shorts tab
        shorts_url = self.normalize_channel_url(url)
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'ignoreerrors': True,
            'nocheckcertificate': True,
            'playlistend': 100,  # Limit to 100 shorts
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(shorts_url, download=False)
                return info
        except Exception as e:
            raise Exception(f"Failed to extract shorts info: {str(e)}")
    
    def get_videos_from_url(self, url):
        """Get list of videos with full metadata from URL"""
        
        # Check if it's a single video
        if 'watch?v=' in url or '/shorts/' in url:
            return self._get_single_video_info(url)
        
        # Otherwise treat as channel/playlist
        info = self.extract_shorts_info(url)
        
        if not info:
            raise Exception("No information found for this URL")
        
        videos = []
        
        # Handle playlists/channels
        if 'entries' in info:
            for entry in info['entries']:
                if entry and entry.get('id'):
                    # Get full info for each video to get metadata
                    try:
                        video_info = self._get_video_metadata(entry.get('id'))
                        if video_info:
                            videos.append(video_info)
                    except:
                        # Fallback to basic info if full metadata fails
                        video_url = entry.get('url')
                        if not video_url:
                            video_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                        
                        videos.append({
                            'id': entry.get('id'),
                            'title': entry.get('title', 'Unknown Title'),
                            'url': video_url,
                            'duration': entry.get('duration', 0),
                            'view_count': entry.get('view_count', 0),
                            'upload_date': entry.get('upload_date', ''),
                            'tags': entry.get('tags', []),
                            'thumbnail': entry.get('thumbnail', '')
                        })
        else:
            # Single video
            videos.append(self._parse_video_info(info, url))
        
        return videos
    
    def _get_single_video_info(self, url):
        """Get info for a single video"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'nocheckcertificate': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return [self._parse_video_info(info, url)]
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
    
    def _get_video_metadata(self, video_id):
        """Get full metadata for a video by ID"""
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'nocheckcertificate': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._parse_video_info(info, url)
        except:
            return None
    
    def _parse_video_info(self, info, url):
        """Parse video info into standardized format"""
        # Format duration
        duration = info.get('duration', 0)
        duration_str = self._format_duration(duration)
        
        # Format upload date
        upload_date = info.get('upload_date', '')
        if upload_date:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(upload_date, '%Y%m%d')
                upload_date = date_obj.strftime('%Y-%m-%d')
            except:
                pass
        
        # Format view count
        view_count = info.get('view_count', 0)
        view_count_str = self._format_views(view_count)
        
        # Get tags/hashtags
        tags = info.get('tags', [])
        if not tags:
            # Try to extract from description
            description = info.get('description', '')
            tags = re.findall(r'#\w+', description)
        
        return {
            'id': info.get('id'),
            'title': info.get('title', 'Unknown Title'),
            'url': url,
            'duration': duration,
            'duration_str': duration_str,
            'view_count': view_count,
            'view_count_str': view_count_str,
            'upload_date': upload_date,
            'tags': tags[:5] if tags else [],  # Limit to 5 tags
            'thumbnail': info.get('thumbnail', '')
        }
    
    def _format_duration(self, seconds):
        """Format duration in seconds to MM:SS or HH:MM:SS"""
        if not seconds:
            return "0:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    
    def _format_views(self, views):
        """Format view count to readable string"""
        if not views:
            return "0 views"
        
        if views >= 1_000_000:
            return f"{views / 1_000_000:.1f}M views"
        elif views >= 1_000:
            return f"{views / 1_000:.1f}K views"
        return f"{views} views"
    
    def download_video(self, url, output_path):
        """Download a single video"""
        self.cancel_flag.clear()
        
        try:
            ydl_opts = self.get_ydl_opts(output_path)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    return {'status': 'error', 'error': 'No video information available'}
                
                return {
                    'status': 'success',
                    'title': info.get('title', 'Unknown'),
                    'id': info.get('id', ''),
                    'filepath': ydl.prepare_filename(info)
                }
        except yt_dlp.utils.DownloadError as e:
            if "cancelled by user" in str(e):
                return {'status': 'cancelled', 'error': 'Download cancelled'}
            return {'status': 'error', 'error': str(e)}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def cancel(self):
        """Cancel current download"""
        self.cancel_flag.set()
