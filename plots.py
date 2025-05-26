import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot
from data_garmin_slicer import devider
import datetime


def generate_plot_week_activity(data):
    """Generates plot with activities from last week"""
    df = pd.DataFrame(data)
    df['date'] = df['date_time'].dt.date

    latest_date = df['date'].max()
    start_of_week = latest_date - pd.Timedelta(days=6)
    date_range = pd.date_range(start_of_week, latest_date).date

    activity_types = df['activity_type'].unique()
    full_grid = pd.MultiIndex.from_product([date_range, activity_types], names=['date', 'activity_type']).to_frame(index=False)

    daily_sessions = df.groupby(['date', 'activity_type'])['duration'].sum().reset_index()
    daily_sessions['duration_hours'] = daily_sessions['duration'] / 3600
    
    daily_sessions['duration_str'] = daily_sessions['duration'].apply(devider)

    merged = pd.merge(full_grid, daily_sessions, on=['date', 'activity_type'], how='left').fillna({
        'duration': 0,
        'duration_hours': 0,
        'duration_str': '0:00'})


    traces = []
    for activity in merged['activity_type'].unique():
        activity_data = merged[merged['activity_type'] == activity]
        traces.append(go.Scatter(
            x=activity_data['date'],
            y=activity_data['duration_hours'],
            mode='lines+markers+text',
            name=activity,
            text=activity_data.apply(lambda row: row['duration_str'] if row['duration'] > 0 else '', axis=1),
            textposition='top center',
            hoverinfo='text+x+y',
            hovertemplate=f'Date: %{{x}}<br>Duration: %{{y:.1f}} hours (%{{text}})<br>Activity: {activity}<extra></extra>'
        ))

    layout = go.Layout(
        title='Weekly Activity Focus (One Line per Sport)',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Duration (hours)', tickformat='.1f'),
        template='plotly_dark',
        width=800 )

    fig = go.Figure(data=traces, layout=layout)

    # Convert the Plotly figure to HTML
    plot_html = plot(fig, include_plotlyjs='cdn', output_type='div')
    return plot_html

def generate_bar_chart_calories(data):
    """Generates a plot with calories burnt weekly"""
    df = pd.DataFrame(data)
    df['date_time'] = pd.to_datetime(df['date_time']) 
    df['date'] = df['date_time'].dt.date
    df_calories = df.groupby('date', as_index=False)['calories'].sum()
    df_calories['date'] = df_calories['date'].astype(str)

    trace = go.Bar(
        x=df_calories['date'],
        y=df_calories['calories'],
        name='Calories Burnt',
        marker=dict(color='red'), 
        hoverinfo='x+y',
        hovertemplate='Date: %{x|%b %d}<br>Calories Burnt: %{y}<extra></extra>')

    layout = go.Layout(
        title='Daily Calories Burnt',
        xaxis=dict(title='Date', tickformat='%b %d'),
        yaxis=dict(title='Calories Burnt'),
        template='plotly_dark',
        width=600
    )

    fig = go.Figure(data=[trace], layout=layout)
    plot_html = plot(fig, include_plotlyjs='cdn', output_type='div')
    return plot_html


def generate_weekly_activites_plot(data):
    """Generates a plot with three months activities"""
    df = pd.DataFrame(data)
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['week_start'] = df['date_time'].dt.to_period('W').dt.start_time

    latest_date = df['date_time'].max().date()
    start_of_three_months = latest_date - pd.DateOffset(months=3)
    date_range = pd.date_range(start=start_of_three_months, end=latest_date, freq='W').to_series().dt.to_period('W').dt.start_time.unique()

    activity_types = df['activity_type'].unique()
    full_grid = pd.MultiIndex.from_product([date_range, activity_types], names=['week_start', 'activity_type']).to_frame(index=False)

    weekly_sessions = df.groupby(['week_start', 'activity_type'])['duration'].sum().reset_index()
    weekly_sessions['duration_hours'] = weekly_sessions['duration'] / 3600
    weekly_sessions['duration_str'] = weekly_sessions['duration'].apply(devider)

    merged = pd.merge(full_grid, weekly_sessions, on=['week_start', 'activity_type'], how='left').fillna({
        'duration': 0,
        'duration_hours': 0,
        'duration_str': '0:00'
    })

    traces = []
    for activity in merged['activity_type'].unique():
        activity_data = merged[merged['activity_type'] == activity]
        traces.append(go.Scatter(
            x=activity_data['week_start'],
            y=activity_data['duration_hours'],
            mode='lines+markers+text',
            name=activity,
            # text=activity_data.apply(lambda row: row['duration_str'] if row['duration_hours'] > 0 else '', axis=1),
            textposition='top center',
            hoverinfo='text+x+y',
            hovertemplate=f'Week Start: %{{x|%Y-%m-%d}}<br>Duration: %{{y:.1f}} hours (%{{text}})<br>Activity: {activity}<extra></extra>'))

    layout = go.Layout(
        title='Weekly Activity Focus',
        xaxis=dict(title='Week Start', tickformat='%b %d'),
        yaxis=dict(title='Duration (hours)', tickformat='.1f'),
        template='plotly_dark',
        width=1400)

    fig = go.Figure(data=traces, layout=layout)

    plot_html = plot(fig, include_plotlyjs='cdn', output_type='div')
    return plot_html


