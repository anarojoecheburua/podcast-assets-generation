import os
import tempfile

import streamlit as st
from dotenv import load_dotenv
from mistralai.client.sdk import Mistral
from mistralai.client.models.file import File

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
TRANSCRIPTION_MODEL = "voxtral-mini-2507"
CHAT_MODEL = "mistral-medium-latest"


def get_client():
    if not MISTRAL_API_KEY:
        st.error("MISTRAL_API_KEY not found. Add it to your .env file.")
        st.stop()
    return Mistral(api_key=MISTRAL_API_KEY)


def transcribe_audio(client: Mistral, audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.complete(
            model=TRANSCRIPTION_MODEL,
            file=File(fileName="audio.mp3", content=f, content_type="audio/mpeg"),
            timeout_ms=600_000,  # 10 minutes
        )
    return format_transcript(client, response.text)


def format_transcript(client: Mistral, text: str) -> str:
    response = client.chat.complete(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": f"""The following is a raw podcast transcript with no paragraph breaks.
Reformat it by adding paragraph breaks to make it readable.
Start a new paragraph when the speaker changes or when there is a clear shift in topic.
Do not change any words, correct any text, or add anything — only add paragraph breaks.
Return only the reformatted transcript, nothing else.

TRANSCRIPT:
{text}"""}],
        timeout_ms=300_000,
    )
    return response.choices[0].message.content.strip()


def generate_assets(client: Mistral, transcript: str) -> dict:
    prompt = f"""You are a podcast content strategist. Based on the transcript below, generate the following assets:

1. SUMMARY: A concise 3-5 sentence summary of the episode.
2. YOUTUBE_TITLES: Exactly 5 compelling YouTube title options (numbered 1-5).
3. YOUTUBE_DESCRIPTION: A full YouTube description (2-4 paragraphs) with relevant keywords naturally included.
4. KEY_MOMENTS: Exactly 8 bullet points highlighting the key moments or insights from the episode. Each moment must be on its own separate line.

Formatting rules (follow strictly):
- Do NOT use em dashes (—) or en dashes (–). Use a regular hyphen (-) instead.
- Do NOT add extra headers or commentary outside the markers below.

Format your response exactly like this:
---SUMMARY---
<summary here>

---YOUTUBE_TITLES---
1. <title 1>
2. <title 2>
3. <title 3>
4. <title 4>
5. <title 5>

---YOUTUBE_DESCRIPTION---
<description here>

---KEY_MOMENTS---
• <moment 1>
• <moment 2>
• <moment 3>
• <moment 4>
• <moment 5>
• <moment 6>
• <moment 7>
• <moment 8>

TRANSCRIPT:
{transcript}"""

    response = client.chat.complete(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        timeout_ms=300_000,
    )
    return parse_assets(response.choices[0].message.content)


def parse_assets(raw: str) -> dict:
    import re

    sections = {
        "summary": "",
        "youtube_titles": "",
        "youtube_description": "",
        "key_moments": "",
        "raw": raw,
    }

    # Each tuple: (section key, regex that matches the header line regardless of surrounding punctuation)
    marker_map = [
        ("summary",           r"SUMMARY"),
        ("youtube_titles",    r"YOUTUBE[_\s]TITLES?"),
        ("youtube_description", r"YOUTUBE[_\s]DESCRIPTION"),
        ("key_moments",       r"KEY[_\s]MOMENTS?"),
    ]

    # Match marker on its own line so trailing [^\w\n]* doesn't eat into the content below
    found = []
    for key, pattern in marker_map:
        m = re.search(rf"(?m)^[^\w\n]*{pattern}[^\w\n]*$", raw, re.IGNORECASE)
        if m:
            found.append((m.start(), m.end(), key))

    found.sort()  # ensure they're in order of appearance

    for i, (start, end, key) in enumerate(found):
        next_start = found[i + 1][0] if i + 1 < len(found) else len(raw)
        sections[key] = clean(raw[end:next_start].strip())

    return sections


def clean(text: str) -> str:
    text = text.replace("\u2014", "-")  # em dash
    text = text.replace("\u2013", "-")  # en dash
    return text.strip()


# --- UI ---

st.set_page_config(page_title="Podcast Assets Generator", page_icon="🎙️", layout="wide")
st.title("🎙️ Podcast Assets Generator")
st.caption("Upload an MP3 to transcribe and generate YouTube-ready content assets.")

uploaded_file = st.file_uploader("Upload your podcast MP3", type=["mp3"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")

    if st.button("Generate Assets", type="primary"):
        client = get_client()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            with st.status("Transcribing audio...", expanded=True) as status:
                transcript = transcribe_audio(client, tmp_path)
                status.update(label="Formatting transcript...", state="running")
                status.update(label="Generating assets...", state="running")
                assets = generate_assets(client, transcript)
                status.update(label="Done!", state="complete")

            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["Summary", "YouTube Titles", "YouTube Description", "Key Moments", "Full Transcript"]
            )

            parsed_ok = all(assets[k] for k in ("summary", "youtube_titles", "youtube_description", "key_moments"))

            with tab1:
                st.subheader("Episode Summary")
                st.markdown(assets["summary"] if assets["summary"] else assets["raw"])

            with tab2:
                st.subheader("YouTube Title Options")
                st.markdown(assets["youtube_titles"] if assets["youtube_titles"] else assets["raw"])

            with tab3:
                st.subheader("YouTube Description")
                st.markdown(assets["youtube_description"] if assets["youtube_description"] else assets["raw"])

            with tab4:
                st.subheader("Key Moments")
                st.markdown(assets["key_moments"] if assets["key_moments"] else assets["raw"])

            if not parsed_ok:
                st.warning("Could not parse all sections - showing full model output in each tab above.")

            with tab5:
                st.subheader("Full Transcript")
                st.markdown(transcript)

        finally:
            os.unlink(tmp_path)
