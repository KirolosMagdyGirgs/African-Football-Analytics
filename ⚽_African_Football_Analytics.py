import pandas as pd
import re
import math
import numpy as np
from scipy import stats
import streamlit as st
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
from highlight_text import fig_text
import textwrap


# Set up the page
st.set_page_config(page_title=' African Football Analytics', layout='centered', page_icon='⚽')

# Sidebar branding
st.sidebar.image("Afican football analytics logo.png", width=300)  # replace with local or URL path
st.sidebar.markdown(
    "<h1 style='margin-center: 0;'>African Football Analytics</h1>",
    unsafe_allow_html=True
)




# Sidebar - League Selector + Minutes Filter
st.sidebar.title('Filters')

league_option = st.sidebar.selectbox(
    "Select League",
    ["Egyptian Premier League", "South African PSL"]
)

minutes_var = st.sidebar.number_input("Minimum Minutes Played", value=400, step=50)
apply_button = st.sidebar.button("Apply Filter")
position_group_params = {
                'Goalkeepers': ['GK Successful Distribution p90 Percentile', 'Successful Launches p90 Percentile',
                                'Clean Sheets p90 Percentile', 'Goals Conceded p90 Percentile',
                                'Goals Conceded Inside Box p90 Percentile', 'Penalties Saved p90 Percentile',
                                'Catches p90 Percentile', 'Punches p90 Percentile', 'Saves Made p90 Percentile',
                                'Saves Made from Inside Box p90 Percentile'],

                'Full Backs': ['Goal Assists p90 Percentile', 'Chances Created p90 Percentile',
                               'Successful Crosses open play p90 Percentile',
                               'Successful Crosses & Corners p90 Percentile','Through balls p90 Percentile', 'ProgressivePasses p90 Percentile',
                               'FinalThirdPasses p90 Percentile', 'Tackles Won p90 Percentile',
                               'Total Clearances p90 Percentile', 'Interceptions p90 Percentile',
                               'Recoveries p90 Percentile','Blocks p90 Percentile', 'Duels won % p90 Percentile',
                               'Total Fouls Won p90 Percentile','Touches p90 Percentile','Total Fouls Conceded p90 Percentile','Yellow Cards p90 Percentile' ,
                               'Total Red Cards p90 Percentile'],

                'Center Backs': ['Total Clearances p90 Percentile', 'Interceptions p90 Percentile',
                                 'Recoveries p90 Percentile', 'Tackles Won p90 Percentile','Blocked Shots p90 Percentile','Blocks p90 Percentile',
                                 'Aerial Duels won p90 Percentile', 'Ground Duels won p90 Percentile',
                                 'Clean Sheets p90 Percentile', 'Goals Conceded Inside Box p90 Percentile',
                                 'Goals Conceded p90 Percentile', 'Open Play Pass Success % p90 Percentile',
                                 'ProgressivePasses p90 Percentile', 'FinalThirdPasses p90 Percentile','Successful Long Passes p90 Percentile',
                                 'Yellow Cards p90 Percentile' ,'Total Red Cards p90 Percentile','Total Fouls Conceded p90 Percentile',
                                 'Set Pieces Goals p90 Percentile'
                                 ],

                'Midfielders': ['Goals p90 Percentile','Attempts from Set Pieces p90 Percentile', 'Goal Assists p90 Percentile',
                                'Second Goal Assists p90 Percentile',
                                'Open Play Pass Success % p90 Percentile', 'Through balls p90 Percentile',
                                'FinalThirdPasses p90 Percentile', 'ProgressivePasses p90 Percentile',
                                'Chances Created p90 Percentile','Successful Crosses & Corners p90 Percentile', 'Touches p90 Percentile',
                                'Dribbles success % p90 Percentile', 'Dispossessed p90 Percentile',
                                'Duels won % p90 Percentile', 'Tackles Won p90 Percentile',
                                'Recoveries p90 Percentile', 'Times Tackled p90 Percentile'
                                ,'Total Fouls Conceded p90 Percentile'],

                'Wingers': ['Goals p90 Percentile', 'Goal Assists p90 Percentile','Second Goal Assists p90 Percentile', 'Chances Created p90 Percentile',
                            'Successful Crosses & Corners p90 Percentile','Successful Crosses open play p90 Percentile', 'ProgressivePasses p90 Percentile',
                            'FinalThirdPasses p90 Percentile', 'Touches p90 Percentile',
                            'Total Touches In Opposition Box p90 Percentile', 'Dribbles success % p90 Percentile',
                            'Overruns p90 Percentile', 'Dispossessed p90 Percentile', 'Total Fouls Won p90 Percentile',
                            'Attempts from Set Pieces p90 Percentile', 'Total Shots p90 Percentile', 'Shots On Target ( inc goals ) p90 Percentile'
                            ],

                'Strikers': ['Goals p90 Percentile', 'Headed Goals p90 Percentile', 'Goal Assists p90 Percentile',
                             'Successful Lay-offs p90 Percentile', 'Chances Created p90 Percentile',
                             'ProgressivePasses p90 Percentile', 'Total Shots p90 Percentile',
                             'Shots On Target ( inc goals ) p90 Percentile', 'Shots Per Goal p90 Percentile',
                             'Conversion Rate p90 Percentile','Set Pieces Goals p90 Percentile','Minutes Per Goal Percentile','Winning Goal p90 Percentile'
                             , 'Total Touches In Opposition Box p90 Percentile','Aerial Duels won p90 Percentile', 'Ground Duels won p90 Percentile',
                             'Offsides p90 Percentile']
            }

# Load and cache data
def load_data(league_name, minutes):
    file_map = {
        "Egyptian Premier League": "Player Season Stats - EPL.xlsx",
        "South African PSL": "Player Season Stats - PSL.xlsx"
    }
    file_path = f"{file_map[league_name]}"
    df = pd.read_excel(file_path)
    df = df[df['Time Played'] >= minutes]
    return df
# Compute percentiles
def compute_percentiles(df):
    exclude_columns = ['index', 'Player Id', 'Full Name', 'Match Name', 'Team Name', 'Team Id', 'Last Updated', '90s',
                       'Most Played Position', 'Positions Played', 'Number of Positions Played',
                       'Position Group', 'position']
    exclude_columns = [col for col in exclude_columns if col in df.columns]
    
    stat_columns = [col for col in df.columns if col not in exclude_columns]

   


    negative_stats = negative_stats = [
    'Minutes Per Goal', 'Aerial Duels lost', 'Aerial Duels lost p90', 'Dispossessed', 'Dispossessed p90', 
    'Duels lost', 'Duels lost p90', 'Ground Duels lost', 'Ground Duels lost p90', 'Handballs conceded', 
    'Hit Woodwork', 'Hit Woodwork p90', 'Offsides', 'Offsides p90', 'Overruns', 'Overruns p90', 
    'Foul Attempted Tackle', 'Foul Attempted Tackle p90', 'GK Unsuccessful Distribution', 
    'GK Unsuccessful Distribution p90', 'Goals Conceded', 'Goals Conceded p90', 
    'Goals Conceded Outside Box', 'Goals Conceded Outside Box p90', 'Goals Conceded Inside Box', 
    'Goals Conceded Inside Box p90', 'Own Goal Scored', 'Own Goal Scored p90', 
    'Penalties Conceded', 'Penalties Conceded p90', 'Red Cards - 2nd Yellow', 'Red Cards - 2nd Yellow p90', 
    'Straight Red Cards', 'Straight Red Cards p90', 'Total Red Cards', 'Total Red Cards p90', 
    'Total Unsuccessful Passes ( Excl Crosses & Corners )', 
    'Total Unsuccessful Passes ( Excl Crosses & Corners ) p90', 'Unsuccessful Corners into Box', 
    'Unsuccessful Corners into Box p90', 'Unsuccessful Crosses & Corners', 
    'Unsuccessful Crosses & Corners p90', 'Unsuccessful Crosses open play', 
    'Unsuccessful Crosses open play p90', 'Unsuccessful Dribbles', 'Unsuccessful Dribbles p90', 
    'Unsuccessful Launches', 'Unsuccessful Launches p90', 'Unsuccessful Long Passes', 
    'Unsuccessful Long Passes p90', 'Unsuccessful Passes Opposition Half', 
    'Unsuccessful Passes Opposition Half p90', 'Unsuccessful Passes Own Half', 
    'Unsuccessful Passes Own Half p90', 'Unsuccessful Short Passes', 
    'Unsuccessful Short Passes p90', 'Unsuccessful lay-offs', 'Unsuccessful lay-offs p90', 
    'Yellow Cards', 'Yellow Cards p90', 'Substitute Off', 'Substitute Off p90', 
    'Tackles Lost', 'Tackles Lost p90', 'Total Fouls Conceded', 'Total Fouls Conceded p90', 
    'Total Losses Of Possession', 'Shots Off Target (inc woodwork)', 'Goals Conceded Inside Box p90','Goals Conceded Outside Box p90',
    'Shots Off Target (inc woodwork) p90', 'Shots Per Goal', 'Shots Per Goal p90','Handballs conceded','Handballs conceded p90','Hit Woodwork p90','Hit Woodwork',
    'Total Unsuccessful Passes ( Excl Crosses & Corners ) p90','Total Unsuccessful Passes ( Excl Crosses & Corners )'
        ]
    percentile_data = {}
    for group in df['Position Group'].dropna().unique():
        group_df = df[df['Position Group'] == group]
        for stat in stat_columns:
            if stat not in group_df.columns:
                continue
            scores = group_df[stat].dropna()
            if len(scores) == 0:
                continue
            if stat in negative_stats:
                percentiles = group_df[stat].apply(lambda x: 100 - math.floor(stats.percentileofscore(scores, x)))
            else:
                percentiles = group_df[stat].apply(lambda x: math.floor(stats.percentileofscore(scores, x)))
            for idx, value in percentiles.items():
                percentile_data.setdefault(idx, {})[f"{stat} Percentile"] = value

    percentile_df = pd.DataFrame.from_dict(percentile_data, orient='index')
    percentile_df = percentile_df.reindex(df.index)
    return pd.concat([df, percentile_df], axis=1)

if apply_button:
    df = load_data(league_option, minutes_var)
    df = compute_percentiles(df)
    st.session_state.df = df
    st.session_state.df_loaded = True

if st.session_state.get("df_loaded", False):
    df = st.session_state.df
    st.markdown(f"### 📋 {league_option} - Season 24/25")
    st.markdown(f"### 📅 Data as of 10-05-2025")
    tab1, tab2, tab3, tab4 = st.tabs([
        "Pizza Chart (Single Player)",
        "Pizza Chart (Comparison)",
        "Player Total Stats",
        "Player Per 90 Stats"
    ])

    with tab1:
        st.write("## Player Pizza Chart")

        # Step 1: Select Position Group
        position_groups = sorted(df['Position Group'].dropna().unique())
        position_group_var = st.selectbox("Select a position group:", position_groups)

        # Step 2: Filter by position group, then get teams
        pos_filtered_df = df[df['Position Group'] == position_group_var]
        teams = sorted(set(t for sub in pos_filtered_df['Team Name'].dropna().str.split(', ') for t in sub))

        # Step 3: Select team
        team_name_var = st.selectbox("Select a team:", teams)

        # Step 4: Filter by team
        filtered_df = pos_filtered_df[pos_filtered_df['Team Name'].str.contains(team_name_var, na=False)]

        # Step 5: Select player
        player_name_var = st.selectbox("Select a player:", filtered_df['Match Name'].sort_values().unique())

        if st.button("Show Chart"):
            player_row = filtered_df[filtered_df['Match Name'] == player_name_var].iloc[0]
            position_group = player_row['Position Group']
            params = position_group_params.get(position_group)

            if not params:
                st.warning("No defined metrics for this position group.")
            else:
                values = [int(player_row[p]) if pd.notna(player_row[p]) else 0 for p in params]
                readable_params = [
                    "\n".join(textwrap.wrap(
                        re.sub(r"([A-Z])", r" \1", p.replace(' p90 Percentile', '')).strip(), width=14
                    )) for p in params
                ]

                font_normal = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf')
                baker = PyPizza(
                    params=readable_params,
                    background_color="#0e1117",
                    straight_line_color="#F2F2F2",
                    straight_line_lw=1,
                    last_circle_color="#F2F2F2",
                    last_circle_lw=1.5,
                    other_circle_lw=1,
                    inner_circle_size=5
                )

                fig, ax = baker.make_pizza(
                    values,
                    figsize=(10, 10.5),
                    color_blank_space="same",
                    slice_colors=['#1A78CF'] * len(values),
                    value_colors=['#F2F2F2'] * len(values),
                    value_bck_colors=['#1A78CF'] * len(values),
                    blank_alpha=0.4,
                    kwargs_slices=dict(edgecolor="#F2F2F2", zorder=2, linewidth=1),
                    kwargs_params=dict(color="#F2F2F2", fontsize=14, fontproperties=font_normal.prop, va="center"),
                    kwargs_values=dict(
                        color="#F2F2F2", fontsize=14,
                        fontproperties=font_normal.prop, zorder=3,
                        bbox=dict(edgecolor="#F2F2F2", facecolor="cornflowerblue", boxstyle="round,pad=0.05", lw=1)
                    )
                )

                num_params = len(readable_params)
                for i, text in enumerate(ax.texts[:num_params]):
                    angle = 360 * i / num_params
                    x, y = text.get_position()
                    text.set_position((x, y + 6))  # Adjust label position

                fig.text(0.515, 0.97, f'{player_name_var} - {team_name_var} - {int(player_row["Time Played"])} mins',
                        size=20, ha="center", color="#F2F2F2")
                fig.text(0.515, 0.942, f'Per 90 Percentile Rank vs {position_group} (Minimum {minutes_var} Minutes Played) | 24/25',
                        size=15, ha="center", color="#F2F2F2")
                fig.text(0.99, 0.005, "Data: Opta\nInspired by: McKay Johns", size=14, color="#F2F2F2", ha="right")
                fig.text(0.03, 0.005, "Twitter: African Football Analytics", size=14, color="#F2F2F2", ha="left")

                st.pyplot(fig)

                with st.expander("Metric Glossary"):
                    st.write("""
                    - **Progressive Passes**: A pass that moves the ball closer to the opponent goal by 25% & at least 5m vertically.
                    - **Second Assist**: The last action before an assist.
                    - **Lay-off**: A pass by a striker with back to goal played to a teammate.
                    - **Overrun**: Heavy touch in a dribble.
                    - **Dispossessed**: Losing possession under pressure.
                    - **Blocks**: A blocked pass or cross.
                    """)



    with tab2:
        st.write("## Player Comparison Pizza Chart")

        teams = sorted(set(t for sub in df['Team Name'].dropna().str.split(', ') for t in sub))
        position_groups = sorted(df['Position Group'].dropna().unique())

        position_group_var = st.selectbox("Select position group:", position_groups)

        team1 = st.selectbox("Select first player's team:", teams, index=0)
        player1_df = df[(df['Team Name'].str.contains(team1)) & (df['Position Group'] == position_group_var)]
        player1 = st.selectbox("Select first player:", player1_df['Match Name'].sort_values().unique())

        team2 = st.selectbox("Select second player's team:", teams, index=1)
        player2_df = df[(df['Team Name'].str.contains(team2)) & (df['Position Group'] == position_group_var)]
        player2 = st.selectbox("Select second player:", player2_df['Match Name'].sort_values().unique())

       
        if st.button("Compare Players"):
            params = position_group_params.get(position_group_var)
            if not params:
                st.warning("No defined metrics for this position group.")
            else:
                row1 = player1_df[player1_df['Match Name'] == player1].iloc[0]
                row2 = player2_df[player2_df['Match Name'] == player2].iloc[0]

                values1 = [int(row1[p]) if pd.notna(row1[p]) else 0 for p in params]
                values2 = [int(row2[p]) if pd.notna(row2[p]) else 0 for p in params]

                readable_params = [
                    "\n".join(textwrap.wrap(
                        re.sub(r"([A-Z])", r" \1", p.replace(' p90 Percentile', '')).strip(), width=14 # witdth determines the space allowed for the label
                    )) for p in params
                ]
                font_normal = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf')

                baker = PyPizza(
                    params=readable_params,
                    background_color="#0e1117",
                    straight_line_color="#F2F2F2",
                    straight_line_lw=1,
                    last_circle_color="#F2F2F2",
                    last_circle_lw=1.5,
                    other_circle_lw=1,
                    inner_circle_size=5
                )

                fig, ax = baker.make_pizza(
                    values1,
                    compare_values=values2,
                    figsize=(10, 10.5),
                    color_blank_space="same",
                    blank_alpha=0.4,
                    param_location=104,
                    kwargs_slices=dict(edgecolor="#F2F2F2", zorder=2, linewidth=1),
                    kwargs_compare=dict(facecolor="#ff9300", edgecolor="#222222", zorder=3, linewidth=1),
                    kwargs_params=dict(color="#F2F2F2", fontsize=14, fontproperties=font_normal.prop, va="center"),
                    kwargs_values=dict(
                        color="#F2F2F2", fontsize=14,
                        fontproperties=font_normal.prop, zorder=3,
                        bbox=dict(edgecolor="#F2F2F2", facecolor="cornflowerblue", boxstyle="round,pad=0.1", lw=1)
                    ),
                    kwargs_compare_values=dict(
                        color="#F2F2F2", fontsize=12,
                        fontproperties=font_normal.prop, zorder=3,
                        bbox=dict(edgecolor="#F2F2F2", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1)
                    )
                )
                 # 🔧 Adjust parameter label positions based on angle
                num_params = len(readable_params)
                for i, text in enumerate(ax.texts[:num_params]):  # Only stat labels, not value texts
                    angle = 360 * i / num_params

                    # Move labels outward or inward slightly
                    x, y = text.get_position()
                    if 90 <= angle <= 270:  # Top half
                        text.set_position((x, y + 6))
                    else:  # Bottom half
                        text.set_position((x, y + 6))


                fig_text(
                0.515, 0.97,
                f'<{player1}> <({int(row1["Time Played"])})> vs <{player2}> <({int(row2["Time Played"])})>',
                size=20,
                highlight_textprops=[
                    {"color": '#1A78CF'},     # player1 name
                    {"color": '#1A78CF'},     # player1 minutes
                    {"color": '#FF9300'},     # player2 name
                    {"color": '#FF9300'}      # player2 minutes
                ],
                ha="center", color="#F2F2F2", ax=ax, fig=fig
                )

                fig.text(
                    0.515, 0.923,
                    f'Per 90 Percentile Rank vs {position_group_var} (Minimum {minutes_var} Minutes Played) | 24/25',
                    size=15, ha="center", color="#F2F2F2"
                )

                fig.text(
                    0.99, 0.005,
                    "Data: Opta\nInspired by: McKay Johns",
                    size=14, color="#F2F2F2", ha="right"
                )

                fig.text(
                    0.03, 0.005,
                    "Twitter : African Football Analytics",
                    size=14, color="#F2F2F2", ha="left"
                )

                st.pyplot(fig)

                with st.expander("Metric Glossary"):
                    st.write("""
                    - **Progressive Passes**: A pass that moves the ball closer to the opponent goal by 25% & at least 5m vertically.
                    - **Second Assist**: The last action before an assist.
                    - **Lay-off**: A pass by a striker with back to goal played to a teammate.
                    - **Overrun**: Heavy touch in a dribble.
                    - **Dispossessed**: Losing possession under pressure.
                    - **Blocks**: A blocekd pass or cross.
                    """)
    with tab3:
        st.write("## Players Total Stats Table")

        # Filter out p90 stats and remove 'last Updated' (keep Percentiles)
        total_columns = [
            col for col in df.columns
            if 'p90' not in col and 'Percentile' not in col and col != 'Last Updated'
        ]
        percentile_columns = [col for col in df.columns if 'Percentile' in col and 'p90' not in col]

        # Ordered stat → stat + percentile
        stat_base_names = sorted([
            col for col in total_columns if col not in [
                'index', 'Player Id', 'Full Name', 'Match Name', 'Team Name',
                'Team Id', '90s', 'Most Played Position',
                'Positions Played', 'Number of Positions Played',
                'Position Group', 'position', 'Time Played'
            ]
        ])

        ordered_cols = []
        for stat in stat_base_names:
            ordered_cols.append(stat)
            perc = f"{stat} Percentile"
            if perc in percentile_columns:
                ordered_cols.append(perc)

        # Always show identifying columns
        identifying_cols = ['Match Name', 'Team Name', 'Position Group', 'Time Played', '90s']
        final_cols = identifying_cols + ordered_cols
        full_df = df[final_cols].copy()

        # Filters: Position Group → Team → Player → Stats
        position_groups = sorted(set(pos for sub in full_df['Position Group'].dropna().str.split(', ') for pos in sub))
        pos = st.selectbox("Select Position Group", position_groups)

        filtered_df = full_df[full_df['Position Group'].str.contains(pos, na=False)]

        teams = sorted(set(t for sub in filtered_df['Team Name'].dropna().str.split(', ') for t in sub))
        selected_team = st.selectbox("Select Team", ["All"] + teams)

        if selected_team != "All":
            filtered_df = filtered_df[filtered_df['Team Name'].str.contains(selected_team, na=False)]

        players = sorted(filtered_df['Match Name'].unique())
        selected_player = st.selectbox("Select Player", ["All"] + players)

        if selected_player != "All":
            filtered_df = filtered_df[filtered_df['Match Name'] == selected_player]

        # Select stats to display
        available_stats = [col for col in ordered_cols if 'Percentile' not in col]
        selected_stats = st.multiselect("Select Stats to Display", available_stats, default=available_stats)

        # Build final display
        selected_cols = []
        for stat in selected_stats:
            selected_cols.append(stat)
            perc = f"{stat} Percentile"
            if perc in filtered_df.columns:
                selected_cols.append(perc)

        display_df = filtered_df[identifying_cols + selected_cols]

        if st.button("Show Total Stats"):
            percentile_cols = [col for col in display_df.columns if 'Percentile' in col]
            styled_df = display_df.style.background_gradient(subset=percentile_cols, cmap='RdYlGn')
            st.dataframe(styled_df, height=750)

            with st.expander("Metric Glossary"):
                st.write("""
                - **Overrun**: Heavy touch in a dribble.
                - **Progressive Passes**: A pass that moves the ball closer to the opponent goal by 25% & at least 5 m vertically.
                - **Second Assist**: The last action before an assist.
                - **Lay-off**: A pass by a striker who has received the ball with back to goal.
                - **Dispossessed**: Losing the ball under pressure.
                - **GK Distribution**: Successful goalkeeper passes.
                - **GK Launches**: Long balls launched forward.
                - **Other Goals**: Goals not scored with foot or head.
                """)


    with tab4:
        st.write("## Players Per 90 Stats Table")

        # Filter only p90 stats + their percentiles
        p90_stats = [col for col in df.columns if 'p90' in col and 'Percentile' not in col]
        percentile_columns = [f"{col} Percentile" for col in p90_stats if f"{col} Percentile" in df.columns]

        stat_base_names = sorted(p90_stats)

        ordered_cols = []
        for stat in stat_base_names:
            ordered_cols.append(stat)
            perc = f"{stat} Percentile"
            if perc in percentile_columns:
                ordered_cols.append(perc)

        identifying_cols = ['Match Name', 'Team Name', 'Position Group', 'Time Played', '90s']
        final_cols = identifying_cols + ordered_cols
        full_df = df[final_cols].copy()

        # Filters
        position_groups = sorted(set(pos for sub in full_df['Position Group'].dropna().str.split(', ') for pos in sub))
        pos = st.selectbox("Select Position Group", position_groups, key="p90_group")

        filtered_df = full_df[full_df['Position Group'].str.contains(pos, na=False)]

        teams = sorted(set(t for sub in filtered_df['Team Name'].dropna().str.split(', ') for t in sub))
        selected_team = st.selectbox("Select Team", ["All"] + teams, key="p90_team")

        if selected_team != "All":
            filtered_df = filtered_df[filtered_df['Team Name'].str.contains(selected_team, na=False)]

        players = sorted(filtered_df['Match Name'].unique())
        selected_player = st.selectbox("Select Player", ["All"] + players, key="p90_player")

        if selected_player != "All":
            filtered_df = filtered_df[filtered_df['Match Name'] == selected_player]

        # Stat selection
        available_stats = [col for col in ordered_cols if 'Percentile' not in col]
        selected_stats = st.multiselect("Select Stats to Display", available_stats, default=available_stats, key="p90_stats")

        selected_cols = []
        for stat in selected_stats:
            selected_cols.append(stat)
            perc = f"{stat} Percentile"
            if perc in filtered_df.columns:
                selected_cols.append(perc)

        display_df = filtered_df[identifying_cols + selected_cols]

        if st.button("Show p90 Stats"):
            percentile_cols = [col for col in display_df.columns if 'Percentile' in col]
            p90_cols = [col for col in selected_cols if 'Percentile' not in col]
            styled_df = display_df.style \
                .background_gradient(subset=percentile_cols, cmap='RdYlGn') \
                .format(subset=p90_cols + ['90s'], formatter="{:.2f}")
            st.dataframe(styled_df, height=750)

            with st.expander("Metric Glossary"):
                st.write("""
                - **Overrun**: Heavy touch in a dribble.
                - **Progressive Passes**: A pass that moves the ball closer to the opponent goal by 25% & at least 5 m vertically.
                - **Second Assist**: The last action before an assist.
                - **Lay-off**: A pass by a striker who has received the ball with back to goal.
                - **Dispossessed**: Losing the ball under pressure.
                - **GK Distribution**: Successful goalkeeper passes.
                - **GK Launches**: Long balls launched forward.
                - **Other Goals**: Goals not scored with foot or head.
                """)
else:
    st.info("👈Please apply league and minutes filters from the sidebar to load data.")
