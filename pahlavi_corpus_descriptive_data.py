#!/usr/bin/env python3
"""
Pahlavi Corpus Data Analysis Tool
Functions for generating statistics and analysis from the indexed Pahlavi corpus
"""

import pandas as pd
import os
import inspect

# Set home directory path
hdir = os.path.expanduser('~')

# Define paths following project conventions
dh_path = '/Dropbox/Active_Directories/Digital_Humanities/'
corpus_path = os.path.join(hdir, dh_path.strip('/'), 'Corpora/pickled_tokenized_cleaned_corpora/pahlavi_corpus.csv')
output_path = os.path.join(hdir, dh_path.strip('/'), 'Datasets/pahlavi_corpus_descriptive_data')

# Check if corpus file exists
if not os.path.exists(corpus_path):
    raise FileNotFoundError(f"Corpus file not found at: {corpus_path}")

# Load the corpus
print("📚 Loading Pahlavi corpus...")
df = pd.read_csv(corpus_path, encoding='utf-8')
print(f"✅ Loaded {len(df):,} entries")

# Display basic info about the dataframe
print(f"\n📊 Corpus Overview:")
print(f"DataFrame shape: {df.shape}")
print(f"Columns: {list(df.columns)}")


def frequency_dict(sort_by='frequency', ascending=False):
    """
    Create a frequency dictionary of all tokens in the corpus.
    
    Args:
        sort_by (str): Sort by 'frequency' (default) or 'word' (alphabetical)
        ascending (bool): Sort order - False for descending (default), True for ascending
    
    Returns:
        DataFrame: Two columns - 'word' and 'frequency'
    
    Example:
        freq_df = frequency_dict()  # Most frequent words first
        freq_df = frequency_dict(sort_by='word')  # Alphabetical order
        freq_df = frequency_dict(ascending=True)  # Least frequent first
    """
    # Count occurrences of each unique token
    # SQL equivalent: SELECT token AS word, COUNT(*) AS frequency FROM df GROUP BY token
    freq_counts = df['token'].value_counts()
    
    # Convert to DataFrame with named columns
    freq_df = pd.DataFrame({
        'word': freq_counts.index,
        'frequency': freq_counts.values
    })
    
    # Sort based on user preference
    if sort_by == 'word':
        freq_df = freq_df.sort_values('word', ascending=ascending)
    else:  # sort by frequency (default)
        freq_df = freq_df.sort_values('frequency', ascending=ascending)
    
    # Reset index to have clean row numbers
    freq_df = freq_df.reset_index(drop=True)
    
    print(f"\n📊 Frequency Dictionary Generated:")
    print(f"Total unique tokens: {len(freq_df):,}")
    print(f"Total token instances: {freq_df['frequency'].sum():,}")
    print(f"\nTop 10 most frequent tokens:")
    print(freq_df.head(10).to_string(index=False))
    
    return freq_df


def conditional_frequency_dict(sort_by='frequency', ascending=False):
    """
    Create a conditional frequency dictionary of word pairs (bigrams) in the corpus.
    
    Args:
        sort_by (str): Sort by 'frequency' (default), 'first_word', or 'second_word'
        ascending (bool): Sort order - False for descending (default), True for ascending
    
    Returns:
        DataFrame: Three columns - 'first_word', 'second_word', 'frequency'
                   Only includes pairs that occur more than once (frequency > 1)
    
    Example:
        bigram_df = conditional_frequency_dict()  # Most frequent pairs first
        bigram_df = conditional_frequency_dict(sort_by='first_word')  # Alphabetical by first word
    """
    # Create columns for the current token and the next token
    # This "shifts" the token column up by one row to create pairs
    df_bigrams = df.copy()
    df_bigrams['next_token'] = df_bigrams['token'].shift(-1)
    
    # Remove pairs that cross line boundaries or text boundaries
    # (where title or line changes between consecutive tokens)
    df_bigrams['same_context'] = (
        (df_bigrams['title'] == df_bigrams['title'].shift(-1)) &
        (df_bigrams['line'] == df_bigrams['line'].shift(-1))
    )
    
    # Filter to only valid pairs (same context)
    valid_pairs = df_bigrams[df_bigrams['same_context']].copy()
    
    # Count occurrences of each word pair
    # SQL equivalent: SELECT token AS first_word, next_token AS second_word, COUNT(*) AS frequency
    #                 FROM valid_pairs 
    #                 GROUP BY token, next_token
    #                 HAVING COUNT(*) > 1
    pair_counts = valid_pairs.groupby(['token', 'next_token']).size()
    
    # Convert to DataFrame
    bigram_df = pd.DataFrame({
        'first_word': [pair[0] for pair in pair_counts.index],
        'second_word': [pair[1] for pair in pair_counts.index],
        'frequency': pair_counts.values
    })
    
    # Drop pairs that only occur once
    bigram_df = bigram_df[bigram_df['frequency'] > 1]
    
    # Drop pairs containing function words in either position
    # SQL equivalent: WHERE first_word NOT IN ('ud', 'ī', ...) AND second_word NOT IN ('ud', 'ī', ...)
    stopwords = ['ud', 'ī', 'ō', 'ēn', 'kū', '∵', 'o', 'kē', 'bē', 'pad', 'ēw', 'ān', 'az', 'nē']
    bigram_df = bigram_df[
        ~bigram_df['first_word'].isin(stopwords) &
        ~bigram_df['second_word'].isin(stopwords)
    ]
    
    # Sort based on user preference
    if sort_by == 'first_word':
        bigram_df = bigram_df.sort_values('first_word', ascending=ascending)
    elif sort_by == 'second_word':
        bigram_df = bigram_df.sort_values('second_word', ascending=ascending)
    else:  # sort by frequency (default)
        bigram_df = bigram_df.sort_values('frequency', ascending=ascending)
    
    # Reset index
    bigram_df = bigram_df.reset_index(drop=True)
    
    print(f"\n📊 Conditional Frequency Dictionary (Bigrams) Generated:")
    print(f"Total unique word pairs (freq > 1): {len(bigram_df):,}")
    print(f"Total bigram instances: {bigram_df['frequency'].sum():,}")
    print(f"\nTop 10 most frequent word pairs:")
    print(bigram_df.head(10).to_string(index=False))
    
    return bigram_df


def phrases(min_frequency=5, sort_by='frequency', ascending=False):
    """
    Find phrases (trigrams) that appear in the corpus.
    
    Args:
        min_frequency (int): Minimum number of occurrences (default: 5)
        sort_by (str): Sort by 'frequency' (default), 'first_word', 'second_word', or 'third_word'
        ascending (bool): Sort order - False for descending (default), True for ascending
    
    Returns:
        DataFrame: Four columns - 'first_word', 'second_word', 'third_word', 'frequency'
                   Only includes phrases that occur at least min_frequency times
    
    Example:
        phrases_df = phrases()  # Phrases occurring 5+ times
        phrases_df = phrases(min_frequency=10)  # Phrases occurring 10+ times
    """
    # Create columns for current token, next token, and token after that
    df_trigrams = df.copy()
    df_trigrams['next_token'] = df_trigrams['token'].shift(-1)
    df_trigrams['third_token'] = df_trigrams['token'].shift(-2)
    
    # Remove phrases that cross line or text boundaries
    df_trigrams['same_context'] = (
        (df_trigrams['title'] == df_trigrams['title'].shift(-1)) &
        (df_trigrams['line'] == df_trigrams['line'].shift(-1)) &
        (df_trigrams['title'] == df_trigrams['title'].shift(-2)) &
        (df_trigrams['line'] == df_trigrams['line'].shift(-2))
    )
    
    # Filter to only valid phrases (same context)
    valid_phrases = df_trigrams[df_trigrams['same_context']].copy()
    
    # Count occurrences of each three-word phrase
    # SQL equivalent: SELECT token, next_token, third_token, COUNT(*) AS frequency
    #                 FROM valid_phrases
    #                 GROUP BY token, next_token, third_token
    #                 HAVING COUNT(*) >= min_frequency
    phrase_counts = valid_phrases.groupby(['token', 'next_token', 'third_token']).size()
    
    # Convert to DataFrame
    phrases_df = pd.DataFrame({
        'first_word': [phrase[0] for phrase in phrase_counts.index],
        'second_word': [phrase[1] for phrase in phrase_counts.index],
        'third_word': [phrase[2] for phrase in phrase_counts.index],
        'frequency': phrase_counts.values
    })
    
    # Filter by minimum frequency
    phrases_df = phrases_df[phrases_df['frequency'] >= min_frequency]
    
    # Exclude phrases containing '∵' in any position
    phrases_df = phrases_df[
        (phrases_df['first_word'] != '∵') &
        (phrases_df['second_word'] != '∵') &
        (phrases_df['third_word'] != '∵')
    ]
    
    # Sort based on user preference
    if sort_by == 'first_word':
        phrases_df = phrases_df.sort_values('first_word', ascending=ascending)
    elif sort_by == 'second_word':
        phrases_df = phrases_df.sort_values('second_word', ascending=ascending)
    elif sort_by == 'third_word':
        phrases_df = phrases_df.sort_values('third_word', ascending=ascending)
    else:  # sort by frequency (default)
        phrases_df = phrases_df.sort_values('frequency', ascending=ascending)
    
    # Reset index
    phrases_df = phrases_df.reset_index(drop=True)
    
    print(f"\n📊 Phrases (Trigrams) Generated:")
    print(f"Total unique phrases (freq >= {min_frequency}): {len(phrases_df):,}")
    print(f"Total phrase instances: {phrases_df['frequency'].sum():,}")
    print(f"\nTop 10 most frequent phrases:")
    print(phrases_df.head(10).to_string(index=False))
    
    return phrases_df


def generate_all_datasets():
    """
    Generate all three datasets (frequency dictionary, conditional frequency, phrases)
    and save them as CSV files.
    
    Saves to: ~/Dropbox/Active_Directories/Digital_Humanities/Datasets/pahlavi_corpus_descriptive_data/
    Files: pah_freqdic.csv, pah_con_freq.csv, pah_phrases.csv
    
    Returns:
        dict: Paths to the three saved files
    
    Example:
        paths = generate_all_datasets()
    """
    print("\n" + "=" * 70)
    print("🔄 GENERATING ALL DATASETS")
    print("=" * 70)
    
    # Check if output directory exists, create if not
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"✅ Created output directory: {output_path}")
    
    # Generate frequency dictionary
    print("\n1️⃣  Generating Frequency Dictionary...")
    freq_df = frequency_dict()
    freq_path = os.path.join(output_path, 'pah_freqdic.csv')
    freq_df.to_csv(freq_path, index=False, encoding='utf-8')
    print(f"✅ Saved to: {freq_path}")
    
    # Generate conditional frequency dictionary (bigrams)
    print("\n2️⃣  Generating Conditional Frequency Dictionary (Bigrams)...")
    bigram_df = conditional_frequency_dict()
    bigram_path = os.path.join(output_path, 'pah_con_freq.csv')
    bigram_df.to_csv(bigram_path, index=False, encoding='utf-8')
    print(f"✅ Saved to: {bigram_path}")
    
    # Generate phrases (trigrams)
    print("\n3️⃣  Generating Phrases (Trigrams)...")
    phrases_df = phrases()
    phrases_path = os.path.join(output_path, 'pah_phrases.csv')
    phrases_df.to_csv(phrases_path, index=False, encoding='utf-8')
    print(f"✅ Saved to: {phrases_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ ALL DATASETS GENERATED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nFiles saved to: {output_path}")
    print(f"  • pah_freqdic.csv ({len(freq_df):,} entries)")
    print(f"  • pah_con_freq.csv ({len(bigram_df):,} entries)")
    print(f"  • pah_phrases.csv ({len(phrases_df):,} entries)")
    
    # Return paths
    return {
        'frequency_dict': freq_path,
        'conditional_freq': bigram_path,
        'phrases': phrases_path
    }


# Display available functions
print("\n" + "=" * 70)
print("📚 AVAILABLE FUNCTIONS")
print("=" * 70)

# Get all functions defined in this module
import sys
current_module = sys.modules[__name__]
functions = [name for name in dir(current_module) 
             if callable(getattr(current_module, name)) and not name.startswith('_')]

for func_name in functions:
    func = getattr(current_module, func_name)
    
    # Get function signature
    try:
        sig = inspect.signature(func)
        func_signature = f"{func_name}{sig}"
    except:
        func_signature = f"{func_name}()"
    
    # Get docstring
    docstring = func.__doc__
    if docstring:
        first_line = docstring.strip().split('\n')[0]
        print(f"   • {func_signature}")
        print(f"     {first_line}")
    else:
        print(f"   • {func_signature}")

print("=" * 70)