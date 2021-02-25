#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os

import pandas as pd
from pandas import DataFrame, Series


# In[2]:


#set home directory path
hdir = os.path.expanduser('~')

#pahlavi corpus directory
pah_path = hdir + "/Dropbox/Active_Directories/Digital_Humanities/Corpora/pahlavi_corpus/"

#pickle path
pickle_path = hdir + "/Dropbox/Active_Directories/Digital_Humanities/Corpora/pickled_tokenized_cleaned_corpora"


# In[3]:


df_pahcorp = pd.read_csv (os.path.join(pickle_path,r'pahlavi_corpus.csv'))


# In[4]:


df_pahcorp.head()


# ----
# 
# ## Key Word in Context

# In[6]:


def index_kwic (term):
    
    """This function returns a dataframe filtered by the search term."""
    
    result = df_pahcorp[df_pahcorp['token'].str.match(term)]
    return result
    
    # str.match; the str part is telling match how to behave; .match is a method specific to pandas
    
    
# if can get it working, add regex functionality: 


# In[7]:


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
        


# In[7]:


#df_pahcorp["token"] == "afsōn"


# In[8]:


kwic_pah ("hāmōn")


# In[29]:


# Conditional frequency

# two problems: (1) find where the words are; (2) find what words are next to a particular location

# collect on i-1 i+1; counter is a function in the collections module that takes a list and turns it into a frequency dictionary
## A column is technically a series, which can work like a list.


# In[ ]:




