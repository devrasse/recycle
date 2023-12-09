import json
import requests  # pip install requests
import streamlit as st  # pip install streamlit
from streamlit_lottie import st_lottie  # pip install streamlit-lottie
import pandas as pd
import time
import os
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import pearsonr


# GitHub: https://github.com/andfanilo/streamlit-lottie
# Lottie Files: https://lottiefiles.com/

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

#st.title(':bar_chart: 2024년 미추홀구 예산')
#st.markdown('<style>div.block-containner{padding-top:1rem;}</style>', unsafe_allow_html=True)

# 화면 중앙에 위치하도록 스타일 설정
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 0.5vh;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 제목을 div 태그로 감싸서 스타일 적용
st.markdown('<div class="centered"><h1 style="text-align:center;">📊 자원순환과 예산 분석 </h1></div>', unsafe_allow_html=True)
st.title("   ")

lottie_loading = load_lottiefile("lottiefiles/loading.json")  # replace link to local lottie file
loading_state = st.empty()
#lottie_hello = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_M9p23l.json")
#lottie_loading = load_lottieurl("https://lottie.host/efece630-073b-49e3-8240-1a8a9c118346/KbRGnvFFOG.json")
# st_lottie(
#     lottie_loading,
#     speed=1,
#     reverse=False,
#     loop=True,
#     quality="low", # medium ; high
#     renderer="canvas", # svg, canvas
#     height=None,
#     width=None,
#     key=None,
# )
with loading_state.container():
    with st.spinner('데이터 읽어오는 중...'):
        st_lottie(lottie_loading)
        df = pd.read_excel('budget.xlsx')
    st.success('로딩 완료!')
    
loading_state.empty()

budget = df.copy()
budget = budget.dropna(subset=['산출근거식'])
# #budget.drop(0, inplace=True)
selected_columns = ['회계연도', '예산구분', '세부사업명', '부서명', '예산액', '자체재원','단위사업명','편성목명']
budget = budget[selected_columns]
#budget['자체재원'] = budget['자체재원'].replace('경정', '', regex=True)
#budget['회계연도'] = budget['회계연도'].fillna(0).replace(float('inf'), 0).astype(int)
#budget['회계연도'] = budget['회계연도'].astype(str)
budget['자체재원'] = budget['자체재원'].fillna(0).apply(lambda x: int(x) if str(x).isdigit() and x != '' else 0)

budget = budget[(budget['예산구분'] == '본예산') | (budget['예산구분'] == '본예산(안)')]
budget_group = budget.groupby(['회계연도','부서명']).sum()

budget_dataframes = {}
for year in range(2015, 2025):
    budget_year = budget_group.xs(year, level='회계연도', drop_level=True)
    budget_year.reset_index(inplace=True)
    budget_dataframes[f'budget_{year}'] = budget_year[['세부사업명', '부서명', '예산액', '자체재원']]


with st.expander("미추홀구 예산", expanded=False):
    st.dataframe(budget,use_container_width=True)

highlight_department = '자원순환과'

col1, col2 = st.columns(2)
budget_2024 = budget_dataframes['budget_2024']
budget_2024['자체재원'] = (budget_2024['자체재원']  / 1000).apply(np.floor)
budget_2024['예산액'] = (budget_2024['예산액']  / 1000).apply(np.floor)
budget_2024 = budget_2024.sort_values(by='예산액',ascending=False)

# fig = px.bar(budget, x='부서명', y='예산액',
#               #color_discrete_map=color_discrete_map,
#               title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub> ', labels={'자체재원': '구비', '부서명': '부서명'},
#               template= 'simple_white')
# #fig.update_layout(yaxis_tickformat=',.0s')
# fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
# #fig.update_layout(title_x=0.5)
# fig.update_xaxes(tickangle=45)
with col1:
    fig = px.pie(budget_2024, values='예산액', names='부서명',
                title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub>',
                template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황</b><br><sub>2024년 부서별 예산현황</sub>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    color_discrete_map = {highlight_department: 'blue'}
    for department in budget_2024['부서명']:
        if department != highlight_department:
            color_discrete_map[department] = 'gray'

    fig = px.pie(budget_2024, values='예산액', names='부서명',
                title='<b>미추홀구 예산 현황</b><br><sub>2024년 자원순환과</sub>',
                template='simple_white')
    fig.update_traces(marker=dict(colors=budget_2024['부서명'].map(color_discrete_map)),
                    textposition='inside', textinfo = 'percent+label',textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황</b><br><sub>2024년 부서별 예산현황</sub>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)
budget_top10 = budget_2024.nlargest(10,'예산액')
budget_top10 = budget_top10.sort_values(by='예산액',ascending=False)

with col1:
    fig = px.bar(budget_top10, x='부서명', y='예산액',
                #color_discrete_map=color_discrete_map,
                title='<b>미추홀구 예산 현황</b><br><sub>2024년 상위10개부서</sub> ',
                labels={'예산액': '예산액', '부서명': '부서명'},
                template= 'simple_white',text = budget_top10['예산액'].apply(lambda x: f'{x:,.0f}'))
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황</b><br><sub>2024년 상위10개부서</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True)

with col2:
    color_discrete_map = {highlight_department: 'blue'}
    for department in budget_top10['부서명']:
        if department != highlight_department:
            color_discrete_map[department] = 'gray'

    fig = px.bar(budget_top10, x='부서명', y='예산액', color='부서명',
                color_discrete_map=color_discrete_map,
                title='<b>미추홀구 예산 현황</b><br><sub>2024년 상위10개부서</sub> ', labels={'예산액': '예산액', '부서명': '부서명'},
                template= 'simple_white',text = budget_top10['예산액'].apply(lambda x: f'{x:,.0f}'))
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황</b><br><sub>2024년 상위10개부서</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2) 
budget_2024 = budget_2024.sort_values(by='자체재원',ascending=False)
with col1:
    fig = px.pie(budget_2024, values='자체재원', names='부서명',
                title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub>',
                template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 부서별 예산현황</sub>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    color_discrete_map = {highlight_department: 'blue'}
    for department in budget_2024['부서명']:
        if department != highlight_department:
            color_discrete_map[department] = 'gray'

    fig = px.pie(budget_2024, values='자체재원', names='부서명',
                title='<b>미추홀구 예산 현황</b><br><sub>2024년</sub>',
                template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(marker=dict(colors=budget_2024['부서명'].map(color_discrete_map)),
                    textposition='inside', textinfo = 'percent+label', textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 부서별 예산현황(자원순환과)</sub>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)

budget_top10_self = budget_2024.nlargest(10,'자체재원')
budget_top10_self = budget_top10_self.sort_values(by='자체재원',ascending=False)

with col1:    
    fig = px.bar(budget_top10_self, x='부서명', y='자체재원',
                #color_discrete_map=color_discrete_map,
                title='<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 상위10개부서</sub> ', 
                labels={'자체재원': '예산액(구비)', '부서명': '부서명'},
                template= 'simple_white',text = budget_top10_self['예산액'].apply(lambda x: f'{x:,.0f}'))
    #fig.update_layout(yaxis_tickformat=',.0s')

    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 상위10개부서</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True) 

with col2:
    color_discrete_map = {highlight_department: 'blue'}
    for department in budget_top10_self['부서명']:
        if department != highlight_department:
            color_discrete_map[department] = 'gray'

    fig = px.bar(budget_top10_self, x='부서명', y='자체재원',color='부서명',
                color_discrete_map=color_discrete_map,
                title='<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 상위10개부서</sub> ', labels={'자체재원': '예산액(구비)', '부서명': '부서명'},
                template= 'simple_white',text = budget_top10_self['예산액'].apply(lambda x: f'{x:,.0f}'))
    #fig.update_layout(yaxis_tickformat=',.0s')

    fig.update_layout(title = {
        'text': '<b>미추홀구 예산 현황(구비)</b><br><sub>2024년 상위10개부서</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True)
    
st.markdown("---")
col1, col2 = st.columns(2) 

department_of_recycle = budget[(budget['회계연도']==2024)&(budget['부서명']=='자원순환과')]
department_of_recycle['자체재원'] = (department_of_recycle['자체재원']  / 1000).apply(np.floor)
#department_of_recycle = budget_2024[budget_2024['부서명'] == '자원순환과']
with col1:
    fig = px.treemap(budget_2024, path=['부서명'], values='자체재원',
        height=800, width= 800, color_discrete_sequence=px.colors.qualitative.Set1) #px.colors.qualitative.Pastel2)
    fig.update_layout(title = {
        'text': '2024년 미추홀구 예산 현황(구비)',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = dict(t=100, l=25, r=25, b=25))
    fig.update_traces(marker = dict(line=dict(width = 1, color = 'black')))
    fig.update_traces(texttemplate='%{label}: %{value:,.0f}백만원' , textposition='middle center', 
                    textfont_color='black') 
    fig.update_traces(#hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    fig.update_traces(hoverlabel=dict(font_size=16, font_family="Arial", font_color="white"))
    fig.update_layout(font=dict(size=20))
    st.plotly_chart(fig, use_container_width=True)   

col1.write("</div>", unsafe_allow_html=True)

with col2:
    fig = px.treemap(department_of_recycle, path=['단위사업명','세부사업명','편성목명'], values='자체재원',
        height=800, width= 800, color_discrete_sequence=px.colors.qualitative.Pastel2) #px.colors.qualitative.Pastel2)
    fig.update_layout(title = {
        'text': '2024년 자원순환과 예산 현황(구비)',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = dict(t=100, l=25, r=25, b=25))
    fig.update_traces(marker = dict(line=dict(width = 1, color = 'black')))
    fig.update_traces(texttemplate='%{label}: %{value:,.0f}백만원' , textposition='middle center', 
                    textfont_color='black') 
    fig.update_traces(#hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    fig.update_traces(hoverlabel=dict(font_size=16, font_family="Arial", font_color="white"))
    fig.update_layout(font=dict(size=20))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)
recycle_group = department_of_recycle.groupby(by='세부사업명').sum()
budget_top10_recycle = recycle_group.nlargest(10,'자체재원')
budget_top10_recycle = budget_top10_recycle.sort_values(by='자체재원',ascending=False)
budget_top10_recycle.reset_index(inplace=True)
with col1:
    fig = px.pie(department_of_recycle, values='자체재원', names='세부사업명',
            template='simple_white',color_discrete_sequence = px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo = 'percent+label', 
            textfont_color='white')
    fig.update_layout(title = {
        'text': '<b>자원순환과 예산 현황</b><br><sub>2024년 세부사업</sub>',
        'y': 0.95,
        'x': 0.4,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    fig.update_traces(hoverinfo='label+percent+value', 
                    hovertemplate='%{label}: %{value:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(budget_top10_recycle,x='세부사업명', y='자체재원',
                labels={'자체재원': '구비', '세부사업명': '사업명'},
                template= 'simple_white',text = budget_top10['자체재원'].apply(lambda x: f'{x:,.0f}'))
    fig.update_layout(title = {
        'text': '<b>자원순환과 예산 현황</b><br><sub>2024년 세부사업</sub>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)
budget_group.reset_index(inplace=True)
budget_group['자체재원'] = budget_group['자체재원'].astype(float)
budget_group['자체재원'] = (budget_group['자체재원']  / 1000).apply(np.floor)
budget_top5 = budget_group.groupby('회계연도').apply(lambda group: group.nlargest(5, '자체재원')).reset_index(drop=True)
budget_top5.reset_index(inplace=True)

with col1:
    # Plotly를 사용하여 시계열 그래프 그리기
    fig = px.line(budget_top5, x='회계연도', y='자체재원', color='부서명', markers=True,
                title='<b>부서별 예산 증가 현황</b><br><sub>연도별 예산증가 상위5개 부서 현황</sub> ', labels={'자체재원': '구비', '회계연도': '연도'},
                template= 'simple_white')
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    fig.update_layout(title_x=0.4)
    fig.update_traces(hovertemplate='연도: %{x}년<br>예산액: %{y:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    color_discrete_map = {highlight_department: 'blue'}
    for department in budget['부서명'].unique():
        if department != highlight_department:
            color_discrete_map[department] = 'gray'

    # Plotly를 사용하여 시계열 그래프 그리기
    fig = px.line(budget_top5, x='회계연도', y='자체재원', color='부서명', markers=True,
                color_discrete_map=color_discrete_map,
                title='<b>부서별 예산 증가 현황</b><br><sub>연도별 예산증가 상위5개 부서 현황</sub>', labels={'자체재원': '구비', '회계연도': '연도'},
                template= 'simple_white')
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    fig.update_layout(title_x=0.4)
    fig.update_traces(hovertemplate='연도: %{x}년<br>예산액: %{y:,.0f}백만원')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
budget_department_of_recycle = budget[budget['부서명'] == '자원순환과']

budget_department_of_recycle_years = budget_department_of_recycle.groupby('회계연도').sum()
budget_department_of_recycle_years['자체재원'] = (budget_department_of_recycle_years['자체재원']  / 1000).apply(np.floor)
budget_department_of_recycle_years.reset_index(inplace=True)

fig = px.line(budget_department_of_recycle_years, x='회계연도', y='자체재원',  markers=True,
            title='<b>자원순환과 예산 현황</b><br><sub>연도별 현황(구비)</sub>', labels={'자체재원': '예산액', '회계연도': '연도'}
            ,template= 'simple_white', #text = budget_department_of_recycle_years['예산액'].apply(lambda x: f'{x:,.0f}백만원'
            )
fig.update_traces(hovertemplate='연도: %{x}년<br>구비: %{y:,.0f}백만원')
fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
fig.update_layout(title_x=0.5)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)
budget_department_of_recycle_group = budget_department_of_recycle.groupby(['회계연도','세부사업명']).sum()
budget_department_of_recycle_group.reset_index(inplace=True)
budget_department_of_recycle_group['자체재원'] = (budget_department_of_recycle_group['자체재원']  / 1000).apply(np.floor)

budget_life_waste = budget_department_of_recycle_group[budget_department_of_recycle_group['세부사업명'].str.contains('생활폐기물.*처리')]
budget_life_waste['세부사업명'] = '생활폐기물 수거 처리'

budget_recycle_waste = budget_department_of_recycle_group\
                        [budget_department_of_recycle_group['세부사업명'].str.contains('재활용품.*처리')]
budget_recycle_waste['세부사업명'] = '재활용품 수거 처리'
budget_food_waste = budget_department_of_recycle_group\
                    [budget_department_of_recycle_group['세부사업명'].str.contains('음식물.*수거|수거.*음식물')]
budget_food_waste['세부사업명'] = '음식물류폐기물 수거처리'
df_agencyfee = pd.concat([budget_food_waste, budget_life_waste, budget_recycle_waste], ignore_index=True)
df_agencyfee = df_agencyfee.fillna(0)

with col1:

    fig = px.line(df_agencyfee, x='회계연도', y='자체재원', color='세부사업명', markers=True,
                title='<b>자원순환과 예산 현황</b><br><sub>연도별 대행료 지출(생활,재활용,음식물)',
                labels={'자체재원': '예산액', '회계연도': '연도'}
                ,template= 'simple_white', #text = budget_department_of_recycle_years['예산액'].apply(lambda x: f'{x:,.0f}백만원'
                custom_data=['세부사업명']
                )
    fig.update_traces(hovertemplate='연도: %{x}년<br>예산액: %{y:,.0f}백만원<br>사업명: %{customdata[0]}',
                    hoverlabel=dict(font=dict(color='white')))
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    fig.update_layout(title_x=0.4)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(df_agencyfee, x='회계연도', y='자체재원', color='세부사업명',
                    #color_discrete_map=color_discrete_map,
                    title='<b>자원순환과 예산 현황</b><br><sub>연도별 대행료 지출(생활,재활용,음식물)</sub> ',
                    labels={'자체재원': '예산액', '회계연도': '연도'},
                    template= 'simple_white',text = df_agencyfee['자체재원'].apply(lambda x: f'{x:,.0f}'))
    fig.update_layout(title = {
        'text': '<b>자원순환과 예산 현황</b><br><sub>연도별 대행료 지출(생활,재활용,음식물)',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'color': 'white',
                'size' : 20}}, margin = {'t': 80} )
    #fig.update_layout(yaxis_tickformat=',.0s')
    fig.update_traces(textposition='inside', textfont_color='white')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    #fig.update_layout(title_x=0.5)
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='%{label}: %{value:,.0f}백만원')

    st.plotly_chart(fig, use_container_width=True)
    
st.markdown("---")    
col1, col2, col3 = st.columns(3)
with col1:
    fig = px.line(budget_life_waste, x='회계연도', y='자체재원', markers=True,
            title='<b>생활폐기물 처리 비용</b><br><sub>연도별 생활폐기물 수거처리</sub>', labels={'자체재원': '예산액', '회계연도': '연도'}
            ,template= 'simple_white', #text = budget_department_of_recycle_years['예산액'].apply(lambda x: f'{x:,.0f}백만원'
            custom_data=['세부사업명'])
    fig.update_traces(hovertemplate='연도: %{x}년<br>예산액: %{y:,.0f}백만원<br>사업명: %{customdata[0]}')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    fig.update_layout(title_x=0.4)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.line(budget_recycle_waste, x='회계연도', y='자체재원', markers=True,
            title='<b>재활용폐기물 처리 비용</b><br><sub>연도별 재활용폐기물 수거처리</sub>', labels={'자체재원': '예산액', '회계연도': '연도'}
            ,template= 'simple_white', #text = budget_department_of_recycle_years['예산액'].apply(lambda x: f'{x:,.0f}백만원'
            custom_data=['세부사업명'])
    fig.update_traces(hovertemplate='연도: %{x}년<br>자체재원: %{y:,.0f}백만원<br>사업명: %{customdata[0]}')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    fig.update_layout(title_x=0.4)
    st.plotly_chart(fig, use_container_width=True)

with col3:
    fig = px.line(budget_food_waste, x='회계연도', y='자체재원', markers=True,
            title='<b>음식물폐기물 처리 비용</b><br><sub>연도별 음식물폐기물 수거처리</sub>', labels={'자체재원': '예산액', '회계연도': '연도'}
            ,template= 'presentation', #text = budget_department_of_recycle_years['예산액'].apply(lambda x: f'{x:,.0f}백만원'
            custom_data=['세부사업명'])
    fig.update_traces(hovertemplate='연도: %{x}년<br>자체재원: %{y:,.0f}백만원<br>사업명: %{customdata[0]}')
    fig.update_layout(yaxis_tickformat=',.0f', yaxis_ticksuffix='백만원')
    fig.update_layout(title_x=0.4)
    st.plotly_chart(fig, use_container_width=True)
