import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np

# Configurações
NUM_REQUISICOES = 100000
DATA_INICIO = datetime(2018, 1, 1)
DATA_FIM = datetime(2025, 10, 17)

# Listas de dados para geração aleatória
solicitantes = [
    "João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Souza",
    "Juliana Lima", "Fernando Alves", "Patricia Rocha", "Roberto Mendes", "Camila Ferreira",
    "Lucas Martins", "Amanda Ribeiro", "Rafael Cardoso", "Beatriz Araújo", "Thiago Barbosa",
    "Fernanda Gomes", "Marcelo Dias", "Larissa Pinto", "Diego Castro", "Gabriela Moreira",
    "Bruno Nascimento", "Leticia Correia", "Guilherme Pereira", "Renata Teixeira", "Vinicius Reis",
    "Mariana Cunha", "Felipe Monteiro", "Isabela Freitas", "André Carvalho", "Carolina Ramos"
]

maquinas = [
    "Máquina A", "Máquina B", "Máquina C", "Máquina D", "Máquina E",
    "Máquina F", "Máquina G", "Máquina H", "Máquina I", "Máquina J",
    "Torno CNC 01", "Torno CNC 02", "Fresadora 01", "Fresadora 02",
    "Centro de Usinagem 01", "Centro de Usinagem 02", "Prensa Hidráulica 01",
    "Injetora 01", "Injetora 02", "Extrusora 01", "Retífica 01", "Retífica 02"
]

pecas = [
    "Rolamento 6205", "Correia Dentada GT2", "Engrenagem Z40", "Eixo Ø25mm",
    "Bucha de Bronze", "Chaveta 8x7x45", "Parafuso M12x40", "Porca Sextavada M12",
    "Arruela Lisa M12", "Vedação O-ring 50x3", "Mancal UCF 205", "Acoplamento Flexível",
    "Corrente Transmissão", "Pinhão Z20", "Rolamento Axial", "Guia Linear 20mm",
    "Patim Recirculante", "Fuso Trapezoidal TR16", "Castanha Fixação", "Placa de Apoio",
    "Cilindro Pneumático", "Válvula Direcional 5/2", "Sensor Indutivo M18", "Relé 24V",
    "Contator 220V", "Disjuntor 10A", "Fusível 5A", "Cabo PP 3x2.5mm", "Conector RJ45",
    "Filtro de Ar Comprimido", "Regulador de Pressão", "Lubrificador Pneumático",
    "Mangueira Poliuretano 8mm", "Conexão Rápida 1/4", "Abraçadeira Metálica",
    "Graxa Lubrificante", "Óleo Hidráulico ISO 68", "Estopa Industrial", "Lixa Grão 120",
    "Disco de Corte 7pol", "Rebolo de Desbaste", "Broca HSS Ø10mm", "Fresa de Topo Ø12mm",
    "Inserto TNMG 160408", "Pastilha CCMT 09T304", "Porta-Ferramenta MCLNR", "Mandril B16"
]

status_entrega = [
    "Sim, {nome}", "Não", "Pendente", "Parcial", "Aguardando", "Em separação"
]

def gerar_data_aleatoria():
    """Gera uma data aleatória entre DATA_INICIO e DATA_FIM"""
    delta = DATA_FIM - DATA_INICIO
    random_days = random.randint(0, delta.days)
    data = DATA_INICIO + timedelta(days=random_days)
    return data.strftime("%m-%Y")

def gerar_status_entrega(solicitante):
    """Gera status de entrega, com maior probabilidade de 'Sim'"""
    status = random.choices(
        status_entrega,
        weights=[60, 15, 10, 8, 4, 3],
        k=1
    )[0]
    
    if "{nome}" in status:
        nome = solicitante.split()[0]
        status = status.format(nome=nome)
    
    return status

def gerar_quantidade():
    """Gera quantidade de peças com distribuição realista"""
    probabilidade = random.random()
    if probabilidade < 0.5:  # 50% das vezes: 1-5 peças
        return random.randint(1, 5)
    elif probabilidade < 0.8:  # 30% das vezes: 6-20 peças
        return random.randint(6, 20)
    elif probabilidade < 0.95:  # 15% das vezes: 21-50 peças
        return random.randint(21, 50)
    else:  # 5% das vezes: 51-200 peças
        return random.randint(51, 200)

def gerar_preco_unitario():
    """Gera preço unitário baseado em distribuição realista"""
    probabilidade = random.random()
    if probabilidade < 0.4:  # 40%: peças baratas
        return round(random.uniform(5, 50), 2)
    elif probabilidade < 0.75:  # 35%: peças médias
        return round(random.uniform(50, 200), 2)
    elif probabilidade < 0.95:  # 20%: peças caras
        return round(random.uniform(200, 1000), 2)
    else:  # 5%: peças muito caras
        return round(random.uniform(1000, 5000), 2)

# Geração dos dados
print(f"Gerando {NUM_REQUISICOES} requisições fake...")

dados = []
for i in range(NUM_REQUISICOES):
    solicitante = random.choice(solicitantes)
    quantidade = gerar_quantidade()
    preco_unitario = gerar_preco_unitario()
    total = round(quantidade * preco_unitario, 2)
    
    registro = {
        "": i,
        "Mês/Ano": gerar_data_aleatoria(),
        "Solicitante": solicitante,
        "2- Máquina de destino:": random.choice(maquinas),
        "6- Descrição da peça: ": random.choice(pecas),
        "7- Quantidade de peças.": quantidade,
        "Total": total,
        "Entregue?": gerar_status_entrega(solicitante)
    }
    
    dados.append(registro)
    
    # Feedback de progresso
    if (i + 1) % 1000 == 0:
        print(f"Geradas {i + 1} requisições...")

# Criar DataFrame
df = pd.DataFrame(dados)

# Salvar em CSV
nome_arquivo = f"requisicoes_fake_{NUM_REQUISICOES}.csv"
df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')

print(f"\n✓ Arquivo '{nome_arquivo}' gerado com sucesso!")
print(f"\nEstatísticas dos dados gerados:")
print(f"- Total de requisições: {len(df)}")
print(f"- Período: {df['Mês/Ano'].min()} até {df['Mês/Ano'].max()}")
print(f"- Total geral: R$ {df['Total'].sum():,.2f}")
print(f"- Valor médio por requisição: R$ {df['Total'].mean():,.2f}")
print(f"- Quantidade total de peças: {df['7- Quantidade de peças.'].sum()}")
print(f"- Solicitantes únicos: {df['Solicitante'].nunique()}")
print(f"- Máquinas únicas: {df['2- Máquina de destino:'].nunique()}")
print(f"- Tipos de peças únicas: {df['6- Descrição da peça: '].nunique()}")

# Mostrar distribuição de status
print(f"\nDistribuição de status de entrega:")
print(df['Entregue?'].value_counts())

# Mostrar amostra dos dados
print(f"\nAmostra dos primeiros 5 registros:")
print(df.head())