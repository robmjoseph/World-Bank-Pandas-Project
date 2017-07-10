
# coding: utf-8

# ****
# ## JSON exercise
# 
# Using data in file 'data/world_bank_projects.json' and the techniques demonstrated above,
# 1. Find the 10 countries with most projects
# 2. Find the top 10 major project themes (using column 'mjtheme_namecode')
# 3. In 2. above you will notice that some entries have only the code and the name is missing. Create a dataframe with the missing names filled in.

# In[34]:

import json
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
from pandas.io.json import json_normalize
import plotly
plotly.tools.set_credentials_file (username = 'robmjoseph', api_key = 'pzWOCon3iXwBPurXXrDK')

#Get data into dataframe from file and assign to variable wbdf
wbdf = pd.read_json('data/world_bank_projects.json')
#Commitment is part of total though total does not indicate the commitment amount
wbdf


# In analyzing the data there were regions that were being identified as countries. These countries could be identified by the 'countrycode' variable that began with a number versus a letter. Regex was used in the code below to select the rows that had a 'countrycode' identifier consisting of only letters.

# In[35]:

#Countrycodes that represent countries and not regions
wbdf[wbdf.countrycode.str.contains(r'[A-Z]{2}')][['countrycode', 'countryshortname']]


# Solution #1
# Arrived at solution by counting the values of 'countryshortname' column after fitering out the countrycodes that represent regions, then called 'head' function to get the top 10.

# In[36]:

#Eliminate countrycodes that represent regions in the data, count values, and get top 10
wbdf[wbdf.countrycode.str.contains(r'[A-Z]{2}')]['countryshortname'].value_counts().head(10)


# Used dataframe to plot histogram

# In[37]:

#Histogram of projects vs country

wb_reindexed = pd.DataFrame(wbdf[wbdf.countrycode.str.contains(r'[A-Z]{2}')]['countryshortname'].value_counts().head(10)).reset_index()
wb_reindexed.columns = ['COUNTRY', 'PROJECTS']
data = [go.Bar(
            x=wb_reindexed.COUNTRY,
            y=wb_reindexed.PROJECTS
    )]
py.iplot(data)


# Solution #2
# Create new dataFrame using pandas and list comprehension to add dictionaries to table with code and name columns.
# Select data using Group-by code and name and count code using size.
# Sort values in descending order so that highest counts are on top.
# Use head to get the top ten items.

# In[38]:

#The mjtheme_namecode column
wbdf.mjtheme_namecode


# In[39]:

#List comprehension to access list then dictionaries so that pandas could access dictionary values. Grouped by code and name, then sorted for top values
pd.DataFrame([x for x in wbdf.mjtheme_namecode for x in x]).groupby(['code', 'name']).size().sort_values(ascending = False).head(10)  


# Solution #3
# 
# Arrived at solution by using the dataframe created in #2 and setting the row names without a value to 'None' to allow for the ffill() operation. Performed a sort_values on the 'code' column and applied ffill() operation to fill the values forward. Ran a groupby on 'code' and 'name' columns to once more answer question #2 after the cleaning operation.

# In[40]:

#Assign variable to dataframe used in question 2
new_df = pd.DataFrame([x for x in wbdf.mjtheme_namecode for x in x])


# In[41]:

#Set name column items without names to 'None'
new_df.name[new_df.name == ''] = None


# In[42]:

#Sorted dataframe by code and filled code forward on 'None' values using 'ffill' method
csdf = new_df.sort_values('code').ffill()


# In[43]:

#Solution #2 with missing values filled
csdf.groupby(['code', 'name']).size().sort_values(ascending = False).head(10)  


# In[44]:

#Display new dataframe
csdf


# World Map Plot
# 
# A world map plot was created to show the cost and location of projects that were being undertaken. To get the data to display, a new dataframe was created with 'countryshortname' and 'totalcommamt' and data from an example on the plotly website was read into a dataframe, globe_df. The useful data in this file were the 3-digit country codes that allowed the plots on the map. The name of the columns on the 'cnt' dataframe had to be changed to have an identical column on which the merge operation could be performed, and 'COUNTRY'was used by changing 'countryshortname'. The 'totalcommamt' column was used due to the data in that column being the best representation of the total, since some values from the 'totalamt' column of the original dataset had 0 values, even though there were commitment values for each row, and the 'totalamt' included the 'totalcommamt' according to the data on the website. That column name was changed to 'LOAN'.
# 
# Having multiple values for country and multiple dollar amounts, a new dataframe was created with country and dollar amounts combined and summed. Yet another dataframe was created that was reindexed to facilitate the merge operation, and finally the merge was done on the 'COUNTRY' column. The 'COUNTRY', 'CODE', and 'LOAN' columns were then used to plot the data on the map.

# In[45]:

import plotly
plotly.tools.set_credentials_file (username = 'robmjoseph', api_key = 'pzWOCon3iXwBPurXXrDK')


# In[46]:

#Create new Dataframe with countryshortname and totalamt to prepare for merge with country data
cnt = wbdf[['countryshortname', 'totalcommamt']].sort_values(by='countryshortname')


# In[47]:

#Read in data file containing country codes that can be used on world map
globe_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')


# In[48]:

#Display data from file
globe_df


# In[49]:

#Change the names of the columns of the cnt Dataframe to COUNTRY and LOAN in preparation for merge operation
cnt.columns = ['COUNTRY', 'LOAN']


# In[50]:

#Display Dataframe with new names
cnt


# In[51]:

#Groupby on COUNTRY and sum multiple loan values for each country
fil_df = cnt.groupby('COUNTRY')['LOAN'].sum()


# In[52]:

#Create a new Dataframe with a new index in preparation for merge operation
fil2_df = pd.DataFrame(fil_df).reset_index()


# In[53]:

#Output Dataframe
fil2_df


# In[54]:

#Perform merge operation on 'fil2_df' and 'globe-df' Dataframes on 'COUNTRY' column
merged_df = pd.merge(fil2_df, globe_df, on='COUNTRY')


# In[55]:

#Display merged Dataframe
merged_df[['COUNTRY', 'CODE', 'LOAN']]


# In[57]:

#Plot of LOAN amounts on world map by CODE
data = [ dict(
        type = 'choropleth',
        locations = merged_df['CODE'],
        z = merged_df['LOAN'],
        text = merged_df['COUNTRY'],
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(
            autotick = False,
            tickprefix = '$',
            title = 'LOANS<br>Billions US$'),
      ) ]

layout = dict(
    title = 'World Bank Data',
    geo = dict(
        showframe = True,
        showcoastlines = True,
        projection = dict(
            type = 'Mercator'
        )
    )
)

fig = dict( data=data, layout=layout )
py.iplot( fig, validate=False)


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



