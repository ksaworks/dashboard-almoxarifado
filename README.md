# Dashboard de almoxarifado

Aplicação em Python para analisar solicitações de materiais de manutenção. O objetivo é reunir consumo, custos e frequência de pedidos por máquina e por solicitante em uma interface que permita explorar os dados e observar tendências.

O projeto utiliza **Streamlit** para a interface, **pandas** para tratamento dos dados e **Plotly** para os gráficos. O arquivo `ml_predictions.py` reúne as rotinas de previsão e identificação de anomalias.

## Funcionalidades

- Importação de planilhas Excel e arquivos CSV.
- Análise de solicitações e custos ao longo do tempo.
- Agrupamento de gastos e quantidade de pedidos por máquina ou solicitante.
- Classificação de criticidade com base na frequência de solicitações.
- Identificação estatística de meses com consumo fora do padrão.
- Projeções exploratórias de demanda e custos para os próximos meses.

As previsões utilizam regressão linear, Random Forest, Gradient Boosting e Prophet, conforme a rotina. São recursos de análise exploratória, não estimativas de economia comprovada.

## Estrutura

- `app.py`: aplicação Streamlit, leitura dos arquivos, filtros e apresentação dos resultados.
- `ml_predictions.py`: preparação das séries, modelos de previsão, anomalias e gráficos.
- `requirements.txt`: dependências Python.
- `fake.py`: apoio à geração de dados de exemplo.

## Execução local

Com Python e `pip` instalados:

```bash
git clone https://github.com/ksaworks/dashboard-almoxarifado.git
cd dashboard-almoxarifado
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

No Windows, ative o ambiente com `.venv\Scripts\activate`.

A aplicação abre no navegador e permite carregar um CSV ou uma planilha Excel.

## Dados esperados

O arquivo precisa conter as seguintes colunas, inclusive a pontuação e os espaços usados nos nomes:

| Coluna | Uso |
| --- | --- |
| `Mês/Ano` | Referência temporal |
| `Solicitante` | Quem solicitou o material |
| `2- Máquina de destino:` | Equipamento associado ao pedido |
| `6- Descrição da peça: ` | Descrição do item (inclui espaço ao final) |
| `7- Quantidade de peças.` | Quantidade solicitada |
| `Total` | Valor do pedido |

O campo `Entregue?` é opcional. O código contém uma rotina de validação das colunas necessárias.

## Limitações

As métricas de ajuste dos modelos são calculadas sobre os dados usados no treinamento. Por isso, não devem ser interpretadas como acurácia validada em produção. Para uso em decisões de compra, seria necessário avaliar os resultados com dados históricos separados para teste e considerar sazonalidade, mudanças de operação e qualidade dos registros.

Este repositório apresenta um projeto de análise de dados em Python; não é uma API backend.
