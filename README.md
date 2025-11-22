# YouTube Downloader Pro

A modern, user-friendly desktop application for downloading YouTube videos, shorts, playlists, and channels with ease.

## ✨ Features

- **Multiple Download Types**
  - Download YouTube Shorts
  - Download all shorts from a channel

- **Quality Selection**
  - Choose from multiple quality options: Best, 1080p, 720p, 480p
  - Audio-only download option

- **User-Friendly Interface**
  - Clean, modern graphical interface
  - Real-time download progress tracking
  - View video metadata (duration, views, upload date, tags)
  - Select specific videos or download all at once

- **Advanced Features**
  - Concurrent downloads (up to 5 simultaneous downloads)
  - Persistent configuration (your settings are saved)
  - Custom download location
  - Thumbnail embedding support

## 🚀 Quick Start (Windows)

1. **Install Dependencies**
   - Double-click `install.bat`
   - Follow the prompts
   - The installer will automatically set up Python dependencies and FFmpeg

2. **Run the Application**
   - Double-click `run.bat`
   - The application window will open

That's it! You're ready to download videos.

## 📋 Requirements

- **Python 3.8 or higher** - The installer will check for this
- **FFmpeg** - Required for video processing (automatically installed by `install.bat`)

## 💡 How to Use

1. **Paste a YouTube URL**
   - Copy any YouTube video, playlist, channel, or shorts URL
   - Paste it into the "YouTube URL" field

2. **Fetch Video Information**
   - Click the "Fetch Info" button
   - The app will retrieve all available videos and display metadata

3. **Configure Your Download**
   - Select your preferred quality (Best, 1080p, 720p, 480p, or Audio only)
   - Choose how many videos to download at once (1-5 concurrent downloads)
   - Select where to save your downloads (default is your Downloads folder)

4. **Download**
   - Click "Download All" to download everything
   - Or select specific videos and click "Download Selected"
   - Watch real-time progress for each download

## 🛠️ Troubleshooting

### "Python is not recognized"
- Install Python from [python.org](https://www.python.org/downloads/)
- **Important:** Check "Add Python to PATH" during installation
- Restart your computer after installing

### "FFmpeg is not recognized"
- Run `install.bat` again and choose to install FFmpeg when prompted
- Or manually install: `winget install ffmpeg`
- Restart your terminal or computer after installation

### Downloads fail with format errors
- Make sure FFmpeg is properly installed
- Try restarting the application
- Check your internet connection

### Application won't start
- Run `install.bat` again to reinstall dependencies
- Make sure Python is properly installed
- Check that all dependencies were installed correctly

### Video metadata not showing
- Check your internet connection
- Verify the YouTube URL is correct
- Some private or restricted videos may not show metadata

## 📝 Notes

- The first download might take a moment as the app initializes
- Large playlists or channels may take some time to fetch all video information
- Download speeds depend on your internet connection and YouTube's servers

## 🔒 Privacy

- All downloads are processed locally on your computer
- No data is collected or sent to external servers
- Your download history and settings are stored only on your device

---

**Enjoy downloading your favorite YouTube content!** 🎥
