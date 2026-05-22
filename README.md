# Video Generation Tool (MVP)

A highly efficient, cloud-based automated Video Generation Tool.

## Architecture

- **Brain (LLM)**: Google AI Studio (Gemini API)
- **Core Language**: Python
- **Video Framework**: Remotion AI / MoviePy
- **UI Automation**: Playwright
- **Storage & Hosting**: Git & GitHub
- **Execution Environment**: Google Colab

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure API Key:
   Add your Google AI Studio API key to the `.env` file.
3. Run Phase 1 Script Generation:
   ```bash
   python src/phase1_script_gen.py --topic "Your topic here"
   ```
