#!/usr/bin/env python3
"""
Pahlavi Corpus Navigation Tool
Functions for searching and analyzing the indexed Pahlavi text corpus
"""

import pandas as pd
import re
import os
import inspect
from datetime import datetime

# Set home directory path
hdir = os.path.expanduser('~')

# Define paths following project conventions
dh_path = '/Dropbox/Active_Directories/Digital_Humanities/'
corpus_path = os.path.join(hdir, dh_path.strip('/'), 'Corpora/pickled_tokenized_cleaned_corpora/pahlavi_corpus.csv')
inbox_path = os.path.join(hdir, 'Dropbox/Active_Directories/Inbox')

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
print(f"\nFirst few rows:")
print(df.head())


def kwic(pattern, case_sensitive=False, save_report=False):
    """
    Keyword in Context (KWIC) search - displays full lines containing matching tokens.
    
    Args:
        pattern (str): Regex pattern to search for in the token column
        case_sensitive (bool): Whether search should be case-sensitive (default: False)
        save_report (bool): If True, saves results to a markdown file in Inbox (default: False)
    
    Returns:
        str or None: Path to saved report if save_report=True, otherwise None
    
    Example:
        kwic('mār')  # Find all lines containing tokens matching 'mār'
        kwic('mār.*')  # Find tokens starting with 'mār'
        kwic('mār', save_report=True)  # Save results to markdown file
    """
    # Set regex flags
    flags = 0 if case_sensitive else re.IGNORECASE
    
    # Find all rows where token matches the pattern
    mask = df['token'].str.contains(pattern, regex=True, na=False, flags=flags)
    matching_rows = df[mask]
    
    if len(matching_rows) == 0:
        print(f"❌ No matches found for pattern: '{pattern}'")
        return None
    
    print(f"\n🔍 KWIC Search Results for: '{pattern}'")
    print(f"Found {len(matching_rows):,} matching tokens\n")
    
    # Get unique combinations of title and line that contain matches
    unique_contexts = matching_rows[['title', 'line']].drop_duplicates()
    
    # Check if results are too long and save_report is False
    if len(unique_contexts) > 50 and not save_report:
        print(f"⚠️  {len(unique_contexts):,} results found (more than 50)")
        print("\nOptions:")
        print("  (1) Display 10 results at random")
        print("  (2) Save markdown report without displaying")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            # Sample 10 random results
            unique_contexts = unique_contexts.sample(n=10, random_state=None)
            print(f"\n📊 Displaying 10 random results out of {len(matching_rows):,} total matches")
        elif choice == "2":
            # Save report without displaying
            save_report = True
            print(f"\n💾 Generating report...")
        else:
            print("❌ Invalid choice. Exiting.")
            return None
    
    print("=" * 80)
    
    # Prepare markdown content if saving
    if save_report:
        markdown_content = f"# Pahlavi Corpus KWIC Search Report\n\n"
        markdown_content += f"**Search Pattern:** `{pattern}`\n\n"
        markdown_content += f"**Case Sensitive:** {case_sensitive}\n\n"
        markdown_content += f"**Total Matching Tokens:** {len(matching_rows):,}\n\n"
        markdown_content += f"**Total Lines with Matches:** {len(unique_contexts):,}\n\n"
        markdown_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown_content += "---\n\n"
    
    # For each unique context (title + line combination)
    for idx, (title, line) in unique_contexts.iterrows():
        # Get ALL tokens from that title and line
        # Sort by index to maintain token order (assuming data is pre-sorted)
        line_tokens = df[(df['title'] == title) & (df['line'] == line)].sort_index()
        
        # Build the line as a string
        tokens_list = line_tokens['token'].tolist()
        line_text = ' '.join(tokens_list)
        
        # Highlight the matching token(s) with **bold** markdown
        highlighted_text = re.sub(
            f'({pattern})',
            r'**\1**',
            line_text,
            flags=flags
        )
        
        # Print the result (unless only saving report)
        if not save_report or len(unique_contexts) <= 50:
            print(f"\n📖 {title} (line {line})")
            print(f"   {highlighted_text}")
        
        # Add to markdown if saving
        if save_report:
            markdown_content += f"## {title} (line {line})\n\n"
            markdown_content += f"{highlighted_text}\n\n"
            markdown_content += "---\n\n"
    
    if not save_report or len(unique_contexts) <= 50:
        print("\n" + "=" * 80)
        print(f"📊 Total: {len(unique_contexts):,} lines containing matches")
    
    # Save report if requested
    if save_report:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"pahlavi_kwic_report_{timestamp}.md"
        full_path = os.path.join(inbox_path, report_filename)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"\n✅ Report saved to: {full_path}")
        return full_path
    
    return None


# Display available functions
print("\n" + "=" * 70)
print("📚 AVAILABLE FUNCTIONS")
print("=" * 70)

# Get all functions defined in this module
import sys

# Try to get current module, with fallback
try:
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
except Exception as e:
    # If function listing fails, just show the main function
    print(f"   • kwic(pattern, case_sensitive=False, save_report=False)")
    print(f"     Keyword in Context (KWIC) search - displays full lines containing matching tokens.")

print("=" * 70)