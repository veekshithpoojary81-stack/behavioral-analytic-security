"""
Dashboard chart generation using Plotly.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_login_hour_distribution(df: pd.DataFrame):
    fig = px.histogram(df, x='hour', nbins=24, title="Login Hour Distribution",
                       color_discrete_sequence=['#00cc96'])
    fig.update_layout(template="plotly_dark")
    return fig

def plot_daily_login_trend(df: pd.DataFrame):
    daily = df.set_index('login_time').resample('D').size().reset_index(name='count')
    fig = px.line(daily, x='login_time', y='count', title="Daily Login Trend",
                  color_discrete_sequence=['#636efa'])
    fig.update_layout(template="plotly_dark")
    return fig

def plot_success_failed_pie(df: pd.DataFrame):
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    fig = px.pie(status_counts, names='status', values='count', title="Success vs Failed",
                 color='status', color_discrete_map={'Success': '#00cc96', 'Failed': '#ef553b'})
    fig.update_layout(template="plotly_dark")
    return fig

def plot_risk_distribution(risk_df: pd.DataFrame):
    if 'risk_level' not in risk_df.columns:
        return go.Figure()
    counts = risk_df['risk_level'].value_counts().reset_index()
    counts.columns = ['risk_level', 'count']
    fig = px.bar(counts, x='risk_level', y='count', title="Risk Level Distribution",
                 color='risk_level', color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(template="plotly_dark")
    return fig

def plot_top_suspicious_users(risk_df: pd.DataFrame):
    if 'is_anomaly' not in risk_df.columns:
        return go.Figure()
    suspicious = risk_df[risk_df['is_anomaly']].groupby('user_id').size().reset_index(name='anomaly_count')
    suspicious = suspicious.sort_values('anomaly_count', ascending=False).head(10)
    fig = px.bar(suspicious, x='user_id', y='anomaly_count', title="Top Suspicious Users",
                 color_discrete_sequence=['#ab63fa'])
    fig.update_layout(template="plotly_dark")
    return fig

def plot_hour_heatmap(df: pd.DataFrame):
    # Pivot user vs hour
    pivot = df.groupby(['user_id', 'hour']).size().reset_index(name='count')
    heatmap_data = pivot.pivot(index='user_id', columns='hour', values='count').fillna(0)
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        colorbar=dict(title='Login Count')
    ))
    fig.update_layout(title="Login Hour Heatmap by User", template="plotly_dark")
    return fig

def plot_anomalies_scatter(login_data: pd.DataFrame):
    # Use PCA to reduce features for visualization
    from sklearn.decomposition import PCA
    features = login_data[['hour', 'is_failed', 'total_logins', 'weekday']].fillna(0)
    pca = PCA(n_components=2)
    components = pca.fit_transform(features)
    plot_df = pd.DataFrame(components, columns=['PC1', 'PC2'])
    plot_df['ml_anomaly'] = login_data.get('ml_anomaly', 'Normal')
    fig = px.scatter(plot_df, x='PC1', y='PC2', color='ml_anomaly',
                     title="ML Anomaly Detection (PCA projection)",
                     color_discrete_map={'Normal': '#00cc96', 'Suspicious': '#ef553b'})
    fig.update_layout(template="plotly_dark")
    return fig