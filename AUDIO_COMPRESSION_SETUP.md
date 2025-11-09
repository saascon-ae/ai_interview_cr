# Audio Compression Setup

This application uses audio compression to reduce file sizes while maintaining good quality for speech recordings.

## Requirements

The audio compression feature requires **ffmpeg** to be installed on your system.

### Installing ffmpeg

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### Windows
Download from: https://ffmpeg.org/download.html
- Extract the zip file
- Add the `bin` folder to your system PATH

#### Verify Installation
```bash
ffmpeg -version
```

## How It Works

1. **Recording**: Audio is recorded in WebM format from the browser
2. **Compression**: The WebM file is automatically converted to MP3 with optimized settings:
   - **Bitrate**: 64kbps (optimal for speech)
   - **Sample Rate**: 22.05kHz (sufficient for speech)
   - **Channels**: Mono (speech doesn't need stereo)
   - **Quality**: High quality setting (q:a=2)

3. **Result**: 
   - Audio files are typically **70-80% smaller** than original WebM files
   - Quality remains excellent for speech recognition and playback
   - Original WebM files are automatically deleted after compression

## File Size Comparison

- **Original WebM**: ~500KB per minute
- **Compressed MP3**: ~120-150KB per minute
- **Savings**: ~70-80% reduction in storage

## Fallback Behavior

If ffmpeg is not installed or compression fails:
- The system will automatically fall back to the original WebM format
- No errors will be shown to users
- The application will continue to function normally

## Python Dependencies

The compression uses the `pydub` library, which is already included in `requirements.txt`:
```
pydub==0.25.1
```

Install dependencies:
```bash
pip install -r requirements.txt
```

