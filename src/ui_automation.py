import os
import time
from playwright.sync_api import sync_playwright

def capture_ui_workflow(keyword: str, duration: float, output_filename: str):
    """
    Automates a headless browser to capture a live software workflow based on a keyword.
    Records the session as a WebM video to be used in Phase 3.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    visuals_dir = os.path.join(base_dir, "assets", "visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    
    # Playwright writes WebM when recording video
    output_filename = output_filename.replace(".mp4", ".webm")
    output_path = os.path.join(visuals_dir, output_filename)
    
    if os.path.exists(output_path):
        print(f"Using cached UI capture for '{keyword}': {output_path}")
        return output_path

    print(f"Automating UI capture for keyword: '{keyword}' (Duration: {duration:.1f}s)...")
    
    with sync_playwright() as p:
        # headless=True is required for Colab environments
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=visuals_dir,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        try:
            # MVP Logic: Go to google and simulate typing the target keyword
            # This simulates a 'live workflow' dynamically driven by the AI script
            page.goto("https://www.google.com")
            search_box = page.locator("textarea[name='q'], input[name='q']").first
            search_box.wait_for()
            
            # Type slowly to simulate a human user
            search_box.type(f"{keyword}", delay=150)
            search_box.press("Enter")
            
            # Keep recording to perfectly match the audio duration from Phase 2
            time.sleep(duration)
            
        except Exception as e:
            print(f"Error during UI automation: {e}")
        finally:
            page.close()
            context.close()
            browser.close()
            
            # Playwright generates a random hash for the video filename.
            # We locate it and rename it to our structured `output_filename`
            files = [os.path.join(visuals_dir, f) for f in os.listdir(visuals_dir) if f.endswith(".webm")]
            if files:
                latest_video = max(files, key=os.path.getctime)
                if latest_video != output_path:
                    # Clean up old file if it somehow exists
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    os.rename(latest_video, output_path)
                return output_path
            
    return None

if __name__ == "__main__":
    # Quick test execution
    capture_ui_workflow("Google Gemini AI Automation", 5.0, "test_capture.webm")
