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

#####################################################
str_cols=['CapCompound', 'Base1Compound']
int_cols=['InnerPerimeter','Cap1Gauge','Base1Gauge']
target_col=['CRR']
select_sku =["185/65 R15",
"215/60 R16",
"165/80 R14",	
"165/70 R14",	
"205/60 R16",	
"175/65 R14",	
"205/65 R16",
"185/60 R15",
"195/65 R15",
"155/80 R13"]


####################################################

####Reading the Files
RR_ISO = pd.read_csv('tblHSURRISOTestResults.csv',encoding="cp1252")
RR_ISO = RR_ISO.rename(columns={'FeatureNumber':'VersionCode'})
RR_ISO = RR_ISO[['UniqueId','VersionCode','CRR','RimSize']] 
RR_ISO = RR_ISO.loc[~(RR_ISO['CRR'] ==0),:]


DR_details = pd.read_csv('tblDRDetails.csv',encoding="cp1252")
DR_details = DR_details[['UniqueId','VersionCode','SizeWithLoadSpeedIndex','CapCompound','Createddate','CapCompound', 'Base1Compound','InnerPerimeter','Cap1Gauge','Base1Gauge']] 


DR_details = DR_details.replace(r'^\s*$', np.nan, regex=True)

RC_with_DR = pd.merge(DR_details,RR_ISO, 
                        left_on=['UniqueId','VersionCode'], right_on=['UniqueId','VersionCode'], how='inner')

 
aspectratio_master = pd.read_excel(open('Master_Table_V1.xlsx', 'rb'),sheet_name='Aspect_Ratio')  
RC_with_DR = pd.merge(RC_with_DR, aspectratio_master, 
                        left_on='SizeWithLoadSpeedIndex', right_on='SizeWithLoadSpeedIndex', how='inner')


RC_with_DR.to_csv('RC_with_DR1.csv')
########Reading the File

with st.expander('Aspect Ratio,Rim Size & Cap Compound'):
    RC_with_DR1 =pd.read_csv('RC_with_DR1.csv')
    RC_with_DR1['SizeWithLoadSpeedIndex'] = RC_with_DR1['SizeWithLoadSpeedIndex'].str.strip()
    RC_with_DR1['Createddate'] = pd.to_datetime(RC_with_DR1['Createddate'])
    RC_with_DR1['Createddate']=RC_with_DR1['Createddate'].dt.date
    
    RC_with_DR1 = RC_with_DR1.loc[~(RC_with_DR1['CRR'] ==0),:]
    
    RC_with_DR1 = RC_with_DR1.dropna(subset=['CRR'])
    
    RC_with_DR1['CRR'] =pd.to_numeric(RC_with_DR1['CRR'], downcast='float',errors='coerce')
    
    ############Select Time Period
    min_date = RC_with_DR1['Createddate'].min()
    max_date =RC_with_DR1['Createddate'].max()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input('Start date', min_date)
    with col2:
            end_date = st.date_input('End date', max_date)
            
    if start_date > end_date:
        st.error('Error: End date must fall after start date.')
            
    RC_with_DR1 = RC_with_DR1[(RC_with_DR1['Createddate'] >= start_date) & (RC_with_DR1['Createddate'] <= end_date)]
    
    
    
    ###Select Rim Sizes
    rim_choices = RC_with_DR1['Rim_Size_new'].unique().tolist()
    rim_choices.insert(0,"ALL")
    rim_make_choice = st.sidebar.multiselect("Select one or more Rim Sizes:",rim_choices,'ALL')
    if "ALL" in rim_make_choice:
        rim_make_choice_final = rim_choices
    else:
        rim_make_choice_final = rim_make_choice
    
    RC_with_DR1=RC_with_DR1.loc[(RC_with_DR1['Rim_Size_new'].isin(rim_make_choice_final))]
    ####First Chart
    RC_with_DR1 = RC_with_DR1.dropna()
    
    
    
    ###Select Aspect Ratio
    ar_choices = RC_with_DR1['aspect_ratio'].unique().tolist()
    ar_choices.insert(0,"ALL")
    ar_make_choice = st.sidebar.multiselect("Select one or more Aspect Ratios:",ar_choices,'ALL')
    if "ALL" in ar_make_choice:
        ar_make_choice_final = ar_choices
    else:
        ar_make_choice_final = ar_make_choice
    RC_with_DR1=RC_with_DR1.loc[(RC_with_DR1['aspect_ratio'].isin(ar_make_choice_final))]
    
    
    ###Select Capcompound
    cap_choices = RC_with_DR1['CapCompound'].unique().tolist()
    cap_choices.insert(0,"ALL")
    cap_make_choice = st.sidebar.multiselect("Select one or more Cap Compounds:",cap_choices,'ALL')
    if "ALL" in cap_make_choice:
        cap_make_choice_final = cap_choices
    else:
        cap_make_choice_final = cap_make_choice
    
    
    RC_with_DR1=RC_with_DR1.loc[(RC_with_DR1['CapCompound'].isin(cap_make_choice_final))]
    
    ####Removing Duplicates
    RC_with_DR1 = RC_with_DR1.dropna()
    st.write("After filtering",RC_with_DR1.shape[0], " observations were filtered for the dashboard" )
    
    csv= RC_with_DR1.to_csv().encode('utf-8')
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
    
    fig = px.scatter(RC_with_DR1, x="Createddate", y="CRR", color='CapCompound')
    st.plotly_chart(fig,use_container_width=True)
     
    #######Second Chart########
    fig1 = go.Figure()
    fig1 = px.violin(RC_with_DR1, y="CRR", color="aspect_ratio", box=True,
              hover_data=RC_with_DR1.columns)
    st.plotly_chart(fig1,use_container_width=True)
    
    
    #######Third Chart########
    fig2 = go.Figure()
    fig2 = px.violin(RC_with_DR1, y="CRR", color="CapCompound", box=True,
              hover_data=RC_with_DR1.columns)
    st.plotly_chart(fig2,use_container_width=True)
    
    
    #######Third Chart########
    fig2 = go.Figure()
    fig2 = px.violin(RC_with_DR1, y="CRR", color="Rim_Size_new", box=True,
              hover_data=RC_with_DR1.columns)
    st.plotly_chart(fig2,use_container_width=True)
    
with st.expander('Selected Variable Analysis'):
    
    variable_make_choice = st.selectbox("Please select the variable for analysis",str_cols+int_cols)
    if variable_make_choice in str_cols:
        fig = go.Figure()
        fig = px.scatter(RC_with_DR1, x="Createddate", y="CRR", color=variable_make_choice)
        fig.update_layout(title_text= "Time Series-Overall")
        st.plotly_chart(fig,use_container_width=True)
            
        fig2 = go.Figure()
        fig2 = px.violin(RC_with_DR1, y="CRR", color=variable_make_choice, box=True)
        fig2.update_layout(title_text= "All SKUs")
        st.plotly_chart(fig2,use_container_width=True)
        for count, value in enumerate(select_sku):
            temp = RC_with_DR1.loc[RC_with_DR1['SizeWithLoadSpeedIndex']==value,:]
            if temp.shape[0]>1:
                fig = px.violin(temp, y="CRR", color=variable_make_choice, box=True)
                fig.update_layout(title_text= "SKU Number-" +str(value))
                st.plotly_chart(fig, use_container_width=True)  
    
    if variable_make_choice in int_cols:
        fig = go.Figure()
        fig = px.scatter(RC_with_DR1, x="Createddate", y="CRR", color=variable_make_choice)
        fig.update_layout(title_text= "Time Series-Overall")
        st.plotly_chart(fig,use_container_width=True)
        
        fig = go.Figure()
        fig = px.scatter(RC_with_DR1, x=variable_make_choice, y="CRR")
        fig.update_layout(title_text= "All SKUs")
        st.plotly_chart(fig,use_container_width=True)
                 
        for count, value in enumerate(select_sku):
            temp = RC_with_DR1.loc[RC_with_DR1['SizeWithLoadSpeedIndex']==value,:]
            if temp.shape[0]>1:
                fig = px.scatter(temp, x=variable_make_choice, y='CRR')
                fig.update_layout(title_text= "SKU Number-" +str(value))
                st.plotly_chart(fig, use_container_width=True)       

with st.expander('Correlation Analysis'):
    st.write('Work in Progress')
    st.write('1.Option to analyze correlation between variables')
    st.write('2.Option to visualize the relationship between variables')
