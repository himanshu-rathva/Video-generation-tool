import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")

def generate_script(topic: str):
    """
    Generates a 60-second script using Gemini and formats it into a structured JSON timeline.
    """
    if not API_KEY or API_KEY == "your_google_ai_studio_api_key_here":
        print("WARNING: Please set a valid GEMINI_API_KEY in the .env file.")
        print("Falling back to a mocked script for demonstration purposes.")
        return mock_generate_script(topic)
        
    print(f"Generating script for topic: '{topic}' via Gemini API...")
    
    try:
        client = genai.Client(api_key=API_KEY)
        
        prompt = f"""
        You are an expert video script writer. Write a 60-second video script about: "{topic}".
        The script should be highly engaging, hook-driven, and perfectly timed for 60 seconds (around 130-150 words).
        
        Output the script strictly as a JSON object with a timeline. The JSON structure must be:
        {{
            "topic": "{topic}",
            "duration_seconds": 60,
            "music_mood": "cyberpunk synthwave" or "motivational cinematic" or "high energy tech beats" or "dark dramatic trap" (choose one fitting the topic),
            "timeline": [
                {{
                    "start_time": 0.0,
                    "end_time": 5.0,
                    "text": "Sentence or phrase to be spoken.",
                    "visual_type": "broll" or "code" or "ui",
                    "visual_prompt": "If 'broll', write a detailed ultra-HD cinematic stock video prompt. If 'code', write a valid short beautiful 4-8 line snippet of python/javascript code representing the topic. If 'ui', write the exact phrase or prompt the user types in an AI search bar.",
                    "visual_keyword": "A simple 1-3 word search term for Pexels API (e.g. 'coding neon', 'cybersecurity laptop', 'ai brain'). Keep it extremely simple for search matching."
                }}
            ]
        }}
        Ensure the timelines roughly cover the 60-second duration sequentially. Make the visual flow dynamic by mixing 'broll', 'code', and 'ui' elements creatively.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        script_data = json.loads(response.text)
        save_script(topic, script_data)
        return script_data
        
    except Exception as e:
        print(f"Error generating script: {e}")
        return None

def mock_generate_script(topic: str):
    """Fallback if API key isn't provided."""
    script_data = {
        "topic": topic,
        "duration_seconds": 60,
        "music_mood": "high energy tech beats",
        "timeline": [
            {
                "start_time": 0.0,
                "end_time": 5.0,
                "text": f"Welcome to this quick guide on {topic}.",
                "visual_type": "broll",
                "visual_prompt": "Cinematic shot of neon cyber tech laboratory with a programmer working in dark room, 4k resolution.",
                "visual_keyword": "tech neon programmer"
            },
            {
                "start_time": 5.0,
                "end_time": 15.0,
                "text": "Today we will see how AI can automate your daily workflow with simple code.",
                "visual_type": "code",
                "visual_prompt": "def automate_work():\n    for task in daily_routine:\n        ai.execute(task)\n        print('Done!')",
                "visual_keyword": "coding developer"
            }
        ]
    }
    save_script(topic, script_data)
    return script_data

def save_script(topic: str, script_data: dict):
    # Save to output file
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"{topic.replace(' ', '_').lower()}_script.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=4)
        
    print(f"Script saved to: {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a video script using Gemini.")
    parser.add_argument("--topic", type=str, default="How to build an AI automation tool", help="Topic for the video script")
    args = parser.parse_args()
    
    generate_script(args.topic)
