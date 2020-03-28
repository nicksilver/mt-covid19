import pandas as pd
import json
import urllib.request
import matplotlib.pyplot as plt


# Data sources
nyt_county = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
nyt_state = 'https://github.com/nytimes/covid-19-data/blob/master/us-states.csv'
usa_facts = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv'
mt_data = 'https://www.arcgis.com/sharing/rest/content/items/0d47920e54e0420cb604213acc8761d5/data'
nls_mt_data = './mt_coronavirus_status.csv'

# Fips codes
{
    "state": {
        "MT": {
            "Missoula": 30063,
            "Gallatin": 30031
        },
        "FL": {
            "Collier": 12021
        }
    }
}

class CovidTrends(object):
    
    def __init__(self, state='Montana', county=None):
        self.state = state
        self.county = county


    def get_nyt_state_data(self):

        datatypes = {
            'date': 'str',
            'county': 'str',
            'state': 'str',
            'fips': 'Int64',
            'cases': 'Int64',
            'deaths': 'Int64'
        }

        nyt_df = pd.read_csv(nyt_county, dtype=datatypes, parse_dates=[0])
        nyt_df.set_index('date',  inplace=True)

        return nyt_df[nyt_df['state'] == self.state]

    def select_county_data(self, state_df):
        county_df_all = state_df[state_df['fips'] == self.county]
        county_df = county_df_all['cases'].to_frame()
        county_df.columns = [self.county]
        return county_df

    def fill_mt_state_data(self, state_df_grp):
        nls_df = pd.read_csv(nls_mt_data, parse_dates=[0], index_col=['date'])
        state_fill_df = pd.merge(state_df_grp, nls_df['MT Cases'], how='outer', 
            left_index=True, right_index=True)
        return state_fill_df[self.state].fillna(nls_df['MT Cases']).to_frame()
  
    def fill_missoula_county_data(self, county_df):
        nls_df = pd.read_csv(nls_mt_data, parse_dates=[0], index_col=['date'])
        county_df = pd.merge(county_df[self.county], nls_df['Missoula Cases'], how='outer', 
            left_index=True, right_index=True)
        return county_df[self.county].fillna(county_df['Missoula Cases']).to_frame()

    def get_covid_data(self):

        state_df = self.get_nyt_state_data()
        state_df_grp = state_df.groupby('date').sum()[['cases']]
        state_df_grp.columns = [self.state]

        if self.state == 'Montana':
            state_fill_df = self.fill_mt_state_data(state_df_grp)
            df = state_fill_df

            if self.county:
                county_df = self.select_county_data(state_df)

                if self.county == 30063:
                    county_df = self.fill_missoula_county_data(county_df)

                df = pd.merge(state_fill_df, county_df, how='outer', right_index=True, left_index=True)

        else:

            df = state_df_grp

            if self.county:
                county_df_all = self.select_county_data(state_df)
                df = pd.merge(state_df_grp, county_df, how='outer', right_index=True, left_index=True)
        
        return df 

data = CovidTrends(county=30063).get_covid_data()
data.diff()



# %%
# Attempt to scrape MT ESRI map data
# i = 26
# with urllib.request.urlopen(mt_data) as url:
#     data = json.loads(url.read().decode())
# d = data['operationalLayers'][0]['featureCollection']['layers'][0]['featureSet']['features'][i]['attributes']
# pd.DataFrame.from_dict(d, orient='index')

# county = 30031 #30063
# state = 'Montana'

# datatypes = {
#     'date': 'str',
#     'county': 'str',
#     'state': 'str',
#     'fips': 'Int64',
#     'cases': 'Int64',
#     'deaths': 'Int64'
# }
# nls_df = pd.read_csv(nls_mt_data, parse_dates=[0], index_col=['date'])
# nyt_df = pd.read_csv(nyt_county, dtype=datatypes, parse_dates=[0])
# nyt_df.set_index('date',  inplace=True)
# state_df = nyt_df[nyt_df['state'] == state]

# state_df_grp = state_df.groupby('date').sum()[['cases']]
# state_df_grp.columns = [state]

# if state == 'Montana':

#     state_fill_df = pd.merge(state_df_grp, nls_df['MT Cases'], how='outer', left_index=True, right_index=True)
#     state_fill_df = state_fill_df[state].fillna(nls_df['MT Cases']).to_frame()
#     df = state_fill_df

#     if county:
#         county_df_all = state_df[state_df['fips'] == county]
#         county_df = county_df_all['cases'].to_frame()
#         county_df.columns = [county]

#         if county == 30063:
#             county_df = pd.merge(county_df[county], nls_df['Missoula Cases'], how='outer', left_index=True, right_index=True)
#             county_df = county_df[county].fillna(county_df['Missoula Cases']).to_frame()

#         df = pd.merge(state_fill_df, county_df, how='outer', right_index=True, left_index=True)

# else:

#     df = state_df_grp

#     if county:
#         county_df_all = state_df[state_df['fips'] == county]
#         county_df = county_df_all['cases'].to_frame()
#         county_df.columns = [county]
#         df = pd.merge(state_df_grp, county_df, how='outer', right_index=True, left_index=True)
