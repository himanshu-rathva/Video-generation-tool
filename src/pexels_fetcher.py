import os
import requests
import random
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def download_broll(keyword: str, output_path: str, duration: float = 5.0) -> str:
    """
    Searches Pexels for a portrait video matching the keyword and downloads it.
    """
    if not PEXELS_API_KEY:
        print("⚠️ PEXELS_API_KEY not found. Cannot fetch B-roll.")
        return None
        
    print(f"🔍 Searching Pexels for B-Roll: '{keyword}'...")
    
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": keyword,
        "orientation": "portrait",
        "size": "medium",
        "per_page": 10
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        videos = data.get("videos", [])
        if not videos:
            print(f"⚠️ No Pexels videos found for '{keyword}'. Using fallback.")
            return None
            
        # Pick a random video from the top results to keep it fresh
        video_choice = random.choice(videos[:5])
        video_files = video_choice.get("video_files", [])
        
        # Find the best HD quality link
        download_url = None
        for file in video_files:
            if file.get("quality") == "hd" and file.get("width") is not None and file.get("width") >= 720:
                download_url = file.get("link")
                break
                
        if not download_url and video_files:
            download_url = video_files[0].get("link") # Fallback to first available
            
        if not download_url:
            return None
            
        print(f"⬇️ Downloading B-Roll from Pexels: {download_url.split('?')[0][-20:]}...")
        
        vid_response = requests.get(download_url, stream=True)
        vid_response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in vid_response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"✅ B-Roll saved to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Pexels API Error: {e}")
        return None

if __name__ == "__main__":
    download_broll("Artificial Intelligence", "test_broll.mp4")
