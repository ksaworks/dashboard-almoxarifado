import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Importa módulo de ML
from ml_predictions import (
    MLPredictor, 
    create_prediction_charts, 
    create_cost_prediction_chart,
    create_anomaly_chart,
    create_criticality_chart
)

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Análise de Almoxarifado",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    
    /* Estilização das abas (tabs) */
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 10px 20px;
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f3f4f6;
        color: #111827 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ef4444 !important;
        color: white !important;
    }
    
    /* Estilização dos cards de métrica */
    [data-testid="stMetricValue"] {
        color: #1f2937 !important;
        font-weight: 600 !important;
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #4b5563 !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #6b7280 !important;
    }
    
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .insight-box {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 10px 0;
        color: #1e40af;
    }
    .warning-box {
        background: #fff3e0;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 10px 0;
        color: #92400e;
    }
    .success-box {
        background: #e8f5e9;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 10px 0;
        color: #065f46;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown("""
    <div style='text-align: center; padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0;'>🤖 Dashboard de Análise</h1>
        <p style='color: white; opacity: 0.9; margin: 10px 0 0 0;'>
            Sistema Inteligente de Gestão, Manutenção de Almoxarifado com Machine Learning
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📁 Upload de Dados")
    
    uploaded_file = st.file_uploader(
        "Carregar arquivo Excel ou CSV",
        type=['xlsx', 'xls', 'csv'],
        help="Faça upload do arquivo de solicitações"
    )
    
    if uploaded_file:
        st.success(f"✓ {uploaded_file.name}")
    
    st.markdown("---")
    
    # Configurações de ML
    st.markdown("### 🤖 Configurações Machine Learning")
    prediction_months = st.slider(
        "Meses para previsão",
        min_value=3,
        max_value=12,
        value=6,
        help="Quantidade de meses futuros para prever"
    )
    
    show_confidence = st.checkbox("Mostrar intervalos de confiança", value=True)
    
    st.markdown("---")
    st.markdown("### 📌 Sobre o Projeto")
    st.info("""
        Dashboard com Machine Learning para:
        - 🔮 Previsões de demanda
        - 📊 Detecção de anomalias
        - 🎯 Análise de criticidade
        - 💡 Insights automáticos
        - 📈 Tendências futuras
    """)
    
    st.markdown("---")
    st.markdown("**Desenvolvido com:**")
    st.markdown("• Python & Streamlit")
    st.markdown("• Scikit-learn")
    st.markdown("• Prophet (Meta)")
    st.markdown("• Plotly")


# Funções auxiliares
def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def validate_dataframe(df):
    """Valida se o DataFrame tem as colunas necessárias"""
    required_columns = ['Mês/Ano', 'Total', 'Solicitante', '2- Máquina de destino:', 
                       '6- Descrição da peça: ', '7- Quantidade de peças.']
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, missing_columns
    
    return True, []

# Processamento de dados
if uploaded_file is not None:
    try:
        # Lê o arquivo baseado na extensão
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            # Tenta diferentes encodings para CSV
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                uploaded_file.seek(0)  # Volta ao início do arquivo
                try:
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                except:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='iso-8859-1')
        else:
            df = pd.read_excel(uploaded_file)
        
        # Valida as colunas
        is_valid, missing_cols = validate_dataframe(df)
        
        if not is_valid:
            st.error(f"""
                ❌ **Erro: Colunas obrigatórias não encontradas!**
                
                **Colunas faltando:**
                {', '.join([f'`{col}`' for col in missing_cols])}
                
                **Colunas encontradas no arquivo:**
                {', '.join([f'`{col}`' for col in df.columns.tolist()])}
                
                **Dica:** Verifique se o arquivo está no formato correto ou renomeie as colunas.
            """)
            st.stop()
        
        # Inicializa preditor ML
        predictor = MLPredictor(df)
        
        # Tabs principais
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📈 Temporal", 
            "🤖 Previsões com IA", 
            "⚠️ Anomalias", 
            "👥 Solicitantes", 
            "🔧 Máquinas", 
            "📦 Peças", 
            "✅ Entregas", 
            "💰 Financeiro"
        ])
        
        # TAB 1: ANÁLISE TEMPORAL
        with tab1:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div class='metric-card'>
                        <h3 style='margin:0; font-size:0.9em;'>Total de Solicitações</h3>
                        <h2 style='margin:10px 0 0 0;'>{len(df):,}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_month = len(df) / len(df['Mês/Ano'].unique())
                st.markdown(f"""
                    <div class='metric-card'>
                        <h3 style='margin:0; font-size:0.9em;'>Média Mensal</h3>
                        <h2 style='margin:10px 0 0 0;'>{avg_month:.0f}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Calcula tendência
                trend, interpretation, slope = predictor.calculate_trend()
                trend_emoji = "📈" if slope > 0 else "📉" if slope < 0 else "➡️"
                st.markdown(f"""
                    <div class='metric-card'>
                        <h3 style='margin:0; font-size:0.9em;'>Tendência {trend_emoji}</h3>
                        <h2 style='margin:10px 0 0 0; font-size:1.2em;'>{trend}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            # Insight automático
            st.markdown(f"""
                <div class='insight-box'>
                    <strong>💡 Insight Automático:</strong> {interpretation}
                </div>
            """, unsafe_allow_html=True)
            
            # Análise mensal
            df_month = df.groupby('Mês/Ano').agg({
                'Mês/Ano': 'count',
                'Total': 'sum'
            }).rename(columns={'Mês/Ano': 'Quantidade'})
            
            # Ordena cronologicamente
            df_month['Data_Sort'] = pd.to_datetime(df_month.index, format='%m-%Y')
            df_month = df_month.sort_values('Data_Sort')
            
            fig = px.line(df_month, y='Quantidade', 
                         title='Evolução Mensal de Solicitações',
                         markers=True)
            fig.update_traces(line_color='#667eea', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
            
            fig2 = px.bar(df_month, y='Total',
                         title='Custo Total por Mês',
                         color_discrete_sequence=['#764ba2'])
            st.plotly_chart(fig2, use_container_width=True)
        
        # TAB 2: PREVISÕES COM IA
        with tab2:
            st.markdown("## 🔮 Previsões Inteligentes")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### Previsão de Solicitações")
                
                # Faz previsões
                df_month, predictions, future_dates, scores = predictor.predict_next_months(
                    months=prediction_months
                )
                
                # Cria gráfico
                fig = create_prediction_charts(df_month, predictions, future_dates, scores)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 Modelos Utilizados")
                
                for name, score in scores.items():
                    st.metric(
                        name,
                        f"{score:.2%}",
                        help=f"R² Score: {score:.4f}"
                    )
                
                # Melhor modelo
                best_model = max(scores, key=scores.get)
                st.markdown(f"""
                    <div class='success-box'>
                        <strong>✅ Melhor Modelo:</strong><br>
                        {best_model}<br>
                        Acurácia: {scores[best_model]:.2%}
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Previsão de custos
            st.markdown("### 💰 Previsão de Custos")
            
            df_month_cost, pred_costs, future_dates_cost, cost_score = predictor.predict_costs(
                months=prediction_months
            )
            
            fig_cost = create_cost_prediction_chart(df_month_cost, pred_costs, future_dates_cost)
            st.plotly_chart(fig_cost, use_container_width=True)
            
            # Resumo financeiro
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_predicted = sum(pred_costs)
                st.metric(
                    f"Custo Previsto ({prediction_months} meses)",
                    format_currency(total_predicted)
                )
            
            with col2:
                avg_predicted = total_predicted / prediction_months
                st.metric(
                    "Média Mensal Prevista",
                    format_currency(avg_predicted)
                )
            
            with col3:
                current_avg = df_month_cost['Total'].mean()
                diff = ((avg_predicted - current_avg) / current_avg) * 100
                st.metric(
                    "Variação Esperada",
                    f"{diff:+.1f}%",
                    delta=f"{diff:+.1f}%"
                )
            
            # Tabela de previsões
            st.markdown("### 📋 Tabela de Previsões Detalhadas")
            
            pred_df = pd.DataFrame({
                'Mês': [d.strftime('%m-%Y') for d in future_dates],
                'Solicitações Previstas (Gradient Boosting)': predictions['Gradient Boosting'].astype(int),
                'Custo Previsto': [format_currency(c) for c in pred_costs]
            })
            
            st.dataframe(pred_df, use_container_width=True)
        
        # TAB 3: DETECÇÃO DE ANOMALIAS
        with tab3:
            st.markdown("## ⚠️ Detecção Inteligente de Anomalias")
            
            df_month_anom, anomalies = predictor.identify_anomalies()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Anomalias Detectadas", len(anomalies))
            
            with col2:
                if len(anomalies) > 0:
                    max_anom = anomalies['Quantidade'].max()
                    st.metric("Pico Anômalo", f"{max_anom:.0f}")
                else:
                    st.metric("Pico Anômalo", "N/A")
            
            with col3:
                normal_mean = df_month_anom[~df_month_anom['Is_Anomaly']]['Quantidade'].mean()
                st.metric("Média Normal", f"{normal_mean:.0f}")
            
            # Gráfico de anomalias
            fig_anom = create_anomaly_chart(df_month_anom, anomalies)
            st.plotly_chart(fig_anom, use_container_width=True)
            
            # Lista de anomalias
            if len(anomalies) > 0:
                st.markdown("### 📊 Períodos com Comportamento Anômalo")
                
                for idx, row in anomalies.iterrows():
                    st.markdown(f"""
                        <div class='warning-box'>
                            <strong>📅 {idx}</strong><br>
                            Solicitações: {row['Quantidade']:.0f} 
                            (Z-Score: {row['Z_Score']:.2f})<br>
                            <em>Valor {abs(row['Z_Score']):.1f} desvios padrão acima/abaixo da média</em>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Nenhuma anomalia significativa detectada!")
        
        # TAB 4: SOLICITANTES
        with tab4:
            df_sol = df.groupby('Solicitante').agg({
                'Solicitante': 'count',
                'Total': ['sum', 'mean']
            }).round(2)
            df_sol.columns = ['Quantidade', 'Custo Total', 'Custo Médio']
            df_sol = df_sol.sort_values('Quantidade', ascending=False)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Solicitantes", len(df_sol))
            with col2:
                st.metric("Mais Ativo", df_sol.index[0])
            with col3:
                top_custo = df_sol.sort_values('Custo Total', ascending=False).index[0]
                st.metric("Maior Custo", top_custo)
            
            fig = px.bar(df_sol.head(15), x='Quantidade', 
                        orientation='h',
                        title='Top 15 Solicitantes por Quantidade',
                        color='Quantidade',
                        color_continuous_scale='Purples')
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_sol.head(50), use_container_width=True)
        
        # TAB 5: MÁQUINAS COM CRITICIDADE
        with tab5:
            st.markdown("## 🔧 Análise de Criticidade de Máquinas")
            
            df_machine_crit = predictor.predict_maintenance_demand()
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                high_crit = len(df_machine_crit[df_machine_crit['Criticidade'] == 'Alta'])
                st.metric("Máquinas Alta Criticidade", high_crit, 
                         delta="Requerem atenção", delta_color="inverse")
            
            with col2:
                medium_crit = len(df_machine_crit[df_machine_crit['Criticidade'] == 'Média'])
                st.metric("Criticidade Média", medium_crit)
            
            with col3:
                low_crit = len(df_machine_crit[df_machine_crit['Criticidade'] == 'Baixa'])
                st.metric("Baixa Criticidade", low_crit,
                         delta="Estáveis", delta_color="normal")
            
            # Gráfico de dispersão
            fig_crit = create_criticality_chart(df_machine_crit)
            st.plotly_chart(fig_crit, use_container_width=True)
            
            # Lista de máquinas críticas
            st.markdown("### ⚠️ Máquinas que Requerem Atenção Especial")
            
            high_machines = df_machine_crit[df_machine_crit['Criticidade'] == 'Alta'].head(10)
            
            for machine, row in high_machines.iterrows():
                st.markdown(f"""
                    <div class='warning-box'>
                        <strong>🔧 {machine}</strong><br>
                        Solicitações: {row['Solicitacoes']:.0f} | 
                        Custo Total: {format_currency(row['Custo_Total'])} | 
                        Custo Médio: {format_currency(row['Custo_Medio'])}
                    </div>
                """, unsafe_allow_html=True)
            
            st.dataframe(df_machine_crit, use_container_width=True)
        
        # TAB 6: PEÇAS COM PREVISÃO DE DEMANDA
        with tab6:
            st.markdown("## 📦 Análise de Peças com Previsão de Demanda")
            
            df_parts_pred = predictor.predict_part_demand()
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Tipos de Peças", len(df_parts_pred))
            
            with col2:
                top_part = df_parts_pred.index[0]
                st.metric("Mais Solicitada", top_part[:30] + "...")
            
            with col3:
                total_demand = df_parts_pred['Taxa_Mensal'].sum()
                st.metric("Demanda Mensal Total", f"{total_demand:.0f} unidades")
            
            # Top peças com previsão
            st.markdown("### 📊 Top 20 Peças - Previsão de Demanda")
            
            top_parts = df_parts_pred.head(20).reset_index()
            
            fig_parts = go.Figure()
            
            fig_parts.add_trace(go.Bar(
                y=top_parts['6- Descrição da peça: '].str[:40],
                x=top_parts['Taxa_Mensal'],
                name='Taxa Mensal Atual',
                orientation='h',
                marker_color='#667eea'
            ))
            
            fig_parts.add_trace(go.Bar(
                y=top_parts['6- Descrição da peça: '].str[:40],
                x=top_parts['Previsao_3_Meses'],
                name='Previsão 3 Meses',
                orientation='h',
                marker_color='#4ecdc4',
                opacity=0.7
            ))
            
            fig_parts.update_layout(
                title='Comparação: Consumo Atual vs Previsão',
                barmode='group',
                height=600
            )
            
            st.plotly_chart(fig_parts, use_container_width=True)
            
            # Tabela detalhada
            st.markdown("### 📋 Tabela de Previsões por Peça")
            
            display_df = df_parts_pred.head(50).reset_index()
            display_df.columns = ['Peça', 'Qtd Total', 'Freq. Solicitação', 
                                  'Taxa Mensal', 'Prev. 3 Meses', 'Prev. 6 Meses']
            
            st.dataframe(display_df, use_container_width=True)
            
            # Recomendações de estoque
            st.markdown("### 💡 Recomendações Inteligentes de Estoque")
            
            high_demand = df_parts_pred[df_parts_pred['Taxa_Mensal'] > df_parts_pred['Taxa_Mensal'].quantile(0.75)].head(5)
            
            for part, row in high_demand.iterrows():
                st.markdown(f"""
                    <div class='insight-box'>
                        <strong>📦 {part[:60]}</strong><br>
                        • Consumo mensal: {row['Taxa_Mensal']:.1f} unidades<br>
                        • Recomendação: Manter estoque de {row['Previsao_3_Meses']:.0f} unidades 
                        (3 meses)<br>
                        • Status: <strong>Alta Demanda</strong> - Priorizar reposição
                    </div>
                """, unsafe_allow_html=True)
        
        # TAB 7: ENTREGAS
        with tab7:
            df_entrega = df['Entregue?'].value_counts().reset_index()
            df_entrega.columns = ['Status', 'Quantidade']
            
            fig = px.pie(df_entrega, values='Quantidade', names='Status',
                        title='Distribuição de Entregas por Status',
                        color_discrete_sequence=px.colors.sequential.Purp)
            st.plotly_chart(fig, use_container_width=True)
            
            entregues = df[df['Entregue?'].str.contains('Sim', na=False)].shape[0]
            taxa = (entregues / len(df) * 100)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Taxa de Entrega", f"{taxa:.1f}%")
            with col2:
                st.metric("Entregues", entregues)
            with col3:
                st.metric("Pendentes", len(df) - entregues)
            
            # Análise de performance
            if taxa >= 90:
                st.markdown("""
                    <div class='success-box'>
                        <strong>✅ Excelente Performance!</strong><br>
                        Taxa de entrega acima de 90%. Continue assim!
                    </div>
                """, unsafe_allow_html=True)
            elif taxa >= 70:
                st.markdown("""
                    <div class='insight-box'>
                        <strong>⚡ Boa Performance</strong><br>
                        Taxa de entrega satisfatória. Pequenos ajustes podem melhorar.
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class='warning-box'>
                        <strong>⚠️ Atenção Necessária</strong><br>
                        Taxa de entrega abaixo do ideal. Recomenda-se análise detalhada.
                    </div>
                """, unsafe_allow_html=True)
        
        # TAB 8: FINANCEIRO
        with tab8:
            custo_total = df['Total'].sum()
            custo_medio = df['Total'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Custo Total", format_currency(custo_total))
            with col2:
                st.metric("Custo Médio", format_currency(custo_medio))
            with col3:
                custo_mensal_medio = custo_total / len(df['Mês/Ano'].unique())
                st.metric("Média Mensal", format_currency(custo_mensal_medio))
            
            df_financeiro = df.groupby('Mês/Ano')['Total'].sum().reset_index()
            
            # Ordena cronologicamente
            df_financeiro['Data_Sort'] = pd.to_datetime(df_financeiro['Mês/Ano'], format='%m-%Y')
            df_financeiro = df_financeiro.sort_values('Data_Sort')
            
            fig = px.line(df_financeiro, x='Mês/Ano', y='Total',
                         title='Evolução dos Custos Mensais',
                         markers=True)
            fig.update_traces(line_color='#667eea', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
            
            # Análise de distribuição de custos
            st.markdown("### 💰 Distribuição de Custos por Máquina")
            
            df_machine_cost = df.groupby('2- Máquina de destino:')['Total'].sum().sort_values(ascending=False).head(10)
            
            fig_dist = px.pie(
                values=df_machine_cost.values,
                names=df_machine_cost.index,
                title='Top 10 Máquinas - Distribuição de Custos'
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            
            st.dataframe(df_financeiro, use_container_width=True)
        
        # Rodapé com insights gerais
        st.markdown("---")
        st.markdown("## 🎯 Insights Gerais do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class='insight-box'>
                    <h4>📊 Análise Concluída</h4>
                    <p><strong>Registros processados:</strong> {}</p>
                    <p><strong>Período analisado:</strong> {} meses</p>
                    <p><strong>Máquinas monitoradas:</strong> {}</p>
                    <p><strong>Tipos de peças:</strong> {}</p>
                </div>
            """.format(
                len(df),
                len(df['Mês/Ano'].unique()),
                df['2- Máquina de destino:'].nunique(),
                df['6- Descrição da peça: '].nunique()
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class='success-box'>
                    <h4>🤖 IA e Machine Learning</h4>
                    <p><strong>✓</strong> Previsões para {} meses</p>
                    <p><strong>✓</strong> Detecção de anomalias ativa</p>
                    <p><strong>✓</strong> Análise de criticidade concluída</p>
                    <p><strong>✓</strong> Recomendações de estoque geradas</p>
                </div>
            """.format(prediction_months), unsafe_allow_html=True)
    
    except KeyError as e:
        st.error(f"""
            ❌ **Erro: Coluna não encontrada no arquivo!**
            
            A coluna **{str(e)}** não foi encontrada no arquivo enviado.
            
            **Colunas encontradas no seu arquivo:**
            {', '.join([f'`{col}`' for col in df.columns.tolist()])}
            
            **Colunas necessárias:**
            - `Mês/Ano`
            - `Total`
            - `Solicitante`
            - `2- Máquina de destino:`
            - `6- Descrição da peça: `
            - `7- Quantidade de peças.`
            
            **Dica:** Verifique se os nomes das colunas estão corretos ou renomeie-as no arquivo.
        """)
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")
        st.exception(e)

else:
    # Tela inicial quando não há arquivo
    st.markdown("## 👋 Bem-vindo ao Dashboard Inteligente!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class='insight-box'>
                <h3>🤖 Recursos de IA</h3>
                <ul>
                    <li>Previsão de demanda futura</li>
                    <li>Detecção automática de anomalias</li>
                    <li>Análise de criticidade de máquinas</li>
                    <li>Recomendações inteligentes</li>
                    <li>Insights automáticos</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='success-box'>
                <h3>📊 Análises Disponíveis</h3>
                <ul>
                    <li>Análise temporal detalhada</li>
                    <li>Performance por solicitante</li>
                    <li>Monitoramento de máquinas</li>
                    <li>Controle de estoque</li>
                    <li>Análise financeira completa</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("👆 **Faça upload de um arquivo Excel (.xlsx, .xls) ou CSV (.csv) na barra lateral para começar a análise**")
    
    # Exemplo de estrutura esperada
    st.markdown("### 📋 Estrutura Esperada do Arquivo")
    
    st.markdown("""
        **Colunas Obrigatórias:**
        - `Mês/Ano` - Formato: MM-AAAA (ex: 01-2024, 02-2024)
        - `Solicitante` - Nome do solicitante
        - `2- Máquina de destino:` - Nome da máquina
        - `6- Descrição da peça: ` - Descrição da peça solicitada
        - `7- Quantidade de peças.` - Quantidade numérica
        - `Total` - Valor total (numérico)
        - `Entregue?` - Status da entrega (opcional)
    """)
    
    exemplo_df = pd.DataFrame({
        'Mês/Ano': ['01-2024', '02-2024'],
        'Solicitante': ['João Silva', 'Maria Santos'],
        '2- Máquina de destino:': ['Máquina A', 'Máquina B'],
        '6- Descrição da peça: ': ['Peça X', 'Peça Y'],
        '7- Quantidade de peças.': [5, 3],
        'Total': [150.50, 200.00],
        'Entregue?': ['Sim, João', 'Sim, Maria']
    })
    
    st.dataframe(exemplo_df, use_container_width=True)
    
    st.markdown("""
        **💡 Dica para arquivos CSV:**
        - Use vírgula (`,`) como separador
        - Codificação recomendada: UTF-8
        - Se tiver problemas com acentos, tente encoding Latin-1
    """)

# Rodapé
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Dashboard de Análise de Almoxarifado</strong></p>
        <p>Desenvolvido com Python, Streamlit, Scikit-learn e Prophet</p>
        <p>🤖 Machine Learning | 📊 Data Science | 💡 Business Intelligence</p>
    </div>
""", unsafe_allow_html=True)