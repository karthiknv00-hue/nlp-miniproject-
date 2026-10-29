# NLP-Based Spelling Correction System

A beginner-friendly Python mini project that checks text against a local English vocabulary and ranks likely corrections with Levenshtein edit distance. The Streamlit page keeps corrections under the user's control.

## Problem statement

Typing mistakes can make short passages harder to read. This application identifies words that are not in its local vocabulary and offers nearby words as possible corrections. It is a demonstration, not a full grammar or context-aware spell checker.

## Objectives

- Tokenize text while retaining original punctuation and spacing.
- Find words missing from a configurable vocabulary.
- Rank up to five candidates by character edit distance.
- Group repeated errors and allow manual selection of alternatives.
- Preserve capitalization and provide corrected text for download.

## Abstract

The project scans input into word spans, checks each token against a lowercase vocabulary, and compares unknown words with vocabulary candidates using Levenshtein distance. Candidates within a configurable maximum distance are ranked and displayed. The user can select a candidate; words without a close match remain untouched.

## Software and hardware requirements

Software: Python 3.9 or newer, pip, and a modern browser. Python packages are listed in `requirements.txt` (Streamlit for the interface and pytest for tests).

Hardware: a computer capable of running Python and a browser. No GPU or network connection is needed after packages are installed.

## NLP methodology and algorithm

1. **Tokenization:** a regular expression locates English words, including contractions. Characters between word spans are not modified.
2. **Vocabulary lookup:** compare each token in lowercase with `data/vocabulary.txt` and words entered in the sidebar.
3. **Misspelling detection:** collect unknown words once and count repeated appearances.
4. **Candidate generation:** skip vocabulary entries whose lengths differ by more than the configured maximum distance.
5. **Distance and ranking:** calculate Levenshtein distance with dynamic programming and keep candidates within the limit. A likely adjacent-letter swap is surfaced prominently; the remaining candidates are ranked by distance and alphabetically. At most five are shown.
6. **Correction:** apply only alternatives selected by the user. Preserve capitalization and punctuation; leave the rest untouched.

The default maximum edit distance is 2. Increasing it can produce more candidates and more false suggestions. Vocabulary membership alone cannot tell whether a correctly spelled word suits its context.

## Project architecture

```text
Spelling_Correction_NLP/
├── app.py                         # Streamlit interface
├── spelling_corrector.py          # NLP logic and edit distance
├── requirements.txt
├── README.md
├── data/
│   └── vocabulary.txt              # Local editable word list
└── tests/
    └── test_spelling_corrector.py  # Pytest checks
```

## Installation and execution

Open a terminal in this project directory. Install the listed packages if needed:

```bash
python -m pip install -r requirements.txt
```

Run the app:

```bash
python -m streamlit run app.py
```

Enter text, set the edit distance, and optionally add custom words in the sidebar. Click **Check spelling**, review suggestions, and select replacements. Use **Download corrected text** to save the displayed result. **Clear text** resets the analysis.

Run tests from the project directory:

```bash
python -m pytest -q
```

## Example input and output

Input:

```text
I definately recieved teh letter!
```

Likely suggestions include `definitely`, `received`, and `the`. Selecting them yields:

```text
I definitely received the letter!
```

## Testing

The pytest suite covers edit distance, correctly spelled words, the requested typos, unknown and repeated words, empty input, punctuation and capitalization, multiple mistakes, custom vocabulary, and words with no suitable suggestion.

## Limitations

- Valid names, specialist terms, and uncommon words can be flagged if absent from the local list.
- Edit distance does not understand sentence meaning; a correctly spelled but misused word is not detected.
- Ranking uses edit distance and alphabetical tie-breaking, not word frequency or context.
- English-only tokenization is used; contractions count as one word.

## Future enhancements

- Add word frequency and contextual language models for better ranking.
- Support multiple languages, dictionary management, and larger open word lists.
- Add saved custom dictionaries, accessibility improvements, and a richer history view.
