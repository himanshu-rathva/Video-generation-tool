import os
import json
import random
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, ColorClip

# Add src to path so we can import our new modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.pexels_fetcher import download_broll
from src.caption_engine import generate_captions_from_timestamps

def render_final_video(script_path: str):
    print("--- PHASE 3: FACELESS VIDEO RENDERING (SHORTS/REELS STYLE) ---")
    if not os.path.exists(script_path):
        print(f"Error: Script file not found at {script_path}")
        return
        
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)
        
    topic = script_data.get("topic", "unknown")
    timeline = script_data.get("timeline", [])
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    outputs_dir = os.path.join(base_dir, "outputs", "rendered_videos")
    os.makedirs(outputs_dir, exist_ok=True)
    
    final_output_path = os.path.join(outputs_dir, f"{topic.replace(' ', '_').lower()}_final.mp4")
    
    video_segments = []
    video_size = (1080, 1920) # YouTube Shorts / Reels aspect ratio 9:16
    
    for i, segment in enumerate(timeline):
        audio_path = segment.get("audio_path")
        timestamp_path = segment.get("timestamp_path")
        visual_keyword = segment.get("visual_keyword", topic)
        
        if not audio_path or not os.path.exists(audio_path):
            print(f"Skipping segment {i}: Audio not found.")
            continue
            
        print(f"\n🎥 Processing Segment {i}: {visual_keyword}")
        
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # 1. Fetch B-Roll from Pexels
            broll_filename = os.path.join(base_dir, "assets", "visuals", f"broll_{i}.mp4")
            os.makedirs(os.path.dirname(broll_filename), exist_ok=True)
            
            broll_path = download_broll(visual_keyword, broll_filename, duration)
            
            if broll_path and os.path.exists(broll_path):
                bg_clip = VideoFileClip(broll_path)
                
                # Loop or trim B-roll to match audio duration perfectly
                if bg_clip.duration < duration:
                    import moviepy.video.fx.all as vfx
                    bg_clip = bg_clip.fx(vfx.loop, duration=duration)
                else:
                    bg_clip = bg_clip.subclip(0, duration)
            else:
                # Fallback to a colored background if Pexels fails or API key missing
                colors = [(30, 30, 40), (40, 20, 30), (20, 40, 40)]
                bg_clip = ColorClip(size=video_size, color=random.choice(colors), duration=duration)
                
            # Resize and crop to 9:16 portrait
            from moviepy.video.fx.all import crop, resize
            w, h = bg_clip.size
            target_ratio = 1080 / 1920.0
            current_ratio = w / float(h)
            
            if current_ratio > target_ratio:
                # Video is wider, crop width
                new_w = int(h * target_ratio)
                x_center = w / 2
                bg_clip = crop(bg_clip, width=new_w, height=h, x_center=x_center)
            else:
                # Video is taller, crop height
                new_h = int(w / target_ratio)
                y_center = h / 2
                bg_clip = crop(bg_clip, width=w, height=new_h, y_center=y_center)
                
            bg_clip = resize(bg_clip, newsize=video_size)
            
            # 2. Generate Pop-Up Captions synced to exact timestamps
            caption_clips = []
            if timestamp_path and os.path.exists(timestamp_path):
                print("📝 Generating synchronized pop-up captions...")
                caption_clips = generate_captions_from_timestamps(timestamp_path, video_size)
                
            # 3. Composite everything together
            layers = [bg_clip] + caption_clips
            final_segment = CompositeVideoClip(layers, size=video_size)
            final_segment = final_segment.set_audio(audio_clip)
            
            video_segments.append(final_segment)
            
        except Exception as e:
            print(f"❌ Error rendering segment {i}: {e}")
            
    if not video_segments:
        print("Error: No segments were successfully rendered.")
        return
        
    print("\n🎬 Stitching all segments together...")
    final_video = concatenate_videoclips(video_segments, method="compose")
    
    print(f"💾 Saving Final Masterpiece to: {final_output_path}")
    final_video.write_videofile(
        final_output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None # Suppress massive MoviePy output
    )
    print(f"✅ FINAL VIDEO RENDERED SUCCESSFULLY: {final_output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Phase 3: Render Faceless B-Roll & Captions Video")
    parser.add_argument("--script", type=str, required=True)
    args = parser.parse_args()
    render_final_video(args.script)
