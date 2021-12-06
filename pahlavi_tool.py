#!/usr/bin/env python
# coding: utf-8

# In[13]:


import os, re

import pandas as pd
from pandas import DataFrame, Series


# In[6]:


#set home directory path
hdir = os.path.expanduser('~')

#pahlavi corpus directory
pah_path = hdir + "/Dropbox/Active_Directories/Digital_Humanities/Corpora/pahlavi_corpus/"

#pickle path
pickle_path = hdir + "/Dropbox/Active_Directories/Digital_Humanities/Corpora/pickled_tokenized_cleaned_corpora"


# In[7]:


df_pahcorp = pd.read_csv (os.path.join(pickle_path,r'pahlavi_corpus.csv'))


# In[8]:


df_pahcorp.sample(5)


# ----
#
# ## Key Word in Context

# In[25]:


def index_kwic (term):

    """This function returns a dataframe filtered by the search term."""

    result = df_pahcorp[df_pahcorp['token'].str.match(term)]
    return result

    # str.match; the str part is telling match how to behave; .match is a method specific to pandas


# add regex functionality:


# In[26]:


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



# In[ ]:


#df_pahcorp["token"] == "afsōn"


# In[27]:


kwic_pah ("hāmōn")


# In[ ]:


# Conditional frequency

# two problems: (1) find where the words are; (2) find what words are next to a particular location

# collect on i-1 i+1; counter is a function in the collections module that takes a list and turns it into a frequency dictionary
## A column is technically a series, which can work like a list.


# In[ ]:


indexed = list(index_kwic('hāmōn').index)

cd_index = []
length = len(indexed)
for i in range(length):
    cd_index.append((indexed[i]-1, indexed[i], indexed[i]+1))



# now need to use this (and counter module?) to count frequency of the terms immediately before and after, i.e. positions 0 and 2 in the tuple


# In[ ]:


cd_index


# In[ ]:


#for x in cd_index:
#    print (cd_index[x][1])


# In[ ]:


cd_index[1][1]


# In[ ]:


df_pahcorp.iloc[240938]


# ## Frequency

# In[11]:


freq_dic = pd.value_counts(df_pahcorp.token).to_frame().reset_index()


# In[12]:


freq_dic.sample(5)


# In[21]:


search_term = re.compile(r"p..z")


# In[23]:


query_mask = freq_dic["index"].str.contains(search_term, na=False)
query = freq_dic[query_mask]
query.head()

# turn into a function, just return top hits


# In[ ]:
