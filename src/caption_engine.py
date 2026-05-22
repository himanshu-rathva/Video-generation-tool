import json
import os

def generate_captions_from_timestamps(timestamp_path: str, video_size: tuple = (1080, 1920)):
    """
    Reads the word-level timestamp JSON and generates a list of MoviePy TextClips.
    Creates the 'Alex Hormozi' style fast-paced pop-up captions.
    """
    # Import inside function to avoid heavy loading if not needed
    try:
        from moviepy.editor import TextClip
    except ImportError:
        print("❌ MoviePy is not installed.")
        return []
        
    if not os.path.exists(timestamp_path):
        print(f"⚠️ Timestamp file not found: {timestamp_path}")
        return []
        
    with open(timestamp_path, "r", encoding="utf-8") as f:
        timestamps = json.load(f)
        
    text_clips = []
    
    for ts in timestamps:
        word = ts.get("word", "").strip()
        start_time = ts.get("startTime", 0.0)
        end_time = ts.get("endTime", 0.0)
        
        if not word or (end_time - start_time) <= 0:
            continue
            
        # Add a tiny buffer so words don't instantly disappear
        duration = (end_time - start_time) + 0.05 
        
        # Determine color based on keyword emphasis (optional MVP logic)
        color = 'yellow' if len(word) > 6 else 'white'
        
        try:
            # Create a dynamic text clip
            txt_clip = TextClip(
                word, 
                fontsize=110, 
                color=color, 
                font='Impact', # A bold, modern font suitable for Shorts
                stroke_color='black', 
                stroke_width=5,
                method='caption',
                size=(video_size[0] * 0.8, None)
            )
            
            txt_clip = (txt_clip
                        .set_position('center')
                        .set_start(start_time)
                        .set_duration(duration))
                        
            text_clips.append(txt_clip)
        except Exception as e:
            # If ImageMagick font fails, try fallback
            try:
                txt_clip = TextClip(
                    word, 
                    fontsize=90, 
                    color='white',
                    stroke_color='black', 
                    stroke_width=3
                )
                txt_clip = txt_clip.set_position('center').set_start(start_time).set_duration(duration)
                text_clips.append(txt_clip)
            except Exception as e2:
                print(f"Failed to generate caption for word '{word}': {e2}")
                
    return text_clips
