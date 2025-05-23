import re

def summarize_text(text, max_summary_sentences=3):
    """
    Generates a mock summary of the input text.
    It takes the first `max_summary_sentences` sentences.
    """
    # TODO: Replace with actual AI summarization call

    if not text or not text.strip():
        return "Content too short to summarize."

    # Split into sentences. This is a simple regex and might not cover all edge cases.
    # It splits after a period, exclamation mark, or question mark followed by one or more spaces.
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    # Filter out any empty strings that might result from multiple spaces after punctuation
    sentences = [s for s in sentences if s.strip()]

    if not sentences:
         return "Content too short to summarize."

    if len(sentences) <= max_summary_sentences:
        # If the text has fewer or equal sentences than max_summary_sentences, return the whole text
        summary = ' '.join(sentences)
    else:
        # Otherwise, take the first max_summary_sentences
        summary = ' '.join(sentences[:max_summary_sentences])
    
    # Ensure the summary ends with appropriate punctuation if the last sentence of the summary had it.
    # This is a simplified approach.
    if summary:
        last_sentence_in_summary_index = min(len(sentences), max_summary_sentences) -1
        original_last_sentence = sentences[last_sentence_in_summary_index]
        if original_last_sentence[-1] in '.!?':
            if not summary.endswith(('.', '!', '?')):
                 summary += original_last_sentence[-1]
        # If the original last sentence didn't end with punctuation, ensure the summary doesn't artificially add one from a previous sentence.
        # This case is mostly handled by the join, but good to be mindful.
        # A more robust way would be to rejoin and then ensure the final char is correct.

    return summary if summary.strip() else "Could not generate a summary."

if __name__ == '__main__':
    # Example Usage:
    sample_text_1 = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence, which should be excluded. And a fifth one!"
    sample_text_2 = "This is a short text."
    sample_text_3 = "Only one sentence here."
    sample_text_4 = ""
    sample_text_5 = "First sentence. Second. Third. Fourth. Fifth."
    sample_text_6 = "Sentence one. Sentence two! Sentence three? Sentence four."

    print(f"Original: '{sample_text_1}'\nSummary: '{summarize_text(sample_text_1)}'\n")
    print(f"Original: '{sample_text_2}'\nSummary: '{summarize_text(sample_text_2)}'\n")
    print(f"Original: '{sample_text_3}'\nSummary: '{summarize_text(sample_text_3, 5)}'\n") # Test with max_sentences > actual
    print(f"Original: '{sample_text_4}'\nSummary: '{summarize_text(sample_text_4)}'\n")
    print(f"Original: '{sample_text_5}'\nSummary: '{summarize_text(sample_text_5, 2)}'\n")
    print(f"Original: '{sample_text_6}'\nSummary: '{summarize_text(sample_text_6, 3)}'\n")
    print(f"Original: '    '\nSummary: '{summarize_text('    ')}'\n") # Test with whitespace only
    print(f"Original: 'Hello world'\nSummary: '{summarize_text('Hello world')}'\n") # No standard punctuation
