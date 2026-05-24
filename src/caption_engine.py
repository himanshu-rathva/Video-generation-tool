import json
import os
import time
from playwright.sync_api import sync_playwright

def render_web_captions(timestamp_path: str, output_path: str, duration: float) -> str:
    """
    Renders advanced GSAP word-by-word active captions on a green screen page 
    and records the result as a WebM video using Playwright.
    """
    print(f"🎬 Web VFX Caption Engine: Rendering dynamic captions for {duration}s...")
    
    if not os.path.exists(timestamp_path):
        print(f"⚠️ Timestamp file not found: {timestamp_path}")
        return None
        
    with open(timestamp_path, "r", encoding="utf-8") as f:
        timestamps = json.load(f)
        
    base_dir = os.path.dirname(os.path.dirname(__file__))
    template_path = os.path.join(base_dir, "src", "templates", "caption_template.html")
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found at {template_path}")
        return None
        
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # We must record at the target video size (1080, 1920)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=output_dir,
            record_video_size={"width": 1080, "height": 1920},
            viewport={"width": 1080, "height": 1920}
        )
        page = context.new_page()
        
        try:
            page.goto(f"file://{template_path}")
            
            # Inject timestamps and start the GSAP timeline
            json_timestamps = json.dumps(timestamps)
            page.evaluate(f"window.loadCaptions({json_timestamps})")
            
            # Wait for the exact duration of the speech + slight buffer to ensure no truncation
            time.sleep(duration + 0.3)
            
        except Exception as e:
            print(f"❌ Error during Playwright caption rendering: {e}")
        finally:
            page.close()
            context.close()
            browser.close()
            
            # Playwright saves a random file.webm in output_dir. Let's find it and rename it.
            recorded_files = [
                os.path.join(output_dir, f) 
                for f in os.listdir(output_dir) 
                if f.endswith(".webm") and not f.startswith("broll") and not f.startswith("code")
            ]
            
            if recorded_files:
                # Get the most recently created file
                latest_webm = max(recorded_files, key=os.path.getctime)
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(latest_webm, output_path)
                print(f"✅ Dynamic VFX Green Screen Captions saved to: {output_path}")
                return output_path
                
    return None

def generate_captions_from_timestamps(timestamp_path: str, video_size: tuple = (1080, 1920)):
    """
    Fallback MoviePy TextClip generator if Playwright fails or isn't used.
    Matches the old signature to ensure backward compatibility.
    """
    try:
        from moviepy.editor import TextClip
    except ImportError:
        print("❌ MoviePy is not installed.")
        return []
        
    if not os.path.exists(timestamp_path):
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
            
        duration = (end_time - start_time) + 0.05 
        color = 'yellow' if len(word) > 6 else 'white'
        
        try:
            txt_clip = TextClip(
                word, 
                fontsize=110, 
                color=color, 
                font='Impact', 
                stroke_color='black', 
                stroke_width=5,
                method='caption',
                size=(video_size[0] * 0.8, None)
            )
            txt_clip = txt_clip.set_position('center').set_start(start_time).set_duration(duration)
            text_clips.append(txt_clip)
        except Exception as e:
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
            except Exception:
                pass
                
    return text_clips
