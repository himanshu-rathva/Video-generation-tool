import os
import json
from moviepy.editor import ColorClip, TextClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

def render_video(script_path: str):
    """
    Phase 3: Visual Sync and Render
    Reads the JSON timestamps and audio paths, creates synchronized clips, and renders the final MP4.
    """
    if not os.path.exists(script_path):
        print(f"Error: Script file not found at {script_path}")
        return
        
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)
        
    topic = script_data.get("topic", "unknown")
    timeline = script_data.get("timeline", [])
    
    print(f"Starting Phase 3 render for: '{topic}'...")
    
    video_clips = []
    
    for i, segment in enumerate(timeline):
        audio_path = segment.get("audio_path")
        visual_keyword = segment.get("visual_keyword", "No Keyword")
        text = segment.get("text", "")
        
        if not audio_path or not os.path.exists(audio_path):
            print(f"Warning: Audio file missing for segment {i}. Skipping.")
            continue
            
        # Load audio to get actual duration
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        # In a full Playwright implementation, we would trigger UI capture here.
        # For the MVP, we generate a placeholder visual clip using MoviePy.
        
        # 1. Visual Capture via Playwright (UI Automation)
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        try:
            from src.ui_automation import capture_ui_workflow
            from moviepy.editor import VideoFileClip
            
            video_filename = f"segment_{i}.webm"
            ui_video_path = capture_ui_workflow(visual_keyword, duration, video_filename)
            
            if ui_video_path and os.path.exists(ui_video_path):
                bg_clip = VideoFileClip(ui_video_path)
                # Ensure it matches exact duration
                if bg_clip.duration > duration:
                    bg_clip = bg_clip.subclip(0, duration)
                bg_clip = bg_clip.resize(newsize=(1920, 1080))
            else:
                bg_clip = ColorClip(size=(1920, 1080), color=(30, 30, 30), duration=duration)
        except ImportError:
            print("UI Automation module not found. Using ColorClip.")
            bg_clip = ColorClip(size=(1920, 1080), color=(30, 30, 30), duration=duration)
        
        # 2. Text Overlay (Visual Keyword)
        try:
            # Requires ImageMagick installed on the system to use TextClip effectively
            txt_clip = TextClip(f"[{visual_keyword}]\n{text}", fontsize=50, color='white', bg_color='transparent', size=(1800, 1000), method='caption')
            txt_clip = txt_clip.set_pos('center').set_duration(duration)
            
            # Combine
            comp_clip = CompositeVideoClip([bg_clip, txt_clip])
        except Exception as e:
            print(f"TextClip failed (ImageMagick might be missing/unconfigured). Using plain background. Error: {e}")
            comp_clip = bg_clip
            
        # Set the audio to the composite clip
        comp_clip = comp_clip.set_audio(audio_clip)
        
        video_clips.append(comp_clip)
        
    if not video_clips:
        print("No valid clips were generated. Aborting render.")
        return
        
    # Concatenate all segments sequentially
    print("Concatenating clips and rendering final video. This may take a moment...")
    final_video = concatenate_videoclips(video_clips, method="compose")
    
    # Save the output
    base_dir = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(base_dir, "outputs", "rendered_videos")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"{topic.replace(' ', '_').lower()}_final.mp4")
    
    # Render with optimal Colab settings (T4 GPU compatible if hw accel added later)
    final_video.write_videofile(
        output_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac", 
        threads=4, 
        preset="ultrafast" # fast render for MVP
    )
    
    print(f"\nRender Complete! Video saved to: {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Phase 3: Video Render")
    parser.add_argument("--script", type=str, required=True, help="Path to the JSON script from Phase 2 (with audio paths)")
    args = parser.parse_args()
    
    render_video(args.script)
