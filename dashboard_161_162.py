# @title
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import socket
import requests
# Carregar a base consolidada


# URL do arquivo no GitHub
url = 'https://github.com/WallasBorges10/Dashboard-161-162/raw/refs/heads/main/base_consolidada_cnt.xlsx'

# Nome do arquivo para salvar temporariamente
file_path = 'base_consolidada_cnt.xlsx'

# Baixar o arquivo usando requests
response = requests.get(url)
with open(file_path, 'wb') as file:
    file.write(response.content)

# Ler o arquivo Excel
df = pd.read_excel(file_path, sheet_name='Planilha1')

# Remover espaços extras nas colunas
df.columns = df.columns.str.strip()

# Renomear colunas
rename_columns = {
    '3 - 1. Sexo do entrevistado:': 'Sexo',
    '4 - 2. Idade do entrevistado:': 'Idade',
    '57 - 55. **MOSTRAR CARTÃO** Para fins de controle amostral e classificação socioeconômica, gostaria que me indicasse em qual faixa de renda se encontra a sua RENDA FAMILIAR, o que engloba tanto a sua renda quanto a das pessoas que moram nesse domicílio, incluindo salários fixos, aluguel, aposentadoria, bico, trabalho informal dentre outros?': 'Renda',
    '58 - 56. Qual a sua religião, seja como praticante ou com a qual o(a) Sr.(a) mais se identifica? **ESPONTÂNEA**': 'Religião',
    '5 - 3. Escolaridade do entrevistado: ENTREVISTADOR: atenção com diferenças nas nomenclaturas das faixas de resposta': 'Escolaridade',
    '7 - 5. O (a) Sr. (a) avalia o governo do presidente Lula como: **CITAR OPÇÕES DE 1 A 5**': 'Avaliação_Governo_Lula',
    '8 - 6. O (a) Sr. (a) aprova ou desaprova o desempenho pessoal do presidente Lula à frente do governo? **CITAR OPÇÕES 1 E 2**': 'Aprovação_Pessoal_Lula',
    '11 - 9. Em sua opinião, nos próximos seis meses a situação do EMPREGO no país: **CITAR OPÇÕES DE 1 A 3**': 'Expectativa_Emprego',
    '13 - 11. Em sua opinião, nos próximos seis meses a situação da SAÚDE no país: **CITAR OPÇÕES DE 1 A 3**': 'Expectativa_Saúde',
    '14 - 12. Em sua opinião, nos próximos seis meses a situação da EDUCAÇÃO no país: **CITAR OPÇÕES DE 1 A 3**': 'Expectativa_Educação',
    '15 - 13. Em sua opinião, nos próximos seis meses a situação da SEGURANÇA PÚBLICA no país: **CITAR OPÇÕES DE 1 A 3**': 'Expectativa_Segurança',
    '12 - 10. Em sua opinião, nos próximos seis meses a sua RENDA MENSAL: **CITAR OPÇÕES DE 1 A 3**': 'Expectativa_Renda',
    'Rodada': 'Rodada'
}
df.rename(columns=rename_columns, inplace=True)

# Mapeamento de valores
mapeamento_genero = {1: 'Masculino', 2: 'Feminino'}
mapeamento_idade = {
    1: '16 a 24 anos', 2: '25 a 34 anos', 3: '35 a 44 anos',
    4: '45 a 59 anos', 5: '60 anos ou mais'
}
mapeamento_avaliacao = {1: 'Ótimo', 2: 'Bom', 3: 'Regular', 4: 'Ruim', 5: 'Péssimo', 99: 'NS/NR'}
mapeamento_aprovacao = {1: 'Aprova', 2: 'Desaprova', 99: 'NS/NR'}
mapeamento_expectativas = {1: 'Vai melhorar', 2: 'Vai piorar', 3: 'Vai ficar igual', 99: 'NS/NR'}
mapeamento_escolaridade = {
    1: 'Até 5ª série (Fundamental)', 2: '6ª a 9ª série (Fundamental)',
    3: 'Ensino Médio', 4: 'Superior completo/incompleto'
}
mapeamento_renda = {
    1: 'Até R$ 2.640,00', 2: 'De R$ 2.640,01 a R$ 6.600,00', 3: 'Acima de R$ 6.600,00',
    94: 'Não quis informar', 99: 'NS/NR'
}
mapeamento_religiao = {
    1: 'Católico', 2: 'Espírita', 3: 'Evangélico', 4: 'Ateu', 5: 'Adventista',
    6: 'Testemunha de Jeová', 7: 'Afro-brasileiras', 98: 'Sem religião', 99: 'NS/NR'
}

df['Sexo'] = df['Sexo'].map(mapeamento_genero)
df['Idade'] = df['Idade'].map(mapeamento_idade)
df['Avaliação_Governo_Lula'] = df['Avaliação_Governo_Lula'].map(mapeamento_avaliacao)
df['Aprovação_Pessoal_Lula'] = df['Aprovação_Pessoal_Lula'].map(mapeamento_aprovacao)
df['Expectativa_Emprego'] = df['Expectativa_Emprego'].map(mapeamento_expectativas)
df['Expectativa_Saúde'] = df['Expectativa_Saúde'].map(mapeamento_expectativas)
df['Expectativa_Educação'] = df['Expectativa_Educação'].map(mapeamento_expectativas)
df['Expectativa_Segurança'] = df['Expectativa_Segurança'].map(mapeamento_expectativas)
df['Expectativa_Renda'] = df['Expectativa_Renda'].map(mapeamento_expectativas)
df['Escolaridade'] = df['Escolaridade'].map(mapeamento_escolaridade)
df['Renda'] = df['Renda'].map(mapeamento_renda)
df['Religião'] = df['Religião'].map(mapeamento_religiao)

# Função para encontrar uma porta livre automaticamente
def find_free_port(default_port=8050):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            sock.bind(("localhost", default_port))
            sock.close()
            return default_port
        except OSError:
            default_port += 1

# Inicializar o Dash App
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard - Pesquisa CNT"),

    # Filtros
    html.Div([
        html.Div([
            html.Label('Gênero:'),
            dcc.Dropdown(
                id='filter_gender',
                options=[{'label': g, 'value': g} for g in df['Sexo'].unique()],
                multi=True
            )
        ], style={'width': '24%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Idade:'),
            dcc.Dropdown(
                id='filter_age',
                options=[{'label': a, 'value': a} for a in df['Idade'].unique()],
                multi=True
            )
        ], style={'width': '24%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Escolaridade:'),
            dcc.Dropdown(
                id='filter_education',
                options=[{'label': e, 'value': e} for e in df['Escolaridade'].unique()],
                multi=True
            )
        ], style={'width': '24%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Religião:'),
            dcc.Dropdown(
                id='filter_religion',
                options=[{'label': r, 'value': r} for r in df['Religião'].dropna().unique()],
                multi=True
            )
        ], style={'width': '24%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    # Gráficos
    html.Div([
        dcc.Graph(id='gov_approval_graph'),
        dcc.Graph(id='personal_approval_graph')
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    html.Div([
        dcc.Graph(id='employment_expectation_graph'),
        dcc.Graph(id='health_expectation_graph')
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    html.Div([
        dcc.Graph(id='education_expectation_graph'),
        dcc.Graph(id='security_expectation_graph')
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    html.Div([
        dcc.Graph(id='income_expectation_graph')
    ], style={'width': '40%', 'margin': 'auto'})
])


# Callback para atualização dos gráficos
@app.callback(
    [Output('gov_approval_graph', 'figure'),
     Output('personal_approval_graph', 'figure'),
     Output('employment_expectation_graph', 'figure'),
     Output('health_expectation_graph', 'figure'),
     Output('education_expectation_graph', 'figure'),
     Output('security_expectation_graph', 'figure'),
     Output('income_expectation_graph', 'figure')],
    [Input('filter_gender', 'value'),
     Input('filter_age', 'value'),
     Input('filter_education', 'value'),
     Input('filter_religion', 'value')]
)
def update_graph(selected_genders, selected_ages, selected_education, selected_religion):
    filtered_data = df.copy()

    # Filtragem dos dados com base nas seleções
    if selected_genders:
        filtered_data = filtered_data[filtered_data['Sexo'].isin(selected_genders)]
    if selected_ages:
        filtered_data = filtered_data[filtered_data['Idade'].isin(selected_ages)]
    if selected_education:
        filtered_data = filtered_data[filtered_data['Escolaridade'].isin(selected_education)]
    if selected_religion:
        filtered_data = filtered_data[filtered_data['Religião'].isin(selected_religion)]

    # Agregar dados para garantir contagem correta
    gov_counts = filtered_data.groupby(['Avaliação_Governo_Lula', 'Rodada']).size().reset_index(name='count')
    personal_counts = filtered_data.groupby(['Aprovação_Pessoal_Lula', 'Rodada']).size().reset_index(name='count')
    emp_counts = filtered_data.groupby(['Expectativa_Emprego', 'Rodada']).size().reset_index(name='count')
    health_counts = filtered_data.groupby(['Expectativa_Saúde', 'Rodada']).size().reset_index(name='count')
    edu_counts = filtered_data.groupby(['Expectativa_Educação', 'Rodada']).size().reset_index(name='count')
    sec_counts = filtered_data.groupby(['Expectativa_Segurança', 'Rodada']).size().reset_index(name='count')
    inc_counts = filtered_data.groupby(['Expectativa_Renda', 'Rodada']).size().reset_index(name='count')

    # Gráficos
# Calcular o valor máximo de contagem entre todos os gráficos
    max_count = max(
        gov_counts['count'].max(),
        personal_counts['count'].max(),
        emp_counts['count'].max(),
        health_counts['count'].max(),
        edu_counts['count'].max(),
        sec_counts['count'].max(),
        inc_counts['count'].max()
    )

# Gráficos com a mesma escala
    fig_gov = px.bar(gov_counts, x='Avaliação_Governo_Lula', y='count', color='Rodada', barmode='group',
                    title='Avaliação do Governo Lula')
    fig_gov.update_layout(yaxis=dict(range=[0, max_count]))

    fig_personal = px.bar(personal_counts, x='Aprovação_Pessoal_Lula', y='count', color='Rodada', barmode='group',
                        title='Aprovação Pessoal do Presidente Lula')
    fig_personal.update_layout(yaxis=dict(range=[0, max_count]))

    fig_emp = px.bar(emp_counts, x='Expectativa_Emprego', y='count', color='Rodada', barmode='group',
                    title='Expectativa de Emprego')
    fig_emp.update_layout(yaxis=dict(range=[0, max_count]))

    fig_health = px.bar(health_counts, x='Expectativa_Saúde', y='count', color='Rodada', barmode='group',
                        title='Expectativa de Saúde')
    fig_health.update_layout(yaxis=dict(range=[0, max_count]))

    fig_edu = px.bar(edu_counts, x='Expectativa_Educação', y='count', color='Rodada', barmode='group',
                    title='Expectativa de Educação')
    fig_edu.update_layout(yaxis=dict(range=[0, max_count]))

    fig_sec = px.bar(sec_counts, x='Expectativa_Segurança', y='count', color='Rodada', barmode='group',
                    title='Expectativa de Segurança Pública')
    fig_sec.update_layout(yaxis=dict(range=[0, max_count]))

    fig_inc = px.bar(inc_counts, x='Expectativa_Renda', y='count', color='Rodada', barmode='group',
                    title='Expectativa de Renda Mensal')
    fig_inc.update_layout(yaxis=dict(range=[0, max_count]))


    return fig_gov, fig_personal, fig_emp, fig_health, fig_edu, fig_sec, fig_inc


if __name__ == '__main__':
    port = find_free_port()
    app.run(host='127.0.0.1', port=port, debug=True)
