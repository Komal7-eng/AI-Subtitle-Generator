import streamlit as st
import whisper
import tempfile
import os
import os
os.environ["PATH"] += r";C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"


st.set_page_config(page_title="AI Subtitle Generator", page_icon="🎬")
st.title("AI Subtitle Generator")
st.write("Built by a VFX Compositor | Upload video → get subtitles instantly")

model_size = st.selectbox("Select model size", ["tiny", "base", "small"], index=1)
st.caption("tiny = fastest, small = most accurate")

uploaded_file = st.file_uploader("Upload a video or audio file", 
    type=["mp4", "mov", "avi", "mp3", "wav", "m4a"])

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_srt(segments):
    srt = ""
    for i, seg in enumerate(segments, 1):
        start = format_time(seg['start'])
        end = format_time(seg['end'])
        text = seg['text'].strip()
        srt += f"{i}\n{start} --> {end}\n{text}\n\n"
    return srt

if uploaded_file is not None:
    st.info(f"File uploaded: {uploaded_file.name}")
    
    if st.button("Generate Subtitles"):
        with tempfile.NamedTemporaryFile(delete=False, 
            suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        with st.spinner(f"Loading Whisper {model_size} model..."):
            model = whisper.load_model(model_size)

        with st.spinner("Transcribing... please wait"):
            result = model.transcribe(tmp_path)

        srt_content = generate_srt(result['segments'])

        st.success("Done! Subtitles generated.")
        
        st.subheader("Preview")
        st.text_area("Subtitle content", srt_content, height=200)

        st.download_button(
            label="Download .srt file",
            data=srt_content,
            file_name=uploaded_file.name.rsplit('.', 1)[0] + ".srt",
            mime="text/plain"
        )

        st.subheader("Full transcript")
        st.write(result['text'])

        os.unlink(tmp_path)
else:
    st.info("Upload a video or audio file to generate subtitles")