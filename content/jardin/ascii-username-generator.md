---
title: "ascii-username-generator"
weight: 10
description: "A Python GUI that pulls words from a linguistic database covering 19 languages and turns them into ASCII-clean usernames. A side project that started as 'wouldn't it be cool to get a username in Basque' and ended as a small example of repurposing NLP infrastructure for a non-NLP task."
summary: "ASCII usernames in 19 languages."
tags: ["python", "tkinter", "nltk", "wordnet", "side-project"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
A Python desktop app that generates fresh usernames by pulling words from a dictionary covering 19 different languages.
{{< /lead >}}

## At a Glance

Most username generators feel the same after a few tries. They draw from a small English wordlist and lean on suffixes (`CoolGuy42`, `BlueBird07`) to manufacture variety that the underlying corpus does not actually provide. This tool takes a different approach: it draws words from a linguistic research database that already covers 19 languages, filters those words down to ones that are typeable on a standard US keyboard, and formats whatever survives.

The result is a generator that can suggest `kalakuva`, `vrijgevig`, `morgendag`, or `english_default_word_42` with similar ease, because the Finnish, Dutch, and Norwegian wordlists are just sitting there waiting to be queried.

## The Problem

A good username generator has to balance three things that pull against each other.

**Variety.** A pool of 5,000 English nouns runs out fast once you start filtering for length, profanity, and aesthetic appeal. You end up generating the same words over and over with different number suffixes.

**Typeability.** Users want usernames they can actually type on whatever keyboard they have in front of them. Pulling from a multilingual corpus means encountering ñ, ä, å, ø, ł, ç, ę, and dozens of other characters that most users would have to copy-paste rather than type.

**Appropriateness.** Generators that pull from a large corpus inevitably surface words that are slurs, profanity, or otherwise unsuitable. Filtering has to happen before output, not after the user complains.

Manual approaches to any one of these are tedious. Manual approaches to all three together are unworkable.

## The Approach

The tool is a single Tkinter desktop app that exposes three formatting choices (case, numeric suffix, batch size) and runs the actual word generation in a background thread so the UI never freezes.

The data source is the trick: rather than maintaining wordlists per language, the generator queries [NLTK](https://www.nltk.org/)'s Open Multilingual WordNet. This is a research database originally built for natural language processing tasks like translation and word-sense disambiguation, but it happens to be exactly what a multilingual username generator needs: a structured, vetted, freely-available corpus of nouns and concepts in dozens of languages.

The generation pipeline is short:

{{< mermaid >}}
flowchart TD
    A[User picks language and format] --> B[Pull all WordNet words for that language]
    B --> C[Filter: ASCII-only and length >= 3]
    C --> D[Filter: not in profanity blocklist]
    D --> E[Random selection]
    E --> F[Apply case and suffix formatting]
    F --> G[Display in clickable result table]
{{< /mermaid >}}

Each filter is independent and order-insensitive in correctness, but the order shown is also the order that minimizes wasted work. The ASCII filter cuts the candidate pool dramatically for non-English languages; running profanity matching on the full multilingual corpus first would do strictly more work to reach the same result.

## Walking Through the Generation

### The Word Source

WordNet exposes its data through *synsets*, which are groupings of words that share a meaning. The generator iterates every synset and pulls every lemma (a specific word in a specific language) attached to it:

```python
for synset in wordnet.all_synsets():
    for lemma in synset.lemmas(lang=lang_code):
        word = lemma.name()
        if word.isalnum():
            words.append(word)
```

The `isalnum()` check is the first cut: WordNet contains some compound entries with underscores (`big_cat`, `running_shoe`) that look strange as usernames. Filtering at this stage drops them before any further processing.

### The ASCII Filter

The filter that does most of the work is one line of code applied per word:

```python
return all(ord(c) < 128 for c in word) and len(word) >= min_len
```

A character's *ordinal* is its position in the Unicode table. The first 128 positions (0 through 127) are exactly the ASCII set: digits, English letters, and basic punctuation. Anything beyond 127 is something else: an accented vowel, a non-Latin script, an emoji, a control character.

For a Spanish word like `mañana`, the `ñ` has ordinal 241, so the word fails the filter and is dropped. For `manana` (no tilde), every character has an ordinal under 128, so it passes. This means the generator naturally surfaces words from non-English languages that happen to be writable in plain English letters: `kalakuva` (Finnish for "fish picture"), `pomoću` (Bosnian, would fail because of the ć), `enero` (Spanish for January, passes cleanly).

### Formatting

Once a word survives the filters, the formatting step applies the user's chosen case and numeric suffix:

```python
case = self.case_var.get()
if case == "lowercase":
    word = word.lower()
elif case == "uppercase":
    word = word.upper()
elif case == "capitalize":
    word = word.capitalize()

style = self.number_var.get()
if style == "1digit":
    word += str(random.randint(0, 9))
elif style == "2digit":
    word += f"{random.randint(0, 99):02d}"
elif style == "3digit":
    word += f"{random.randint(0, 999):03d}"
```

The format string `:02d` is doing real work here: it pads single-digit random numbers with a leading zero (so `7` becomes `07`), which keeps username lengths consistent. Without it, `kalakuva7` and `kalakuva42` would have different total lengths, which is a small inconsistency that reads as sloppy.

## Why WordNet

There are a dozen ways to build a username generator. Most of them involve curating wordlists by hand, scraping public corpora, or writing small grammars that combine adjectives and nouns. WordNet is none of those things, and using it for this task is a slight abuse of its intended purpose.

The reason it works: WordNet was built by linguists who needed a vetted, semantically-organized, multilingual database for serious research. The Open Multilingual WordNet extension links the original Princeton English WordNet to wordlists in dozens of other languages. The database is updated, hosted, version-controlled, and free. NLTK provides a Python interface that returns ready-to-use data with one method call.

For a side project, this means the entire "where do the words come from" problem is solved before the project starts. No wordlist maintenance. No language-by-language scraping. No copyright concerns. Just an iterator over `wordnet.all_synsets()` and a language code.

The aesthetic upside is that WordNet's words are, on average, more interesting than the curated wordlists that ship with most username generators. Linguistic research databases include obscure terms, archaic forms, and technical vocabulary that a hand-picked list would never include.

## Under The Hood

For the technically curious, three of the implementation pieces worth highlighting.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Language coverage via Open Multilingual WordNet" >}}

The 19 languages are not coded in by hand. They are queried from the same dataset using ISO 639-3 language codes:

```python
self.language_names: dict[str, str] = {
    "eng": "English",
    "spa": "Spanish",
    "fra": "French",
    "ita": "Italian",
    "por": "Portuguese",
    "nld": "Dutch",
    "pol": "Polish",
    "swe": "Swedish",
    "fin": "Finnish",
    "nno": "Norwegian Nynorsk",
    "nob": "Norwegian Bokmål",
    "ron": "Romanian",
    "slk": "Slovak",
    "slv": "Slovenian",
    "zsm": "Malay",
    "eus": "Basque",
    "cat": "Catalan",
    "dan": "Danish",
    "lit": "Lithuanian"
}
```

These are the languages that Open Multilingual WordNet covered with sufficient quality and coverage at the time of writing. The codes are passed straight through to `lemma.name(lang=lang_code)`, so adding a new language is a single dictionary entry once the upstream data exists.

A handful of the languages are interesting choices that survived the ASCII filter despite their native scripts using diacritics heavily. Norwegian Bokmål and Nynorsk both make the cut, despite the language using `æ`, `ø`, and `å`, because plenty of words in any language consist entirely of unmarked letters. The filter just lets those through and drops the rest.

{{< /accordionItem >}}

{{< accordionItem title="ASCII compliance through Unicode ordinals" >}}

The validation is one expression:

```python
@staticmethod
def is_valid_word(word: str, min_len: int = 3) -> bool:
    return all(ord(c) < 128 for c in word) and len(word) >= min_len
```

`ord()` returns the integer code point of a character. The ASCII range is exactly the first 128 code points: positions 0 through 127. By checking every character against that boundary in a single `all()` expression, the filter rejects any word containing accented characters, non-Latin scripts, emoji, or invisible control characters.

This is more reliable than approaches that try to identify and strip specific character classes (like Unicode normalization with `NFKD` followed by a regex). Those approaches need to know what to strip; this one just asks whether the result will be typeable on the keyboard the user already has.

The minimum length of 3 is a separate concern. WordNet contains many two-letter words in some languages that read more like abbreviations than nouns, and they make poor usernames. Three is the smallest length that consistently produces something a human would recognize as a word.

{{< /accordionItem >}}

{{< accordionItem title="Background-thread generation with a Tkinter-safe handoff" >}}

A common failure mode for desktop apps is freezing the UI during long operations. The generator avoids this by running the actual word fetching and filtering in a `threading.Thread` and reporting progress back to the GUI through Tkinter-safe primitives.

The interesting subtlety is that Tkinter widgets are not thread-safe: writing to a Tkinter Text widget from a non-main thread can corrupt internal state or crash the interpreter. The fix is to use the logging system as a buffer. A custom log handler captures records on whichever thread emits them, then schedules a Tkinter `after()` call to apply the update on the main thread:

```python
class TextHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        # schedule the actual widget update on the main thread
        self.text_widget.after(0, self._append, msg)
```

`after(0, ...)` is Tkinter's idiomatic "do this next time the event loop is idle" call. The 0 is a delay in milliseconds, but the practical effect is "as soon as you safely can." This pattern means the worker thread can call `logger.info("processing language X")` freely, and the GUI shows the messages as they arrive without ever crossing thread boundaries unsafely.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.6+
- **GUI:** tkinter (built into Python)
- **Word source:** [NLTK](https://www.nltk.org/) with Open Multilingual WordNet
- **Profanity filter:** [better-profanity](https://pypi.org/project/better-profanity/)
- **Clipboard:** [pyperclip](https://pypi.org/project/pyperclip/)
- **Concurrency:** `threading.Thread` with custom logging handler for thread-safe UI updates

## Repo

[github.com/hihipy/ascii-username-generator](https://github.com/hihipy/ascii-username-generator)
