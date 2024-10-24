import streamlit as st
import pandas as pd 
import plotly.graph_objects as go

rp_grid_with_teams = pd.read_csv('rp_grid_active_pitchers_sorted.csv')
# rp_grid_with_teams = pd.read_csv('rp_pivot_merged.csv')

date_columns = rp_grid_with_teams.columns[2:-1]
date_columns_reversed = date_columns[::-1]
last_7_dates = date_columns_reversed[:7]

rp_grid_active_pitchers = rp_grid_with_teams.loc[
    ~(rp_grid_with_teams[last_7_dates] == 0).all(axis=1),
    ['team_name', 'player_name'] + list(last_7_dates) + ['Lanzamientos Totales']
]


rp_grid_active_pitchers.reset_index(drop=True, inplace=True)

team_color_map = {
    'MXC': '#19255b',
    'HER': '#fc5000',
    'OBR': '#134489',
    'NAV': '#e2211c',
    'CUL': '#701d45',
    'MAZ': '#ea0a2a',
    'JAL': '#b99823',
    'MTY': '#1f2344',
    'MOC': '#144734',
    'GSV': '#85a8e2',
}

# st.set_page_config(page_title="LMP Batting Stats", layout="wide")
logo_and_title = """
    <div style="display: flex; align-items: center;">
        <img src="https://www.lmp.mx/assets/img/header/logo_80_aniversary.webp" alt="LMP Logo" width="40" height="40">
        <h1 style="margin-left: 20px; font-size: 30px;">Bullpen LMP</h1>
    </div>
"""

# Display the logo and title using st.markdown
st.markdown(logo_and_title, unsafe_allow_html=True)
st.divider()

team_choice = st.selectbox('Selecciona un equipo:', rp_grid_active_pitchers['team_name'].unique())

team_data = rp_grid_active_pitchers[rp_grid_active_pitchers['team_name'] == team_choice]


team_data = team_data.loc[:, (team_data != 0).any(axis=0)]


date_columns_team = team_data.columns[2:-1]


headers = ['RP'] + [str(col) for col in date_columns_team] + ['Lanzamientos Totales']


def format_cells_for_bold(team_data, columns):
    formatted_cells = []
    for col in columns:
        formatted_column = []
        for value in team_data[col]:
            if value != 0:
                formatted_column.append(f"<b>{value}</b>") 
            else:
                formatted_column.append(f"{value}")  
        formatted_cells.append(formatted_column)
    return formatted_cells


cells = [team_data['player_name']] + format_cells_for_bold(team_data, date_columns_team) + [team_data['Lanzamientos Totales']]


team_color = team_color_map.get(team_choice, '#ffffff')

fig = go.Figure(data=[go.Table(
    header=dict(values=headers, fill_color=team_color, align='center',
                font=dict(size=12, color='beige')),
    cells=dict(values=cells, fill_color='#a19174', align='center', format=['html'],
               font=dict(size=12, family='Verdana', color='black'))  
)])


fig.add_annotation(
    go.layout.Annotation(
        text="@iamfrankjuarez",
        x=0.999,  
        y=1.006, 
        showarrow=False,
        font=dict(size=10, color='white'),  
    )
)

fig.update_layout(
    title=f'Uso del bullpen {team_choice} - Últimos 7 días',
    title_x=0.30,
    font=dict(size=12),
    width=800,
    height=800,
    margin=dict(l=3, r=3, t=30, b=9)
)

st.plotly_chart(fig)
