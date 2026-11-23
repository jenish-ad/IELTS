# TODO

- [ ] Flag likely hesitation within candidate answers using both aligned word duration and the gap before the next word. Start with short words whose aligned spans are unusually long compared with other instances of the same word, especially when followed by a gap inside an unfinished thought.
- [ ] For words with too few reliable repetitions, compare their aligned duration with the median for nearby candidate words with the same syllable count and a similar position in the phrase. Use a nearby pause or restart to help decide whether to flag the clip.
- [ ] Estimate English syllable counts with [`cmudict`](https://pypi.org/project/cmudict/). Strip surrounding punctuation and expand numbers as spoken before lookup. Count the vowel sounds marked with a stress digit (`0`, `1`, or `2`) in each pronunciation. “Sweden” has 2 syllables, “27” spoken as “twenty-seven” has 4, and “responsibilities” has 6. Skip the duration comparison if the lookup is missing, pronunciation variants disagree on the count, or too few comparable words are available. Keep nearby pauses and restarts as separate clues.
- [ ] Return the transcript excerpt and clip timestamps for each flag. Listen to flagged clips to distinguish a stretched word, a filler that WhisperX omitted, silence, or an alignment error.

## Example

In [`output/interview.json`](output/interview.json#L8293), the candidate says “I'm from Sweden and I'm 27 years old.” The aligned span for “and” is 2.522 seconds, compared with a median of 0.13 seconds for “and” in this transcript. The following gap is 0.88 seconds. The current pause metric captures the gap. Review 00:55.1–00:58.5 to check what the full hesitation sounds like.
