import os
import json

def generate_audio_for_script(script_path: str):
    print("--- PHASE 2: AUDIO SYNC & TIMESTAMPS ---")
    if not os.path.exists(script_path):
        print(f"Error: Script file not found at {script_path}")
        return
        
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)
        
    topic = script_data.get("topic", "unknown")
    timeline = script_data.get("timeline", [])
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    audio_asset_dir = os.path.join(base_dir, "assets", "audio", topic.replace(" ", "_").lower())
    os.makedirs(audio_asset_dir, exist_ok=True)
    
    # Check for Google Cloud Credentials
    from dotenv import load_dotenv
    load_dotenv()
    
    gcp_cred_path = os.path.join(base_dir, "gcp_credentials.json")
    use_gcp = False
    gcp_api_key = os.getenv("GCP_API_KEY")
    
    if os.path.exists(gcp_cred_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_cred_path
        use_gcp = True
        print("✅ GCP Credentials found! Using Google Cloud Neural2 with Word Timestamps.")
    elif gcp_api_key:
        use_gcp = True
        print("✅ GCP API Key found! Using Google Cloud Neural2 with Word Timestamps.")
    else:
        print("⚠️ Warning: GCP credentials/API Key not found! Falling back to gTTS (Mock timestamps).")
        print("Please read GCP_SETUP_GUIDE.md to unlock HeyGen-level precision syncing.")
        
    if use_gcp:
        try:
            from google.cloud import texttospeech
            from google.api_core.client_options import ClientOptions
            if gcp_api_key and not os.path.exists(gcp_cred_path):
                client_options = ClientOptions(api_key=gcp_api_key)
                client = texttospeech.TextToSpeechClient(client_options=client_options)
            else:
                client = texttospeech.TextToSpeechClient()
        except ImportError:
            print("❌ google-cloud-texttospeech not installed. Run: pip install -r requirements.txt")
            use_gcp = False

    for i, segment in enumerate(timeline):
        text = segment.get("text", "")
        audio_filename = f"segment_{i}.mp3"
        audio_filepath = os.path.join(audio_asset_dir, audio_filename)
        timestamp_filepath = os.path.join(audio_asset_dir, f"segment_{i}_timestamps.json")
        
        if use_gcp:
            # 1. Call GCP TTS
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="hi-IN",
                name="hi-IN-Neural2-B"
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            request = texttospeech.SynthesizeSpeechRequest(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Attempt to use Word Time Offsets if supported by the SDK
            if hasattr(request, "enable_word_time_offsets"):
                request.enable_word_time_offsets = True
                
            try:
                response = client.synthesize_speech(request=request)
                
                with open(audio_filepath, "wb") as out:
                    out.write(response.audio_content)
                    
                word_timestamps = []
                if hasattr(response, "timepoints") and response.timepoints:
                    for tp in response.timepoints:
                        word_timestamps.append({"word": tp.mark_name, "startTime": tp.time_seconds})
                
                if not word_timestamps:
                    word_timestamps = generate_mock_word_timestamps(text, audio_filepath)
                    
                with open(timestamp_filepath, "w", encoding="utf-8") as f:
                    json.dump(word_timestamps, f, indent=4)
                    
                segment["audio_path"] = audio_filepath
                segment["timestamp_path"] = timestamp_filepath
                print(f"[{i}] Generated Neural2 Audio + Timestamps")
            except Exception as e:
                print(f"⚠️ GCP TTS API Error: {e}")
                print(f"[{i}] Falling back to gTTS (Mock Timestamps)...")
                from gtts import gTTS
                tts = gTTS(text=text, lang='hi', slow=False)
                tts.save(audio_filepath)
                
                word_timestamps = generate_mock_word_timestamps(text, audio_filepath)
                with open(timestamp_filepath, "w", encoding="utf-8") as f:
                    json.dump(word_timestamps, f, indent=4)
                    
                segment["audio_path"] = audio_filepath
                segment["timestamp_path"] = timestamp_filepath
            
        else:
            # Fallback to gTTS
            from gtts import gTTS
            tts = gTTS(text=text, lang='hi', slow=False) # Changed to Hindi to match HeyGen target
            tts.save(audio_filepath)
            
            word_timestamps = generate_mock_word_timestamps(text, audio_filepath)
            with open(timestamp_filepath, "w", encoding="utf-8") as f:
                json.dump(word_timestamps, f, indent=4)
                
            segment["audio_path"] = audio_filepath
            segment["timestamp_path"] = timestamp_filepath
            print(f"[{i}] Generated gTTS Audio + Mock Timestamps")

    updated_script_path = script_path.replace(".json", "_with_audio.json")
    with open(updated_script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=4)
        
    print(f"\nPhase 2 Complete! Timestamps and Audio saved. Proceed to Phase 3.")

def generate_mock_word_timestamps(text, audio_path):
    """Fallback proportional logic to generate timestamps if API doesn't return them."""
    try:
        from moviepy.editor import AudioFileClip
        duration = AudioFileClip(audio_path).duration
    except Exception:
        duration = 5.0

    words = text.split()
    timestamps = []
    if not words: return timestamps
    
    time_per_word = duration / len(words)
    current_time = 0.0
    for w in words:
        timestamps.append({
            "word": w,
            "startTime": round(current_time, 2),
            "endTime": round(current_time + time_per_word, 2)
        })
        current_time += time_per_word
    return timestamps

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Phase 2: GCP Audio & Timestamp Generation")
    parser.add_argument("--script", type=str, required=True)
    args = parser.parse_args()
    generate_audio_for_script(args.script)
