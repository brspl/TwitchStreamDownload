import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def check_dependencies() -> None:
    if shutil.which("ffmpeg") is None:
        sys.exit("ERROR: ffmpeg not found. Add ffmpeg's 'bin' folder to your PATH.")

    result = subprocess.run(
        [sys.executable, "-m", "streamlink", "--version"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.exit(f"ERROR: streamlink not installed. Run: \"{sys.executable}\" -m pip install streamlink")

def parse_channel(value: str) -> str:
    return value.split("?")[0].rstrip("/").split("/")[-1]

def record(channel: str, quality: str, ts_file: Path) -> bool:
    url = f"https://www.twitch.tv/{channel}"
    streamlink_cmd = [sys.executable, "-m", "streamlink", "--stdout", url, quality]
    ffmpeg_cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y",
        "-i", "-",
        "-c", "copy",
        "-f", "mpegts", str(ts_file),
    ]

    print(f"Recording: {url} (quality: {quality})")
    print(f"Temporary file: {ts_file}")
    print("Press Ctrl+C to stop recording.\n")

    streamlink = subprocess.Popen(streamlink_cmd, stdout=subprocess.PIPE)
    ffmpeg = subprocess.Popen(ffmpeg_cmd, stdin=streamlink.stdout)
    streamlink.stdout.close()

    try:
        ffmpeg.wait()
    except KeyboardInterrupt:
        print("\nStopping recording...")
        try:
            ffmpeg.wait(timeout=15)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            ffmpeg.terminate()
            ffmpeg.wait()
    finally:
        if streamlink.poll() is None:
            streamlink.terminate()
        streamlink.wait()

    return ts_file.exists() and ts_file.stat().st_size > 0

def remux_to_mp4(ts_file: Path, mp4_file: Path) -> bool:
    print(f"\nConverting to MP4: {mp4_file}")
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(ts_file),
        "-c", "copy",
        "-dn",
        "-bsf:a", "aac_adtstoasc",
        "-movflags", "+faststart",
        str(mp4_file),
    ]
    return subprocess.run(cmd).returncode == 0

def main() -> None:
    parser = argparse.ArgumentParser(description="Record live Twitch streams to MP4.")
    parser.add_argument("channel", help="channel name or URL, e.g. 'name' or https://www.twitch.tv/name")
    parser.add_argument("--quality", default="best",
                        help="best, worst, 1080p60, 720p60, 480p, audio_only... (default: best)")
    parser.add_argument("--output-dir", default="recordings",
                        help="directory for .ts recordings (default: ./recordings)")
    parser.add_argument("--mp4-dir", default=None,
                        help="separate directory for finished MP4 files (default: same as --output-dir)")
    parser.add_argument("--no-convert", action="store_true",
                        help="keep only the .ts file, skip MP4 conversion")
    parser.add_argument("--keep-ts", action="store_true",
                        help="don't delete the .ts file after a successful conversion")
    args = parser.parse_args()

    check_dependencies()

    channel = parse_channel(args.channel)
    ts_dir = Path(args.output_dir)
    mp4_dir = Path(args.mp4_dir) if args.mp4_dir else ts_dir
    ts_dir.mkdir(parents=True, exist_ok=True)
    mp4_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ts_file = ts_dir / f"{channel}_{timestamp}.ts"
    mp4_file = mp4_dir / f"{channel}_{timestamp}.mp4"

    if not record(channel, args.quality, ts_file):
        ts_file.unlink(missing_ok=True)
        sys.exit("\nNothing was recorded. The channel may be offline or the selected quality is unavailable.")

    size_mb = ts_file.stat().st_size / 1024 / 1024
    print(f"\nRecording saved: {ts_file} ({size_mb:.1f} MB)")

    if args.no_convert:
        return

    if remux_to_mp4(ts_file, mp4_file):
        print(f"Done: {mp4_file}")
        if not args.keep_ts:
            ts_file.unlink()
            print("ts file deleted.")
    else:
        print(f"Conversion failed. The original recording is kept at: {ts_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()
