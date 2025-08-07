import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import plotly.graph_objs as go
import pandas as pd

# Inicializar o app
app = dash.Dash(__name__)
app.title = "Análise Crypto"

# Lista de moedas para exibir
crypto_ids = ['bitcoin', 'ethereum', 'solana', 'cardano', 'ripple', 'dogecoin']
crypto_names = {
    'bitcoin': 'Bitcoin',
    'ethereum': 'Ethereum',
    'solana': 'Solana',
    'cardano': 'Cardano',
    'ripple': 'Ripple',
    'dogecoin': 'Dogecoin'
}

def get_crypto_data():
    url = (
        f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
        f'&ids={",".join(crypto_ids)}&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    )
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data)

# Layout do Dashboard com tema escuro
app.layout = html.Div([
    html.H1('📊 Análises de Criptomoedas', style={'textAlign': 'center', 'color': 'white'}),
    dcc.Interval(id='interval-atualizacao', interval=60*1000, n_intervals=0),  # Atualiza a cada 60 segundos

    html.Div(id='tabela-dados'),

    html.H2('📈 Gráfico de Preços', style={'marginTop': '40px', 'textAlign': 'center', 'color': 'white'}),
    dcc.Dropdown(
        id='dropdown-moeda',
        options=[{'label': crypto_names[c], 'value': c} for c in crypto_ids],
        value='bitcoin',
        style={
            'width': '50%',
            'margin': 'auto',
            'backgroundColor': '#222',
            'color': 'white'
        }
    ),
    dcc.Graph(id='grafico-preco')
], style={'fontFamily': 'Arial', 'padding': '30px', 'backgroundColor': '#111'})


@app.callback(
    Output('tabela-dados', 'children'),
    Input('interval-atualizacao', 'n_intervals')
)
def atualizar_tabela(n):
    df = get_crypto_data()
    table_header = [
        html.Tr([
            html.Th('Criptomoeda'),
            html.Th('Preço (USD)'),
            html.Th('Variação 24h (%)'),
            html.Th('Volume 24h'),
            html.Th('Market Cap')
        ])
    ]

    table_rows = []
    for _, row in df.iterrows():
        cor = 'limegreen' if row['price_change_percentage_24h'] >= 0 else 'tomato'
        table_rows.append(html.Tr([
            html.Td(crypto_names.get(row['id'], row['id'])),
            html.Td(f"${row['current_price']:,}"),
            html.Td(f"{row['price_change_percentage_24h']:.2f}%", style={'color': cor}),
            html.Td(f"${row['total_volume']:,}"),
            html.Td(f"${row['market_cap']:,}")
        ]))

    return html.Table(
        table_header + table_rows,
        style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'color': 'white',
            'backgroundColor': '#222',
            'border': '1px solid #333',
            'textAlign': 'center',
            'marginTop': '20px'
        }
    )


@app.callback(
    Output('grafico-preco', 'figure'),
    Input('dropdown-moeda', 'value')
)
def atualizar_grafico(moeda_id):
    # Consulta histórico de 7 dias
    url = f"https://api.coingecko.com/api/v3/coins/{moeda_id}/market_chart?vs_currency=usd&days=7"
    response = requests.get(url)
    data = response.json()

    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['price'],
        mode='lines',
        name=crypto_names.get(moeda_id, moeda_id)
    ))

    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Preço (USD)',
        template='plotly_dark',
        height=500
    )

    return fig


if __name__ == '__main__':
    app.run(debug=True)

