"""Streamlit interface for the NLP-Based Spelling Correction System."""
from pathlib import Path

import streamlit as st

from spelling_corrector import SpellingCorrector, load_vocabulary

BASE_DIR = Path(__file__).resolve().parent
VOCABULARY_PATH = BASE_DIR / "data" / "vocabulary.txt"

st.set_page_config(page_title="NLP Spelling Correction", page_icon="✍️", layout="centered")
st.title("✍️ NLP-Based Spelling Correction System")
st.caption("Find likely spelling errors, review suggestions, and choose corrections yourself.")

try:
    vocabulary = load_vocabulary(VOCABULARY_PATH)
except FileNotFoundError as error:
    st.error(f"{error}. Please check that data/vocabulary.txt exists.")
    st.stop()

with st.sidebar:
    st.header("Settings")
    max_distance = st.slider("Maximum edit distance", min_value=1, max_value=4, value=2)
    custom_text = st.text_area("Add custom words", placeholder="One word per line, or separate with commas")
    for word in custom_text.replace(",", "\n").splitlines():
        if word.strip():
            vocabulary.add(word.strip().lower())
    st.caption(f"Vocabulary words: {len(vocabulary):,}")

corrector = SpellingCorrector(vocabulary, max_edit_distance=max_distance)
input_text = st.text_area("Enter a sentence or paragraph", height=180,
                          placeholder="For example: I definately recieved teh letter.", key="input_text")
check_col, clear_col = st.columns(2)
with check_col:
    check_clicked = st.button("Check spelling", type="primary", use_container_width=True)
with clear_col:
    if st.button("Clear text", use_container_width=True):
        st.session_state.pop("analysis", None)
        st.session_state["input_text"] = ""
        st.rerun()

if check_clicked:
    if not input_text.strip():
        st.warning("Please enter some text before checking spelling.")
        st.session_state.pop("analysis", None)
    else:
        st.session_state["analysis"] = corrector.check_text(input_text)

analysis = st.session_state.get("analysis")
if analysis:
    st.subheader("Original text")
    st.write(analysis["original_text"])
    errors = analysis["misspellings"]
    st.subheader("Detected misspellings")
    choices: dict[str, str] = {}
    if not errors:
        st.success("No words outside the vocabulary were found.")
    else:
        st.caption("Repeated occurrences are grouped together. Choose an alternative to use it.")
        for normalized, detail in errors.items():
            word = str(detail["word"])
            options = list(detail["suggestions"])
            st.markdown(f"**{word}** — found {detail['count']} time(s)")
            if options:
                selected = st.selectbox(f"Suggestions for {word}", ["Leave unchanged", *options],
                                        key=f"choice_{normalized}")
                if selected != "Leave unchanged":
                    choices[normalized] = selected
            else:
                st.info(f"No suggestion within edit distance {max_distance}; this word will remain unchanged.")
        st.subheader("Correction suggestions")
        for detail in errors.values():
            options_text = ", ".join(detail["suggestions"]) or "No reliable suggestion"
            st.write(f"**{detail['word']}** → {options_text}")
    corrected = corrector.correct_text(str(analysis["original_text"]), choices)
    st.subheader("Corrected text")
    st.text_area("Review your corrected text", value=corrected, height=140, key="corrected_preview")
    st.download_button("Download corrected text", data=corrected, file_name="corrected_text.txt",
                       mime="text/plain", use_container_width=True)

st.divider()
st.caption("Suggestions use character edits. Review choices: names, technical terms, and valid words may be flagged.")
