import os
import requests

# Stable public copyright-free music tracks for testing and production
MUSIC_URLS = {
    "cyberpunk synthwave": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "high energy tech beats": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "motivational cinematic": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "dark dramatic trap": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    "default": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
}

def download_background_music(mood: str, output_path: str) -> str:
    """
    Downloads high-quality copyright-free background music based on the topic mood.
    """
    mood = mood.lower()
    download_url = MUSIC_URLS.get(mood, MUSIC_URLS["default"])
    
    if os.path.exists(output_path):
        print(f"Using cached background music: {output_path}")
        return output_path
        
    print(f"🎵 Music Director: Downloading background track for mood '{mood}'...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        response = requests.get(download_url, stream=True, timeout=15)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"✅ Background music downloaded: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ Music download failed: {e}. Using silent fallback.")
        return None

def build_sidechain_ducking_filter(active_speech_intervals: list):
    """
    Generates a dynamic volume envelope function that acts as a sidechain gate.
    Ducks the background music smoothly when voiceover speech is active.
    """
    def volume_envelope(t):
        # Determine if speech is active in a small window around time 't'
        # This moving-window creates a perfect smooth attack/release volume fade
        steps = 7
        speaking_ratio = 0
        window_size = 0.3 # 300ms fade window
        
        for i in range(steps):
            check_t = t - (window_size / 2) + (i * window_size / (steps - 1))
            any_speech = False
            for start, end in active_speech_intervals:
                # 0.25s release buffer after word ends to prevent choppy volume drops
                if start <= check_t <= (end + 0.25):
                    any_speech = True
                    break
            if any_speech:
                speaking_ratio += 1
                
        ratio = speaking_ratio / steps # 0.0 (silent) to 1.0 (speaking)
        
        # Smooth interpolation:
        # Speaking volume: 0.08 (quiet enough to make voice clear)
        # Quiet volume: 0.38 (loud enough to fill empty space)
        return 0.38 - (0.30 * ratio)
        
    return volume_envelope

def download_sfx(output_path: str) -> str:
    """
    Downloads a high-quality swish/swoosh transition sound effect.
    """
    sfx_url = "https://actions.google.com/sounds/v1/transitional/swish_2.ogg"
    if os.path.exists(output_path):
        return output_path
        
    print(f"🔊 SFX Director: Downloading transition sound effect...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        response = requests.get(sfx_url, stream=True, timeout=15)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"✅ SFX downloaded: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ SFX download failed: {e}. Transitions will be silent.")
        return None

