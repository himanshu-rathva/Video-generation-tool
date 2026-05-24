import os
import json
import random
from moviepy.editor import (
    VideoFileClip, 
    AudioFileClip, 
    CompositeVideoClip, 
    concatenate_videoclips, 
    ColorClip,
    CompositeAudioClip
)

# Add src to path so we can import our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.pexels_fetcher import download_broll
from src.caption_engine import render_web_captions
from src.ui_automation import capture_ui_workflow, render_code_visual
from src.music_director import download_background_music, build_sidechain_ducking_filter, download_sfx

def render_final_video(script_path: str):
    print("--- PHASE 3: ADVANCED FACELESS VIDEO RENDERING ENGINE (V2) ---")
    if not os.path.exists(script_path):
        print(f"Error: Script file not found at {script_path}")
        return
        
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)
        
    topic = script_data.get("topic", "unknown")
    music_mood = script_data.get("music_mood", "high energy tech beats")
    timeline = script_data.get("timeline", [])
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    outputs_dir = os.path.join(base_dir, "outputs", "rendered_videos")
    os.makedirs(outputs_dir, exist_ok=True)
    
    final_output_path = os.path.join(outputs_dir, f"{topic.replace(' ', '_').lower()}_final.mp4")
    
    video_segments = []
    video_size = (1080, 1920) # YouTube Shorts / Reels portrait format
    
    global_time = 0.0
    segment_starts = []
    active_speech_intervals = []
    
    for i, segment in enumerate(timeline):
        audio_path = segment.get("audio_path")
        timestamp_path = segment.get("timestamp_path")
        visual_type = segment.get("visual_type", "broll")
        visual_prompt = segment.get("visual_prompt", "")
        visual_keyword = segment.get("visual_keyword", topic)
        
        if not audio_path or not os.path.exists(audio_path):
            print(f"Skipping segment {i}: Audio not found.")
            continue
            
        print(f"\n🎬 Processing Segment {i} [{visual_type.upper()}]: {visual_keyword}")
        
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            segment_starts.append(global_time)
            
            # --- 1. VISUAL GENERATION (Dynamic based on Type) ---
            bg_clip = None
            
            if visual_type == "code":
                # Render programmatic code visualizer
                code_filename = f"code_{i}.webm"
                code_path = render_code_visual(visual_prompt, duration, code_filename)
                
                if code_path and os.path.exists(code_path):
                    bg_clip = VideoFileClip(code_path)
            
            elif visual_type == "ui":
                # Render Dynamic UI search mockups
                ui_filename = f"ui_{i}.webm"
                ui_path = capture_ui_workflow(visual_keyword, duration, ui_filename, timestamp_path)
                
                if ui_path and os.path.exists(ui_path):
                    bg_clip = VideoFileClip(ui_path)
                    
            if not bg_clip:
                # Default/Fallback: Fetch high-quality vertical B-Roll from Pexels
                broll_filename = os.path.join(base_dir, "assets", "visuals", f"broll_{i}.mp4")
                os.makedirs(os.path.dirname(broll_filename), exist_ok=True)
                
                broll_path = download_broll(visual_keyword, broll_filename, duration)
                
                if broll_path and os.path.exists(broll_path):
                    bg_clip = VideoFileClip(broll_path)
                else:
                    # Solid beautiful dark fallback color if all fail
                    colors = [(15, 12, 30), (20, 10, 20), (10, 20, 20)]
                    bg_clip = ColorClip(size=video_size, color=random.choice(colors), duration=duration)
            
            # Loop/trim and format the B-roll/visual to exactly 9:16 portrait
            if bg_clip.duration < duration:
                import moviepy.video.fx.all as vfx
                bg_clip = bg_clip.fx(vfx.loop, duration=duration)
            else:
                bg_clip = bg_clip.subclip(0, duration)
                
            # Resize and crop to 9:16 vertical ratio
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
            
            # --- 2. ADVANCED VFX CAPTION OVERLAY ---
            caption_clips = []
            if timestamp_path and os.path.exists(timestamp_path):
                # Save web captions to WebM green screen
                caption_filename = os.path.join(base_dir, "assets", "visuals", f"captions_{i}.webm")
                caption_path = render_web_captions(timestamp_path, caption_filename, duration)
                
                if caption_path and os.path.exists(caption_path):
                    # Load green screen, chromakey it out, and add as an overlay clip
                    green_clip = VideoFileClip(caption_path, has_mask=True)
                    import moviepy.video.fx.all as vfx
                    
                    # Key out pure green screen (#00ff00)
                    overlay_clip = green_clip.fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)
                    caption_clips = [overlay_clip]
                    
                    # Accumulate speech timestamps for dynamic audio sidechain ducking
                    with open(timestamp_path, "r", encoding="utf-8") as tf:
                        timestamps = json.load(tf)
                        for ts in timestamps:
                            active_speech_intervals.append((
                                global_time + ts.get("startTime", 0.0),
                                global_time + ts.get("endTime", 0.0)
                            ))
                            
            # --- 3. COMPOSITION ---
            layers = [bg_clip] + caption_clips
            final_segment = CompositeVideoClip(layers, size=video_size)
            final_segment = final_segment.set_audio(audio_clip)
            
            video_segments.append(final_segment)
            global_time += duration
            
        except Exception as e:
            print(f"❌ Error rendering segment {i}: {e}")
            
    if not video_segments:
        print("Error: No segments were successfully rendered.")
        return
        
    print("\n🎬 Stitching all vertical visual segments together...")
    final_video = concatenate_videoclips(video_segments, method="compose")
    
    # --- 4. ADVANCED MUSIC & AUDIO COMPOSITING (DUCKING & SFX) ---
    speech_audio = final_video.audio
    audio_tracks = [speech_audio]
    
    # 4a. Dynamic Mood background music
    bg_music_filename = os.path.join(base_dir, "assets", "audio", "bg_music.mp3")
    bg_music_path = download_background_music(music_mood, bg_music_filename)
    
    if bg_music_path and os.path.exists(bg_music_path):
        bg_music = AudioFileClip(bg_music_path)
        
        # Loop music if it's shorter than the final video duration
        if bg_music.duration < final_video.duration:
            import moviepy.audio.fx.all as afx
            bg_music = bg_music.fx(afx.audio_loop, duration=final_video.duration)
        else:
            bg_music = bg_music.subclip(0, final_video.duration)
            
        # Apply sidechain volume envelope based on our word timings
        print("🎵 Music Director: Generating custom sidechain volume envelope for audio ducking...")
        ducking_filter = build_sidechain_ducking_filter(active_speech_intervals)
        
        # Apply volume envelopes dynamically
        bg_music = bg_music.fl(lambda gf, t: ducking_filter(t) * gf(t))
        audio_tracks.append(bg_music)
        
    # 4b. Swoosh Sound Effects at transition points
    swish_filename = os.path.join(base_dir, "assets", "audio", "swoosh.ogg")
    swish_path = download_sfx(swish_filename)
    
    if swish_path and os.path.exists(swish_path):
        print(f"🔊 Audio Director: Placing swoosh transition sound effects between segments...")
        # Place swish at every transition start (skip segment 0 start)
        for transition_t in segment_starts[1:]:
            swish_clip = AudioFileClip(swish_path).set_start(transition_t).volumex(0.30)
            audio_tracks.append(swish_clip)
            
    # Composite all audio tracks together and bind to final video
    print("🔊 Compositing final premium stereo audio mix...")
    final_audio = CompositeAudioClip(audio_tracks)
    final_video = final_video.set_audio(final_audio)
    
    # --- 5. RENDER THE MASTERPIECE ---
    print(f"\n💾 Saving Final High-Quality Masterpiece to: {final_output_path}")
    final_video.write_videofile(
        final_output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None # Suppress large verbose MoviePy logs
    )
    print(f"🎉 SUCCESS! WORLD'S BEST HIGH QUALITY VIDEO GENERATED: {final_output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Phase 3: Render Pro-Grade Faceless B-Roll & Visuals Video")
    parser.add_argument("--script", type=str, required=True)
    args = parser.parse_args()
    render_final_video(args.script)
