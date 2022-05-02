# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 09:33:42 2022

@author: alvi
"""
import streamlit as st
import numpy as np
import pandas as pd
from chart_studio import plotly as py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from itertools import product
from datetime import datetime
import time
from PIL import Image


###------>How RimSize/CapCompound/AspectRatio Vs RRC



#######Setting the Basics for the Page
st.set_page_config(page_title="RRCExploratory", page_icon="muscleman.jpg", layout="wide", initial_sidebar_state="auto")
st.title('RRC Exploratory')


####Reading the Files
#RR_ISO = pd.read_csv('tblHSURRISOTestResults.csv',encoding="cp1252")
#RR_ISO = RR_ISO.rename(columns={'FeatureNumber':'VersionCode'})
#RR_ISO = RR_ISO[['UniqueId','VersionCode','CRR','RimSize']] 
#RR_ISO = RR_ISO.loc[~(RR_ISO['CRR'] ==0),:]
#
#DR_details = pd.read_csv('tblDRDetails.csv',encoding="cp1252")
#DR_details = DR_details[['UniqueId','VersionCode','SizeWithLoadSpeedIndex','CapCompound','Createddate']] 
#
#
#DR_details = DR_details.replace(r'^\s*$', np.nan, regex=True)
#
#RC_with_DR = pd.merge(DR_details,RR_ISO, 
#                        left_on=['UniqueId','VersionCode'], right_on=['UniqueId','VersionCode'], how='inner')
#
# 
#aspectratio_master = pd.read_excel(open('Master_Table_V1.xlsx', 'rb'),sheet_name='Aspect_Ratio')  
#RC_with_DR = pd.merge(RC_with_DR, aspectratio_master, 
#                        left_on='SizeWithLoadSpeedIndex', right_on='SizeWithLoadSpeedIndex', how='inner')
#
#
#RC_with_DR.to_csv('RC_with_DR.csv')
########Reading the File
RC_with_DR =pd.read_csv('RC_with_DR.csv')
RC_with_DR['Createddate'] = pd.to_datetime(RC_with_DR['Createddate'])
RC_with_DR['Createddate']=RC_with_DR['Createddate'].dt.date

RC_with_DR = RC_with_DR.loc[~(RC_with_DR['CRR'] ==0),:]

RC_with_DR = RC_with_DR.dropna(subset=['CRR'])

RC_with_DR['CRR'] =pd.to_numeric(RC_with_DR['CRR'], downcast='float')

############Select Time Period
min_date = RC_with_DR['Createddate'].min()
max_date =RC_with_DR['Createddate'].max()

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input('Start date', min_date)
with col2:
        end_date = st.date_input('End date', max_date)
        
if start_date > end_date:
    st.error('Error: End date must fall after start date.')
        
RC_with_DR = RC_with_DR[(RC_with_DR['Createddate'] >= start_date) & (RC_with_DR['Createddate'] <= end_date)]



###Select Rim Sizes
rim_choices = RC_with_DR['Rim_Size_new'].unique().tolist()
rim_choices.insert(0,"ALL")
rim_make_choice = st.sidebar.multiselect("Select one or more Rim Sizes:",rim_choices,'ALL')
if "ALL" in rim_make_choice:
    rim_make_choice_final = rim_choices
else:
    rim_make_choice_final = rim_make_choice

RC_with_DR=RC_with_DR.loc[(RC_with_DR['Rim_Size_new'].isin(rim_make_choice_final))]
####First Chart
RC_with_DR = RC_with_DR.dropna()



###Select Aspect Ratio
ar_choices = RC_with_DR['aspect_ratio'].unique().tolist()
ar_choices.insert(0,"ALL")
ar_make_choice = st.sidebar.multiselect("Select one or more Aspect Ratios:",ar_choices,'ALL')
if "ALL" in ar_make_choice:
    ar_make_choice_final = ar_choices
else:
    ar_make_choice_final = ar_make_choice
RC_with_DR=RC_with_DR.loc[(RC_with_DR['aspect_ratio'].isin(ar_make_choice_final))]


###Select Capcompound
cap_choices = RC_with_DR['CapCompound'].unique().tolist()
cap_choices.insert(0,"ALL")
cap_make_choice = st.sidebar.multiselect("Select one or more Cap Compounds:",cap_choices,'ALL')
if "ALL" in cap_make_choice:
    cap_make_choice_final = cap_choices
else:
    cap_make_choice_final = cap_make_choice


RC_with_DR=RC_with_DR.loc[(RC_with_DR['CapCompound'].isin(cap_make_choice_final))]

####Removing Duplicates
RC_with_DR = RC_with_DR.dropna()
st.write("After filtering",RC_with_DR.shape[0], " observations were filtered for the dashboard" )

csv= RC_with_DR.to_csv().encode('utf-8')
st.download_button(
   "Click to Download Data",
    csv,
   "RRC Data.csv",
   "text/csv",
   key='download-csv'
   )


image = Image.open('muscle_man2.png')
st.sidebar.image(image)




#######################################################Charts
####First Chart
fig = go.Figure()

fig = px.scatter(RC_with_DR, x="Createddate", y="CRR", color='CapCompound')
st.plotly_chart(fig,use_container_width=True)




#######Second Chart########
fig1 = go.Figure()
fig1 = px.violin(RC_with_DR, y="CRR", color="aspect_ratio", box=True,
          hover_data=RC_with_DR.columns)
st.plotly_chart(fig1,use_container_width=True)


#######Third Chart########
fig2 = go.Figure()
fig2 = px.violin(RC_with_DR, y="CRR", color="CapCompound", box=True,
          hover_data=RC_with_DR.columns)
st.plotly_chart(fig2,use_container_width=True)


#######Third Chart########
fig2 = go.Figure()
fig2 = px.violin(RC_with_DR, y="CRR", color="Rim_Size_new", box=True,
          hover_data=RC_with_DR.columns)
st.plotly_chart(fig2,use_container_width=True)

