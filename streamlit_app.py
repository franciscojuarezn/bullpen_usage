import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re  

rp_grid_with_teams = pd.read_csv('rp_pivot_merged.csv').drop(columns=['Lanzamientos Totales'])

date_columns = rp_grid_with_teams.columns[2:]

date_columns_reversed = date_columns[::-1]
last_7_dates = date_columns_reversed[:7]

rp_grid_active_pitchers = rp_grid_with_teams.loc[
    ~(rp_grid_with_teams[last_7_dates] == '0').all(axis=1),
    ['team_name', 'player_name'] + list(last_7_dates)
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

logo_and_title = """
    <div style="display: flex; align-items: center;">
        <img src="https://www.lmp.mx/assets/img/header/logo_80_aniversary.webp" alt="LMP Logo" width="40" height="40">
        <h1 style="margin-left: 20px; font-size: 30px;">Bullpen LMP</h1>
    </div>
"""

st.markdown(logo_and_title, unsafe_allow_html=True)
st.divider()

team_choice = st.selectbox('Selecciona un equipo:', rp_grid_active_pitchers['team_name'].unique())

team_data = rp_grid_active_pitchers[rp_grid_active_pitchers['team_name'] == team_choice]

non_date_columns = ['player_name']

date_columns_team = [col for col in team_data.columns if col not in ['team_name'] + non_date_columns]

cols_to_keep_in_dates = (team_data[date_columns_team] != '0').any(axis=0)
date_cols_to_keep = cols_to_keep_in_dates[cols_to_keep_in_dates].index.tolist()

cols_to_keep = non_date_columns + date_cols_to_keep

team_data = team_data[cols_to_keep]

date_columns_team = [col for col in team_data.columns if col not in non_date_columns]

def extract_total_pitches(cell_value):
    """Extract the total number of pitches from a cell value (e.g., '15P 9 6B<br>0ER 1H')."""
    match = re.search(r'(\d+)P', str(cell_value))
    return int(match.group(1)) if match else 0

team_data['Lanzamientos Totales'] = team_data[date_columns_team].apply(lambda row: sum(extract_total_pitches(x) for x in row), axis=1)

# team_data.loc[team_data['player_name'] == 'Denny Roman', 'Lanzamientos Totales'] = 17

team_data = team_data.sort_values(by='Lanzamientos Totales', ascending=False)

headers = ['RP'] + date_columns_team + ['Lanzamientos Totales']

def format_cells_with_bold_numbers(team_data, columns):
    formatted_cells = []
    for col in columns:
        formatted_column = []
        for value in team_data[col]:
            if value != '0':
                value_with_bold_numbers = re.sub(r'(\d+)', r'<b>\1</b>', value)
                formatted_column.append(value_with_bold_numbers)
            else:
                formatted_column.append(f"{value}")
        formatted_cells.append(formatted_column)
    return formatted_cells

cells = [team_data['player_name'].tolist()] + format_cells_with_bold_numbers(team_data, date_columns_team) + [team_data['Lanzamientos Totales'].tolist()]

team_color = team_color_map.get(team_choice, '#ffffff')

fig = go.Figure(data=[go.Table(
    header=dict(
        values=headers,
        fill_color=team_color,
        align='center',
        font=dict(size=13, color='beige')
    ),
    cells=dict(
        values=cells,
        fill_color='#a19174',
        align='center',
        format=['html'] * len(headers),
        font=dict(size=10   , family='Verdana', color='black')
    )
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
    title=f'Uso del bullpen {team_choice} - Última semana',
    title_x=0.30,
    font=dict(size=12),
    width=None,
    height=800,
    margin=dict(l=1, r=1, t=30, b=5)
)

st.plotly_chart(fig)
