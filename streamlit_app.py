import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load the data
rp_grid_with_teams = pd.read_csv('rp_grid_active_pitchers_sorted.csv')

# Select the last 6 columns for the dates (excluding 'team_name', 'player_name', and 'Total_Pitches')
date_columns = rp_grid_with_teams.columns[2:-1]  # Assuming the last column is 'Total_Pitches'
date_columns_reversed = date_columns[::-1]

# Filter out players who haven't pitched in the last 6 days
rp_grid_active_pitchers = rp_grid_with_teams.loc[
    ~(rp_grid_with_teams[date_columns_reversed] == 0).all(axis=1),  # '~' is the negation operator
    ['team_name', 'player_name'] + list(date_columns_reversed) + ['Lanzamientos Totales']
]

# Reset the index for the clean DataFrame
rp_grid_active_pitchers.reset_index(drop=True, inplace=True)

# Define the team color map
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

# Create a dropdown for team selection
team_choice = st.selectbox('Selecciona un equipo:', rp_grid_active_pitchers['team_name'].unique())

# Filter data for the selected team
team_data = rp_grid_active_pitchers[rp_grid_active_pitchers['team_name'] == team_choice]

# Remove columns (days) where all pitchers for the selected team have 0 values
team_data = team_data.loc[:, (team_data != 0).any(axis=0)]

# Extract date columns for dynamic plotting (after filtering out zero days)
date_columns_team = team_data.columns[2:-1]  # Assuming the first two columns are team_name and player_name, last is Total_Pitches

# Prepare the headers and cell values for the Plotly table (including Total_Pitches)
headers = ['RP'] + [str(col) for col in date_columns_team] + ['Lanzamientos Totales']

# Function to make non-zero values bold
def format_cells_for_bold(team_data, columns):
    formatted_cells = []
    for col in columns:
        formatted_column = []
        for value in team_data[col]:
            if value != 0:
                formatted_column.append(f"<b>{value}</b>")  # Make non-zero values bold
            else:
                formatted_column.append(f"{value}")  # Keep zero values normal
        formatted_cells.append(formatted_column)
    return formatted_cells

# Format the cells with bold for non-zero values (including Total Pitches)
cells = [team_data['player_name']] + format_cells_for_bold(team_data, date_columns_team) + [team_data['Lanzamientos Totales']]

# Get the team's color from the map
team_color = team_color_map.get(team_choice, '#ffffff')  # Default to white if team not found

# Create the table figure using Plotly
fig = go.Figure(data=[go.Table(
    header=dict(values=headers, fill_color=team_color, align='center',
                font=dict(size=12, color='beige')),
    cells=dict(values=cells, fill_color='#a19174', align='center', format=['html'],
               font=dict(size=12, family='Verdana', color='black'))  # Use 'html' to format bold text
)])

# Add watermark annotation in the lower right corner
fig.add_annotation(
    go.layout.Annotation(
        text="@iamfrankjuarez",
        x=0.999,  # Adjust X position for watermark (closer to 1 for the right edge)
        y=1.006,  # Adjust Y position for watermark (closer to 0 for the bottom edge)
        showarrow=False,
        font=dict(size=10, color='white'),  # Adjust font size and color
    )
)

# Update layout for the figure
fig.update_layout(
    title=f'Uso del bullpen {team_choice} - Últimos 7 días',
    title_x=0.30,
    font=dict(size=12),
    width=800,
    height=800,
    margin=dict(l=5, r=5, t=30, b=5)
)

# Display the figure in Streamlit
st.plotly_chart(fig)
