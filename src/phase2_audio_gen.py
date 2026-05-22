import os
import json
from gtts import gTTS

def generate_audio_for_script(script_path: str):
    """
    Reads the generated JSON script and creates audio files for each timeline segment.
    Uses a temporary manual asset folder. Falls back to gTTS for instant prototyping 
    before GCP Neural2 billing is configured.
    """
    if not os.path.exists(script_path):
        print(f"Error: Script file not found at {script_path}")
        return
        
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)
        
    topic = script_data.get("topic", "unknown")
    timeline = script_data.get("timeline", [])
    
    # Create manual asset folder
    base_dir = os.path.dirname(os.path.dirname(__file__))
    audio_asset_dir = os.path.join(base_dir, "assets", "audio", topic.replace(" ", "_").lower())
    os.makedirs(audio_asset_dir, exist_ok=True)
    
    print(f"Checking audio assets for topic: '{topic}' in {audio_asset_dir}...")
    
    for i, segment in enumerate(timeline):
        text = segment.get("text", "")
        # Naming convention for manual audio files
        audio_filename = f"segment_{i}.mp3"
        audio_filepath = os.path.join(audio_asset_dir, audio_filename)
        
        # Check if manual Neural2 audio was placed by user
        if os.path.exists(audio_filepath):
            print(f"[{i}] Found manual audio asset: {audio_filename}")
        else:
            print(f"[{i}] Manual asset missing. Generating temp audio via gTTS for: '{text[:30]}...'")
            # Fallback to gTTS for MVP pipeline completion
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(audio_filepath)
            
        # Update segment with audio path
        segment["audio_path"] = audio_filepath
        
    # Save the updated script with audio paths
    updated_script_path = script_path.replace(".json", "_with_audio.json")
    with open(updated_script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=4)
        
    print(f"\nPhase 2 Complete! Updated script saved to: {updated_script_path}")
    print("Note: Replace the gTTS .mp3 files in the assets folder with GCP Neural2 files when ready.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Phase 2: Audio Generation/Integration")
    parser.add_argument("--script", type=str, required=True, help="Path to the JSON script from Phase 1")
    args = parser.parse_args()
    
    generate_audio_for_script(args.script)
