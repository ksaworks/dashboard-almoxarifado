"""
Módulo de Machine Learning para Previsões
Dashboard de Análise de Peças
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from prophet import Prophet
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class MLPredictor:
    """Classe para previsões com Machine Learning"""
    
    def __init__(self, df):
        self.df = df
        self.models = {}
        self.predictions = {}
        
    def prepare_temporal_data(self):
        """Prepara dados temporais para previsão"""
        # Agrupa por mês
        df_month = self.df.groupby('Mês/Ano').agg({
            'Mês/Ano': 'count',
            'Total': 'sum'
        }).rename(columns={'Mês/Ano': 'Quantidade'})
        
        # Converte para datetime
        df_month['Data'] = pd.to_datetime(df_month.index, format='%m-%Y')
        df_month = df_month.sort_values('Data')
        df_month['Mes_Num'] = range(len(df_month))
        
        return df_month
    
    def predict_next_months(self, months=6):
        """Prevê quantidade de solicitações para os próximos meses"""
        df_month = self.prepare_temporal_data()
        
        # Features
        X = df_month[['Mes_Num']].values
        y = df_month['Quantidade'].values
        
        # Treina múltiplos modelos
        models = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        predictions = {}
        scores = {}
        
        for name, model in models.items():
            # Treina
            model.fit(X, y)
            
            # Score no conjunto de treino
            scores[name] = model.score(X, y)
            
            # Prevê próximos meses
            future_months = np.arange(len(df_month), len(df_month) + months).reshape(-1, 1)
            pred = model.predict(future_months)
            predictions[name] = pred
            
            self.models[name] = model
        
        # Gera datas futuras
        last_date = df_month['Data'].max()
        future_dates = [last_date + timedelta(days=30*i) for i in range(1, months+1)]
        
        return df_month, predictions, future_dates, scores
    
    def predict_costs(self, months=6):
        """Prevê custos para os próximos meses"""
        df_month = self.prepare_temporal_data()
        
        X = df_month[['Mes_Num']].values
        y = df_month['Total'].values
        
        # Modelo de previsão de custos
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Prevê
        future_months = np.arange(len(df_month), len(df_month) + months).reshape(-1, 1)
        pred_costs = model.predict(future_months)
        
        last_date = df_month['Data'].max()
        future_dates = [last_date + timedelta(days=30*i) for i in range(1, months+1)]
        
        return df_month, pred_costs, future_dates, model.score(X, y)
    
    def prophet_forecast(self, periods=6):
        """Previsão usando Prophet (Facebook)"""
        df_month = self.prepare_temporal_data()
        
        # Prepara dados para Prophet
        df_prophet = pd.DataFrame({
            'ds': df_month['Data'],
            'y': df_month['Quantidade']
        })
        
        # Treina modelo
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )
        model.fit(df_prophet)
        
        # Faz previsão
        future = model.make_future_dataframe(periods=periods, freq='M')
        forecast = model.predict(future)
        
        return forecast, model
    
    def identify_anomalies(self):
        """Identifica anomalias nos dados"""
        df_month = self.prepare_temporal_data()
        
        # Calcula estatísticas
        mean_qty = df_month['Quantidade'].mean()
        std_qty = df_month['Quantidade'].std()
        
        # Identifica outliers (além de 2 desvios padrão)
        df_month['Is_Anomaly'] = np.abs(df_month['Quantidade'] - mean_qty) > (2 * std_qty)
        df_month['Z_Score'] = (df_month['Quantidade'] - mean_qty) / std_qty
        
        anomalies = df_month[df_month['Is_Anomaly']]
        
        return df_month, anomalies
    
    def predict_maintenance_demand(self):
        """Prevê demanda de manutenção por máquina"""
        # Análise por máquina
        df_machine = self.df.groupby('2- Máquina de destino:').agg({
            '2- Máquina de destino:': 'count',
            'Total': ['sum', 'mean']
        })
        df_machine.columns = ['Solicitacoes', 'Custo_Total', 'Custo_Medio']
        df_machine = df_machine.sort_values('Solicitacoes', ascending=False)
        
        # Classifica criticidade
        q75 = df_machine['Solicitacoes'].quantile(0.75)
        q50 = df_machine['Solicitacoes'].quantile(0.50)
        
        def classify_criticality(value):
            if value >= q75:
                return 'Alta'
            elif value >= q50:
                return 'Média'
            else:
                return 'Baixa'
        
        df_machine['Criticidade'] = df_machine['Solicitacoes'].apply(classify_criticality)
        
        return df_machine
    
    def predict_part_demand(self):
        """Prevê demanda futura de peças"""
        # Análise de peças
        df_parts = self.df.groupby('6- Descrição da peça: ').agg({
            '7- Quantidade de peças.': 'sum',
            '6- Descrição da peça: ': 'count'
        })
        df_parts.columns = ['Qtd_Total', 'Freq_Solicitacao']
        df_parts = df_parts.sort_values('Qtd_Total', ascending=False)
        
        # Calcula taxa de consumo médio mensal
        num_months = len(self.df['Mês/Ano'].unique())
        df_parts['Taxa_Mensal'] = df_parts['Qtd_Total'] / num_months
        df_parts['Previsao_3_Meses'] = df_parts['Taxa_Mensal'] * 3
        df_parts['Previsao_6_Meses'] = df_parts['Taxa_Mensal'] * 6
        
        return df_parts
    
    def calculate_trend(self):
        """Calcula tendência geral"""
        df_month = self.prepare_temporal_data()
        
        # Regressão linear para tendência
        X = df_month[['Mes_Num']].values
        y = df_month['Quantidade'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        slope = model.coef_[0]
        
        if slope > 0:
            trend = "Crescente"
            interpretation = f"Aumento médio de {abs(slope):.1f} solicitações por mês"
        elif slope < 0:
            trend = "Decrescente"
            interpretation = f"Redução média de {abs(slope):.1f} solicitações por mês"
        else:
            trend = "Estável"
            interpretation = "Sem variação significativa"
        
        return trend, interpretation, slope


def create_prediction_charts(df_month, predictions, future_dates, scores):
    """Cria gráficos de previsões"""
    
    # Gráfico principal com múltiplas previsões
    fig = go.Figure()
    
    # Dados históricos
    fig.add_trace(go.Scatter(
        x=df_month['Data'],
        y=df_month['Quantidade'],
        mode='lines+markers',
        name='Histórico',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))
    
    # Previsões de cada modelo
    colors = {'Linear Regression': '#ff6b6b', 'Random Forest': '#4ecdc4', 
              'Gradient Boosting': '#f7b731'}
    
    for name, pred in predictions.items():
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=pred,
            mode='lines+markers',
            name=f'{name} (R²={scores[name]:.3f})',
            line=dict(color=colors[name], width=2, dash='dash'),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title='Previsão de Solicitações - Próximos 6 Meses',
        xaxis_title='Data',
        yaxis_title='Quantidade de Solicitações',
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    return fig


def create_cost_prediction_chart(df_month, pred_costs, future_dates):
    """Cria gráfico de previsão de custos"""
    fig = go.Figure()
    
    # Histórico
    fig.add_trace(go.Bar(
        x=df_month['Data'],
        y=df_month['Total'],
        name='Custo Histórico',
        marker_color='#667eea'
    ))
    
    # Previsão
    fig.add_trace(go.Bar(
        x=future_dates,
        y=pred_costs,
        name='Previsão de Custo',
        marker_color='#ff6b6b',
        opacity=0.7
    ))
    
    fig.update_layout(
        title='Previsão de Custos - Próximos 6 Meses',
        xaxis_title='Data',
        yaxis_title='Custo Total (R$)',
        height=500,
        showlegend=True
    )
    
    return fig


def create_anomaly_chart(df_month, anomalies):
    """Cria gráfico de detecção de anomalias"""
    fig = go.Figure()
    
    # Dados normais
    normal_data = df_month[~df_month['Is_Anomaly']]
    fig.add_trace(go.Scatter(
        x=normal_data['Data'],
        y=normal_data['Quantidade'],
        mode='lines+markers',
        name='Normal',
        line=dict(color='#4ecdc4', width=2),
        marker=dict(size=8)
    ))
    
    # Anomalias
    if len(anomalies) > 0:
        fig.add_trace(go.Scatter(
            x=anomalies['Data'],
            y=anomalies['Quantidade'],
            mode='markers',
            name='Anomalia',
            marker=dict(size=15, color='#ff6b6b', symbol='star')
        ))
    
    fig.update_layout(
        title='Detecção de Anomalias nas Solicitações',
        xaxis_title='Data',
        yaxis_title='Quantidade',
        height=400
    )
    
    return fig


def create_criticality_chart(df_machine):
    """Cria gráfico de criticidade de máquinas"""
    criticality_colors = {'Alta': '#ff6b6b', 'Média': '#f7b731', 'Baixa': '#4ecdc4'}
    
    fig = px.scatter(
        df_machine.reset_index().head(30),
        x='Solicitacoes',
        y='Custo_Total',
        size='Custo_Medio',
        color='Criticidade',
        hover_data=['2- Máquina de destino:'],
        title='Análise de Criticidade das Máquinas',
        labels={'Solicitacoes': 'Número de Solicitações', 
                'Custo_Total': 'Custo Total (R$)'},
        color_discrete_map=criticality_colors,
        height=500
    )
    
    return fig