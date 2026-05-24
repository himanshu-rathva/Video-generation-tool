import os
import json
import random
import time
from moviepy.editor import (
    VideoFileClip, 
    AudioFileClip, 
    CompositeVideoClip, 
    concatenate_videoclips, 
    ColorClip,
    CompositeAudioClip
)
from playwright.sync_api import sync_playwright

# Add src to path so we can import our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.pexels_fetcher import download_broll
from src.music_director import download_background_music, build_sidechain_ducking_filter, download_sfx

def render_segment_in_browser(visual_type: str, broll_path: str, visual_prompt: str, visual_keyword: str, timestamp_path: str, duration: float, output_path: str) -> str:
    """
    Renders background, dynamic typing visuals, and active bouncy subtitles
    together in a single browser canvas via Playwright and captures the output.
    Avoids slow CPU chroma-keying pixel masking inside MoviePy.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    template_path = os.path.join(base_dir, "src", "templates", "master_template.html")
    
    if not os.path.exists(template_path):
        print(f"❌ Master template not found at: {template_path}")
        return None
        
    timestamps = []
    if timestamp_path and os.path.exists(timestamp_path):
        with open(timestamp_path, "r", encoding="utf-8") as tf:
            timestamps = json.load(tf)
            
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎬 Playwright Master Renderer: Animating background + VFX subtitles for {duration:.2f}s...")
    
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
            
            # Prepare arguments safely for browser evaluation
            broll_file_url = f"file://{os.path.abspath(broll_path)}" if (broll_path and os.path.exists(broll_path)) else ""
            
            escaped_visual_type = json.dumps(visual_type)
            escaped_broll_url = json.dumps(broll_file_url)
            escaped_code = json.dumps(visual_prompt)
            escaped_ui_keyword = json.dumps(visual_keyword)
            json_timestamps = json.dumps(timestamps)
            
            # Call the JS dynamic orchestrator
            page.evaluate(f"window.startMasterRender({escaped_visual_type}, {escaped_broll_url}, {escaped_code}, {escaped_ui_keyword}, {json_timestamps}, {duration})")
            
            # Sleep for segment length + buffer to record everything
            time.sleep(duration + 0.3)
            
        except Exception as e:
            print(f"❌ Browser render execution error: {e}")
        finally:
            page.close()
            context.close()
            browser.close()
            
            # Find and rename Playwright's recorded .webm clip
            recorded_files = [
                os.path.join(output_dir, f) 
                for f in os.listdir(output_dir) 
                if f.endswith(".webm") and not f.startswith("broll") and not f.startswith("code") and not f.startswith("ui") and not f.startswith("captions")
            ]
            
            if recorded_files:
                latest_webm = max(recorded_files, key=os.path.getctime)
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(latest_webm, output_path)
                print(f"✅ Rendered Segment Saved: {output_path}")
                return output_path
                
    return None

def render_final_video(script_path: str):
    print("--- PHASE 3: LIGHTNING-FAST VERTICAL MASTER RENDER ENGINE (V3) ---")
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
    video_size = (1080, 1920)
    
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
            
        print(f"\n🎥 Compositing Segment {i} [{visual_type.upper()}]: '{visual_keyword}'")
        
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            segment_starts.append(global_time)
            
            # --- 1. DOWNLOAD ASSETS IF B-ROLL ---
            broll_path = None
            if visual_type == "broll":
                broll_filename = os.path.join(base_dir, "assets", "visuals", f"broll_{i}.mp4")
                os.makedirs(os.path.dirname(broll_filename), exist_ok=True)
                broll_path = download_broll(visual_keyword, broll_filename, duration)
            
            # --- 2. HARDWARE ACCELERATED BROWSER RENDER ---
            segment_output_filename = os.path.join(base_dir, "assets", "visuals", f"rendered_segment_{i}.webm")
            rendered_path = render_segment_in_browser(
                visual_type=visual_type,
                broll_path=broll_path,
                visual_prompt=visual_prompt,
                visual_keyword=visual_keyword,
                timestamp_path=timestamp_path,
                duration=duration,
                output_path=segment_output_filename
            )
            
            if rendered_path and os.path.exists(rendered_path):
                # Load pre-rendered segment clip directly
                bg_clip = VideoFileClip(rendered_path)
            else:
                # Emergency dark aesthetic fallback
                colors = [(15, 12, 30), (20, 10, 20), (10, 20, 20)]
                bg_clip = ColorClip(size=video_size, color=random.choice(colors), duration=duration)
                
            # Set the voiceover audio on the visual clip
            bg_clip = bg_clip.subclip(0, duration).set_audio(audio_clip)
            video_segments.append(bg_clip)
            
            # Map word-level timestamps globally for music ducking sidechain
            if timestamp_path and os.path.exists(timestamp_path):
                with open(timestamp_path, "r", encoding="utf-8") as tf:
                    timestamps = json.load(tf)
                    for ts in timestamps:
                        active_speech_intervals.append((
                            global_time + ts.get("startTime", 0.0),
                            global_time + ts.get("endTime", 0.0)
                        ))
            
            global_time += duration
            
        except Exception as e:
            print(f"❌ Error rendering segment {i}: {e}")
            
    if not video_segments:
        print("Error: No segments were successfully rendered.")
        return
        
    print("\n🎬 Instant Stitching of pre-rendered segments...")
    final_video = concatenate_videoclips(video_segments, method="compose")
    
    # --- 3. PREMIUM CONTINUOUS STEREO MIX (MUSIC & TRANSITION SOUNDS) ---
    speech_audio = final_video.audio
    audio_tracks = [speech_audio]
    
    # 3a. Smart background music selection & sidechain ducking
    bg_music_filename = os.path.join(base_dir, "assets", "audio", "bg_music.mp3")
    bg_music_path = download_background_music(music_mood, bg_music_filename)
    
    if bg_music_path and os.path.exists(bg_music_path):
        bg_music = AudioFileClip(bg_music_path)
        if bg_music.duration < final_video.duration:
            import moviepy.audio.fx.all as afx
            bg_music = bg_music.fx(afx.audio_loop, duration=final_video.duration)
        else:
            bg_music = bg_music.subclip(0, final_video.duration)
            
        print("🎵 Music Director: Applying dynamic ducking sidechain curve...")
        ducking_filter = build_sidechain_ducking_filter(active_speech_intervals)
        bg_music = bg_music.fl(lambda gf, t: ducking_filter(t) * gf(t))
        audio_tracks.append(bg_music)
        
    # 3b. Swish transition sounds
    swish_filename = os.path.join(base_dir, "assets", "audio", "swoosh.ogg")
    swish_path = download_sfx(swish_filename)
    
    if swish_path and os.path.exists(swish_path):
        print("🔊 Audio Director: Placing dynamic swoosh sound effects on transitions...")
        for transition_t in segment_starts[1:]:
            swish_clip = AudioFileClip(swish_path).set_start(transition_t).volumex(0.35)
            audio_tracks.append(swish_clip)
            
    # Composite all audio and bind to the master video track
    final_audio = CompositeAudioClip(audio_tracks)
    final_video = final_video.set_audio(final_audio)
    
    # --- 4. RENDER FINAL MP4 ---
    print(f"\n💾 Saving Final Masterpiece to: {final_output_path}")
    final_video.write_videofile(
        final_output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None # Suppress large logs to prevent browser tab freeze
    )
    print(f"🎉 MASTERPIECE GENERATED SUCCESSFULLY IN RECORD TIME! Path: {final_output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Phase 3: Render Pro-Grade Vertical Video in Record Time")
    parser.add_argument("--script", type=str, required=True)
    args = parser.parse_args()
    render_final_video(args.script)
