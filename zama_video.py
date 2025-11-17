# zama_video.py
import os
import requests
import subprocess
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import textwrap

BLOG_URL = "https://www.zama.org/blog"
VIDEO_OUT = "zama_final.mp4"

def fetch_blog_text(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    heads = soup.find_all(["h2", "h3"])

    blocks = []
    for h in heads[:6]:
        t = h.get_text(strip=True)
        if len(t) > 15:
            blocks.append(t)

    if not blocks:
        blocks = ["Zama – Secure AI with Homomorphic Encryption."]

    return blocks


def create_slide(text, i):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), color="white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
        small = ImageFont.truetype("DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    y = 120
    wrapper = textwrap.TextWrapper(width=35)
    for line in wrapper.wrap(text=text):
        draw.text((100, y), line, fill="black", font=font)
        y += 60

    draw.text((100, 650), "Created by @AmitKum955", fill="gray", font=small)

    if os.path.exists("logo.png"):
        logo = Image.open("logo.png").convert("RGBA")
        logo.thumbnail((150, 150))
        img.paste(logo, (1100, 20), logo)

    fname = f"slide_{i}.png"
    img.save(fname)
    return fname


def generate_voice(text_blocks):
    full = ". ".join(text_blocks)
    open("tts.txt", "w").write(full)

    subprocess.run([
        "espeak-ng", "-v", "en", "-s", "140", "-f", "tts.txt", "-w", "voice.wav"
    ], check=False)

    if os.path.exists("voice.wav"):
        subprocess.run([
            "ffmpeg", "-y", "-i", "voice.wav",
            "-af", "volume=1.5", "voice_fixed.wav"
        ])
        return "voice_fixed.wav"

    return None


def make_slides_video(slides):
    with open("slides.txt", "w") as f:
        for s in slides:
            f.write(f"file '{s}'\n")
            f.write("duration 5\n")
        f.write(f"file '{slides[-1]}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", "slides.txt", "-vsync", "vfr", "-pix_fmt", "yuv420p",
        "video_no_audio.mp4"
    ])


def merge(video, audio):
    if not audio:
        subprocess.run([
            "ffmpeg","-y","-f","lavfi","-i","anullsrc=r=44100:cl=mono",
            "-t","2","silent.wav"
        ])
        audio = "silent.wav"

    subprocess.run([
        "ffmpeg","-y","-i","video_no_audio.mp4","-i",audio,
        "-c:v","copy","-c:a","aac","-shortest",VIDEO_OUT
    ])


def main():
    blocks = fetch_blog_text(BLOG_URL)
    slides = []
    for i, b in enumerate(blocks):
        slides.append(create_slide(b, i))

    audio = generate_voice(blocks)
    make_slides_video(slides)
    merge("video_no_audio.mp4", audio)

    print("🎉 VIDEO READY:", VIDEO_OUT)


if __name__ == "__main__":
    main()
