# 🎙️ Podcast Assets Generator

Upload a podcast episode and get back everything you need to publish it. Transcription, summary, YouTube title options, YouTube description, and key moments. Powered by Voxtral.

---

## ✨ What it does

Podcast Assets Generator is a Streamlit web app that takes an MP3 file and automatically produces:

- 📝 **Transcript** - full transcription of the episode, formatted into readable paragraphs
- 💡 **Summary** - a concise 3-5 sentence overview of the episode
- 🎬 **YouTube Titles** - 5 compelling title options ready to use
- 📄 **YouTube Description** - a full, keyword-rich description (2-4 paragraphs)
- ⭐ **Key Moments** - 8 bullet points highlighting the most important insights

Everything is displayed in a clean tabbed interface and can be copied directly from the app.

---

## 🛠️ Tech stack

| Component | Choice | Why |
|---|---|---|
| UI | [Streamlit](https://streamlit.io) | Fast to build, no frontend code needed |
| Transcription | Mistral API - `voxtral-mini-2507` | State-of-the-art speech model, free tier, no GPU needed |
| Asset generation | Mistral API - `mistral-medium-latest` | Strong instruction-following for structured content |
| Env management | python-dotenv | Simple, standard API key handling |

### 🔊 Why Voxtral?

Voxtral is Mistral's family of audio understanding models. It is built on top of Mistral's language models with a native audio encoder, which means it does not just transcribe speech - it understands context, handles multiple speakers, and produces clean, accurate output even for technical or domain-specific conversations.

**`voxtral-mini-2507`** was chosen because:
- It is optimised for speed and cost while maintaining high transcription quality
- It handles long-form audio (tested up to 45 minutes per episode)
- It is available on Mistral's free tier, making this project essentially free to run

### ☁️ Why use Voxtral via API instead of locally?

Voxtral is a large multimodal model. Running it locally requires significant hardware:

- **Minimum**: ~24 GB VRAM (e.g. an NVIDIA RTX 4090 or equivalent)
- **Recommended**: 40-80 GB VRAM for comfortable inference (e.g. A100, H100)
- Setup involves model weights download, CUDA configuration, and dependency management

Running it via the Mistral API offloads all of that. You get the same model quality without any hardware requirements, with no setup beyond an API key. For a tool you run a few times a week to process podcast episodes, the API is the right choice - fast, free (on the free tier), and zero maintenance.

---

## 🚀 Running it locally

### Prerequisites

- Python 3.10 or higher
- A [Mistral API key](https://console.mistral.ai/) (free tier is sufficient)

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/podcast-assets-generation.git
   cd podcast-assets-generation
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv podcast-env
   source podcast-env/bin/activate  # macOS/Linux
   podcast-env\Scripts\activate     # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Add your Mistral API key**

   Create a `.env` file in the project root:

   ```
   MISTRAL_API_KEY=your_api_key_here
   ```

   You can get a free API key at [console.mistral.ai](https://console.mistral.ai/).

5. **Run the app**

   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`.

### 💸 Cost

This project runs on Mistral's free tier and costs essentially nothing to use. A typical 45-minute podcast episode requires one transcription call (Voxtral Mini) and two chat calls (formatting + asset generation). All of these fall comfortably within the free tier limits for personal or low-volume use.

---

## 📁 Project structure

```
podcast-assets-generation/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env                # API key (not committed - add your own)
├── .gitignore
└── LICENSE
```

---

## 🤝 Contributing

Contributions are welcome. If you have ideas for new assets to generate, improvements to the prompts, or UI enhancements, feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to your fork and open a pull request

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Dr Ana Rojo-Echeburua
