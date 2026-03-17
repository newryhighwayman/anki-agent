# Card Types

AnkiAgent creates 4 custom Anki note types, all sharing `styles.css`.

## AnkiAgent TargetToSource

Target language word on front, source language translations on back.

- Fields: `Word`, `IPA`, `AnswerCount`, `Translations`, `Image`
- Front: word + IPA + audio + image + "(N answers)" hint
- Back: all translations with examples

## AnkiAgent SourceToTarget

Source language word on front, target language translations on back.

- Fields: `Word`, `AnswerCount`, `Translations`, `Image`
- Front: word + "(N answers)" hint
- Back: target translations + IPA + audio + image

## AnkiAgent Grammar

Grammar rule on front, explanation on back.

- Fields: `Rule`, `Explanation`, `Example`, `IPA`, `Image`
- Front: rule + image
- Back: explanation + example + IPA + audio

## AnkiAgent Cloze

Cloze deletion card using `{{c1::word}}` syntax.

- Fields: `Text`, `Hint`, `IPA`, `Image`
- Front: text with blanks + hint + image
- Back: full text + IPA

## Multi-meaning merging

When multiple vocab entries share the same target word, they are merged into a single TargetToSource card showing all translations. Similarly, source words that map to multiple target words are merged into a single SourceToTarget card.
