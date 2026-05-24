import os
import json
import time
from playwright.sync_api import sync_playwright

def capture_ui_workflow(keyword: str, duration: float, output_filename: str, timestamp_path: str = None):
    """
    HeyGen-Style Dynamic UI Mockup Renderer.
    Instead of capturing live generic sites, this renders a dynamic, perfect UI 
    (like Google Gemini) and syncs the typing animations EXACTLY to the word timestamps.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    visuals_dir = os.path.join(base_dir, "assets", "visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    
    output_filename = output_filename.replace(".mp4", ".webm")
    output_path = os.path.join(visuals_dir, output_filename)
    
    if os.path.exists(output_path):
        print(f"Using cached dynamic UI capture for '{keyword}': {output_path}")
        return output_path

    print(f"Rendering Dynamic UI Mockup (HeyGen Architecture) for: '{keyword}'...")
    
    # Dynamically generate the Mock UI based on the keyword
    header_text = f"{keyword}" if keyword and len(keyword) < 20 else "Gemini UI"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            background-color: #131314;
            color: #e3e3e3;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
        }}
        .header {{
            font-size: 3.5rem;
            background: -webkit-linear-gradient(45deg, #4285f4, #d96570, #9b72cb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 50px;
            font-weight: 600;
        }}
        .search-box {{
            background-color: #1e1f20;
            border: 1px solid #444;
            border-radius: 30px;
            padding: 25px 40px;
            width: 70%;
            font-size: 2rem;
            display: flex;
            align-items: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        .cursor {{
            display: inline-block;
            width: 4px;
            height: 2.2rem;
            background-color: #e3e3e3;
            margin-left: 8px;
            animation: blink 1s step-end infinite;
        }}
        @keyframes blink {{
            50% {{ opacity: 0; }}
        }}
    </style>
    </head>
    <body>
        <div class="header">Hello, {header_text}</div>
        <div class="search-box">
            <span id="text-container"></span><span class="cursor"></span>
        </div>
        <script>
            // Playwright will call this function to type words exactly at the timestamp!
            window.typeWord = function(text) {{
                document.getElementById('text-container').innerText += text + " ";
            }}
        </script>
    </body>
    </html>
    """
    
    html_path = os.path.join(visuals_dir, "temp_dynamic_ui.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    timestamps = []
    if timestamp_path and os.path.exists(timestamp_path):
        with open(timestamp_path, "r", encoding="utf-8") as f:
            timestamps = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=visuals_dir,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        try:
            page.goto(f"file://{html_path}")
            
            # The Magic Syncing Engine
            if timestamps:
                start_time = time.time()
                for ts in timestamps:
                    word = ts.get("word", "")
                    target_time = ts.get("startTime", 0.0)
                    
                    # Pause execution until the exact millisecond
                    while (time.time() - start_time) < target_time:
                        time.sleep(0.005)
                        
                    # Inject the word exactly when spoken
                    page.evaluate(f"window.typeWord('{word}')")
                
                # Keep recording until audio finishes
                elapsed = time.time() - start_time
                if elapsed < duration:
                    time.sleep(duration - elapsed)
            else:
                time.sleep(duration)
                
        except Exception as e:
            print(f"Error rendering dynamic UI: {e}")
        finally:
            page.close()
            context.close()
            browser.close()
            
            # Clean up and rename
            files = [
                os.path.join(visuals_dir, f) 
                for f in os.listdir(visuals_dir) 
                if f.endswith(".webm") and not f.startswith("code") and not f.startswith("caption")
            ]
            if files:
                latest_video = max(files, key=os.path.getctime)
                if latest_video != output_path:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    os.rename(latest_video, output_path)
                
                # Delete temp html
                if os.path.exists(html_path):
                    os.remove(html_path)
                    
                return output_path
            
    return None

def render_code_visual(code_text: str, duration: float, output_filename: str) -> str:
    """
    Kinetic Codebase Visual Renderer.
    Loads the cinematic IDE-style code visualizer template, feeds the code text,
    plays characters typing and camera movements via GSAP, and records a 9:16 vertical video.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    visuals_dir = os.path.join(base_dir, "assets", "visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    
    output_filename = output_filename.replace(".mp4", ".webm")
    output_path = os.path.join(visuals_dir, output_filename)
    
    if os.path.exists(output_path):
        print(f"Using cached code typing visual: {output_path}")
        return output_path

    print(f"🎬 Code Visualizer Engine: Rendering cinematically highlighted typing sequence...")
    
    template_path = os.path.join(base_dir, "src", "templates", "code_template.html")
    if not os.path.exists(template_path):
        print(f"❌ Code template not found at: {template_path}")
        return None
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=visuals_dir,
            record_video_size={"width": 1080, "height": 1920},
            viewport={"width": 1080, "height": 1920}
        )
        page = context.new_page()
        
        try:
            page.goto(f"file://{template_path}")
            
            # Escape newlines and quotes to prevent JS parsing syntax errors
            escaped_code = json.dumps(code_text)
            page.evaluate(f"window.loadCode({escaped_code}, {duration})")
            
            # Wait for compilation and animation
            time.sleep(duration + 0.3)
            
        except Exception as e:
            print(f"❌ Error rendering code visualizer: {e}")
        finally:
            page.close()
            context.close()
            browser.close()
            
            # Playwright saves a random file.webm in visuals_dir. Let's isolate the code video.
            recorded_files = [
                os.path.join(visuals_dir, f) 
                for f in os.listdir(visuals_dir) 
                if f.endswith(".webm") and not f.startswith("broll") and not f.startswith("caption") and "temp" not in f
            ]
            
            if recorded_files:
                latest_webm = max(recorded_files, key=os.path.getctime)
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(latest_webm, output_path)
                print(f"✅ Dynamic Code Typing Visual saved to: {output_path}")
                return output_path
                
    return None

if __name__ == "__main__":
    test_code = "def start_ai():\n    engine = CoreEngine()\n    engine.train(epochs=100)\n    return 'Automation Active!'"
    render_code_visual(test_code, 5.0, "test_code.webm")
