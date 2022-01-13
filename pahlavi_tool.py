#!/usr/bin/env python
# coding: utf-8

# # Pahlavi Tool
# James Pickett

# In[45]:


#import relevant libraries

import os, re

import pandas as pd
from pandas import DataFrame, Series


# In[46]:


# general function in Pandas to set maximum number of rows; otherwise it abridges and only shows a few

pd.set_option('display.max_rows', 300)


# In[51]:


#set home directory path
hdir = os.path.expanduser('~')

#pahlavi corpus directory
pah_path = hdir + "/Dropbox/Active_Directories/Digital_Humanities/Corpora/pahlavi_corpus/"

#pickle path
pickle_path = hdir + "/Dropbox/Active_Directories/Digital_Humanities/Corpora/pickled_tokenized_cleaned_corpora"

# dataset path
ds_path = hdir + "/Dropbox/Active_Directories/Digital_Humanities/Datasets"


# ### Read-in Data

# In[126]:


#read in main corpus dataset
df_pahcorp = pd.read_csv (os.path.join(pickle_path,r'pahlavi_corpus.csv'))

#df_pahcorp.sample(5)


# In[68]:


#read in dictionary
## Format: UID, Transcription, Translit_Mac, Translit_Skj, New Persian

pahlavi_terms = pd.read_csv(ds_path + "/exported_database_data/pahlavi_terms.csv", names=['UID', 'Transcription',                                                 'Translit_Mac', 'Translit_Skj', 'New_Persian'])

## Format: UID, Term_ID, Definition
pahlavi_definitions = pd.read_csv(ds_path + "/exported_database_data/pahlavi_definitions.csv", names=['UID', 'Term_ID', 'Definition'])

#pahlavi_terms.sample(5)
#pahlavi_definitions.sample(5)


# In[128]:


# Joining Terms and Definitions

merged_pahdic = pd.merge(left=pahlavi_terms, right=pahlavi_definitions, how='left', left_on='UID', right_on='Term_ID')
#merged_pahdic.sample(5)


# ### Help Function

# In[167]:


def pah_help ():
    print ("Pahlavi Tool: Functions and Explanation\n\n           \tpah_def: returns the word-match's definition ordered by frequency value in the corpus\n           \tkwic_pah: key word in context function\n           \tfreq_dic: how often doses the term appear in the corpus\n           \tconfreq: bigram conditional frequency; optional 'group = True' argument organizes by text"
          )


# In[170]:


#pah_help()


# ----
# 
# ## Key Word in Context

# In[88]:


def index_kwic (term):
    
    """This function returns a dataframe filtered by the search term."""
    
    result = df_pahcorp[df_pahcorp['token'].str.match(term)]
    return result
    
    # str.match; the str part is telling match how to behave; .match is a method specific to pandas
    


# In[6]:


def kwic_pah (term):
    
    for i, item in index_kwic(term).iterrows():
        
        title = item["title"]
        line = item["line"]
        
        filtered = df_pahcorp[(df_pahcorp['title']==title)&(df_pahcorp['line']==line)]
        # equivalent syntax: df_pahcorp.query(f'title == "{title}" and line == {line}')
        
        filtered = filtered.sort_values("index")
        # probably already sorted, but better to be on the safe side
                
        text = " ".join(filtered["token"])
        
        print(f'{title}: {line}\n{text}\n')
        
        # task: figure out how to color code results; termcolor package, has to be installed



        
# iterrows(): research what this does exactly, has something to do with dataframes being composed of series
        


# In[89]:


#kwic_pah("p.d")


# ## Frequency

# In[121]:


freq_dic = pd.value_counts(df_pahcorp.token).to_frame().reset_index()
freq_dic.sample(5)


# In[100]:


def freq (term):
    query_mask = freq_dic["index"].str.contains(term, na=False)
    query = freq_dic[query_mask]
    result = query.head()
    return (result)


# In[104]:


#freq("p.d")


# In[165]:


# addiing the frequency data into the dictionary

# need to turn the transcribed word into a unique identifier (will lose some data):
merged_pahdic_clean = merged_pahdic.drop_duplicates(subset=['Transcription'], keep='first')

# merge with frequency data based on the unique identifier:
merged_pahdic_freq = pd.merge(left=merged_pahdic, right=freq_dic, how='left', left_on='Transcription', right_on='index')

# clean up for readability
cleaned_merged_pahdic_freq = merged_pahdic_freq.drop(columns=['UID_y', 'Term_ID', 'index']).rename(columns={'UID_x': 'UID', 'token': 'Frequency'})

#cleaned_merged_pahdic_freq.sample(5)

# ?? how to get rid of those decimal points / why did they enter in the first place?


# ### Get Definition with Frequency

# In[163]:


def pah_def (term):
    query_mask = cleaned_merged_pahdic_freq["Transcription"].str.contains(term, na=False)
    query = cleaned_merged_pahdic_freq[query_mask]
    result = query.sort_values('Frequency', ascending=False).head()
    return (result)
    
    


# In[166]:


#pah_def("p.d")


# ## Conditional Frequency

# In[110]:


def confreq (term, group=False):
    sel = df_pahcorp[df_pahcorp['token']==term].copy()
    sel['index_next'] = sel['index'] + 1
    sel = sel.join(
        df_pahcorp.set_index(['title', 'line', 'index'])['token'].rename('token_next'),
        on=['title', 'line', 'index_next']
    )
    # If there are only 1-frequency results, it will still show them;
    # but if there are enough higher frequency results, it will omit the 1-frequency results.
    result = sel['token_next'].value_counts()
    short_result = [(x,y) for x,y in result.items() if y > 1]
    if len(short_result) > 5:
        result = short_result
    # improvement: create a list of omitted words (e.g. ud, ī, etc.), and make a flag1=False
    # optional argument to omit them.
    
    if group == True:
        result = sel.groupby('title')['token_next'].value_counts().rename("count").reset_index()
    
    return (result)
    


# In[116]:


#confreq ('may', group = True)


# In[169]:


pah_help()

