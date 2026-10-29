import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from spelling_corrector import SpellingCorrector, levenshtein_distance, load_vocabulary

VOCABULARY = load_vocabulary(PROJECT_DIR / "data" / "vocabulary.txt")


def make_corrector(max_distance=2):
    return SpellingCorrector(VOCABULARY, max_edit_distance=max_distance)


def test_edit_distance_examples():
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("", "abc") == 3


def test_correctly_spelled_words_have_no_suggestions():
    corrector = make_corrector()
    assert corrector.suggestions("language") == []
    assert corrector.check_text("The language is useful.")["misspellings"] == {}


def test_common_spelling_errors():
    corrector = make_corrector()
    assert "receive" in corrector.suggestions("recieve")
    assert "the" in corrector.suggestions("teh")
    assert "definitely" in corrector.suggestions("definately")


def test_unknown_word_and_repeated_errors_are_grouped():
    errors = make_corrector().check_text("blorf blorf")["misspellings"]
    assert list(errors) == ["blorf"]
    assert errors["blorf"]["count"] == 2


def test_empty_input():
    assert make_corrector().check_text("")["misspellings"] == {}


def test_capitalization_and_punctuation_are_preserved():
    corrector = make_corrector()
    corrected = corrector.correct_text("I recieved teh letter!", {"recieved": "received", "teh": "the"})
    assert corrected == "I received the letter!"
    assert corrector.correct_text("TEH, teh.", {"teh": "the"}) == "THE, the."


def test_multiple_errors_in_a_sentence():
    errors = make_corrector().check_text("I definately recieved teh letter.")["misspellings"]
    assert set(errors) == {"definately", "recieved", "teh"}


def test_no_suitable_suggestions_leaves_word_unchanged():
    corrector = make_corrector(max_distance=1)
    assert corrector.suggestions("qzxvplm") == []
    assert corrector.correct_text("qzxvplm!", {"qzxvplm": ""}) == "qzxvplm!"


def test_custom_word_is_recognized():
    corrector = SpellingCorrector(VOCABULARY | {"codexword"})
    assert corrector.check_text("Codexword works.")["misspellings"] == {}
