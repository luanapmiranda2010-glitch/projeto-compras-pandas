# Projeto de Análise e Tratamento de Dados em Compras Hospitalares

Este projeto foi criado para demonstrar, de forma prática, o uso de Python e pandas no tratamento de uma base simulada de compras e fornecedores.

## Objetivo

Realizar limpeza, padronização e análise de dados de compras, criando uma base tratada e indicadores para apoiar decisões relacionadas a custos, fornecedores, SLA e performance operacional.

## Tecnologias utilizadas

- Python
- pandas
- CSV/Excel
- Tratamento de dados
- Qualidade de dados
- Análise exploratória
- Indicadores de negócio

## Estrutura do projeto

```text
projeto_compras_pandas/
├── dados/
│   ├── raw/
│   │   ├── pedidos_compras.csv
│   │   └── fornecedores.csv
│   └── processed/
│       └── base_compras_tratada.csv
├── outputs/
│   ├── resumo_geral.csv
│   ├── valor_por_fornecedor.csv
│   ├── valor_por_categoria.csv
│   ├── sla_por_hospital.csv
│   └── pedidos_por_status.csv
├── src/
│   └── tratamento_compras.py
├── requirements.txt
└── README.md
```

## O que foi feito

1. Leitura de arquivos CSV
2. Padronização dos nomes das colunas
3. Limpeza de textos
4. Remoção de duplicidades
5. Tratamento de valores nulos
6. Conversão de datas e campos numéricos
7. Criação de colunas calculadas
8. Integração da base de pedidos com fornecedores
9. Criação de indicadores de compras
10. Exportação da base tratada e dos indicadores

## Indicadores criados

- Total comprado
- Quantidade de pedidos
- Ticket médio
- Percentual de pedidos dentro do SLA de 48h
- Valor comprado por fornecedor
- Valor comprado por categoria
- SLA por hospital
- Quantidade de pedidos por status

## Como executar

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o projeto:

```bash
python src/tratamento_compras.py
```

Após a execução, os arquivos tratados serão gerados nas pastas `dados/processed` e `outputs`.

## Contexto de negócio

A base simula um cenário de compras hospitalares, com informações sobre pedidos, hospitais, fornecedores, itens, categorias, prazos e valores.

O projeto demonstra como técnicas simples de tratamento de dados podem gerar informações úteis para acompanhamento de custos, performance operacional e qualidade dos dados.