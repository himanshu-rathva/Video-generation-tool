# Google Cloud Text-to-Speech Setup Guide

Kyunki hum HeyGen-level ka architecture bana rahe hain jisme **Millisecond-Level Word Timestamps** chahiye, iske liye Google Cloud TTS API sabse best (aur free) option hai.

Aapko bas ek `credentials.json` file chahiye jo aapke project ke backend me kaam karegi. Ise paane ke 4 aasan steps hain:

1. **Google Cloud Console Par Jayen:**
   - Link: [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Apni Gmail id se login karein (agar billing prompt aaye toh set kar lein, Google TTS ke 10 lakh characters har mahine free hote hain).

2. **Naya Project Banayen:**
   - Upar left me "Select a project" par click karein aur "New Project" banayen (Naam rakhein: `Video-Gen-MVP`).

3. **Text-to-Speech API Enable Karein:**
   - Upar search bar me type karein: `Cloud Text-to-Speech API`
   - Is par click karein aur **"Enable"** ka button daba dein.

4. **JSON Key Download Karein (Ye Sabse Zaruri Hai):**
   - Left menu me jayen: `APIs & Services` -> `Credentials`.
   - Upar **"Create Credentials"** par click karein -> **"Service Account"** chunein.
   - Uska naam de dein (jaise `tts-bot`), role me "Project -> Owner" ya "Basic -> Editor" de dein, aur "Done" kar dein.
   - Ab neeche Service Accounts list me us naye email par click karein, upar **"KEYS"** tab me jayen.
   - **"Add Key"** -> **"Create new key"** -> **"JSON"** select karein.
   
Ek choti si `.json` file aapke computer me download ho jayegi. 
Us file ka naam badal kar **`gcp_credentials.json`** rakh dein aur is project folder (`video-gen-tool`) ke andar rakh dein.

---
*Note: Maine aapke project ki `.gitignore` file me pehle se hi setup kar diya hai taaki aapka ye JSON aur `.env` kabhi bhi GitHub par galti se leak na ho!*
