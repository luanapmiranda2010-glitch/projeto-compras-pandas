from pathlib import Path
import pandas as pd
import unicodedata
import re

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "dados" / "raw"
PROCESSED_DIR = BASE_DIR / "dados" / "processed"
OUTPUTS_DIR = BASE_DIR / "outputs"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

def padronizar_coluna(nome: str) -> str:
    """Remove acentos, espaços e caracteres especiais dos nomes das colunas."""
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("utf-8")
    nome = nome.lower().strip()
    nome = re.sub(r"[^a-z0-9]+", "_", nome)
    return nome.strip("_")

def limpar_texto(serie: pd.Series) -> pd.Series:
    """Padroniza campos de texto."""
    return serie.astype("string").str.strip().str.upper()

def carregar_dados() -> tuple[pd.DataFrame, pd.DataFrame]:
    pedidos = pd.read_csv(RAW_DIR / "pedidos_compras.csv", sep=";")
    fornecedores = pd.read_csv(RAW_DIR / "fornecedores.csv", sep=";")
    return pedidos, fornecedores

def tratar_pedidos(pedidos: pd.DataFrame) -> pd.DataFrame:
    pedidos = pedidos.copy()

    # Padronização de colunas
    pedidos.columns = [padronizar_coluna(col) for col in pedidos.columns]

    # Remoção de duplicidades
    pedidos = pedidos.drop_duplicates()

    # Tratamento de textos
    for col in ["hospital", "item", "categoria", "status", "urgente"]:
        pedidos[col] = limpar_texto(pedidos[col])

    # Tratamento de datas
    pedidos["data_solicitacao"] = pd.to_datetime(pedidos["data_solicitacao"], dayfirst=True, errors="coerce")
    pedidos["data_pedido"] = pd.to_datetime(pedidos["data_pedido"], dayfirst=True, errors="coerce")

    # Tratamento de números
    pedidos["quantidade"] = pd.to_numeric(pedidos["quantidade"], errors="coerce").fillna(0)
    pedidos["valor_unitario"] = pd.to_numeric(pedidos["valor_unitario"], errors="coerce")

    # Tratamento de nulos
    pedidos["status"] = pedidos["status"].fillna("NAO INFORMADO")
    pedidos["id_fornecedor"] = pedidos["id_fornecedor"].fillna(0).astype(int)
    pedidos["valor_unitario"] = pedidos["valor_unitario"].fillna(pedidos["valor_unitario"].median())

    # Criação de indicadores calculados
    pedidos["valor_total"] = pedidos["quantidade"] * pedidos["valor_unitario"]
    pedidos["dias_atendimento"] = (pedidos["data_pedido"] - pedidos["data_solicitacao"]).dt.days
    pedidos["dentro_sla_48h"] = pedidos["dias_atendimento"].apply(lambda x: "SIM" if x <= 2 else "NAO")

    return pedidos

def tratar_fornecedores(fornecedores: pd.DataFrame) -> pd.DataFrame:
    fornecedores = fornecedores.copy()
    fornecedores.columns = [padronizar_coluna(col) for col in fornecedores.columns]

    fornecedores["fornecedor"] = limpar_texto(fornecedores["fornecedor"])
    fornecedores["uf"] = limpar_texto(fornecedores["uf"])
    fornecedores["categoria_fornecedor"] = limpar_texto(fornecedores["categoria_fornecedor"])
    fornecedores["uf"] = fornecedores["uf"].fillna("NAO INFORMADO")
    fornecedores["categoria_fornecedor"] = fornecedores["categoria_fornecedor"].fillna("NAO INFORMADO")

    return fornecedores

def criar_indicadores(base: pd.DataFrame) -> dict[str, pd.DataFrame]:
    indicadores = {}

    indicadores["resumo_geral"] = pd.DataFrame({
        "indicador": [
            "total_comprado",
            "quantidade_pedidos",
            "ticket_medio",
            "percentual_dentro_sla_48h"
        ],
        "valor": [
            base["valor_total"].sum(),
            base["id_pedido"].nunique(),
            base["valor_total"].mean(),
            (base["dentro_sla_48h"].eq("SIM").mean() * 100)
        ]
    })

    indicadores["valor_por_fornecedor"] = (
        base.groupby("fornecedor", dropna=False)["valor_total"]
        .sum()
        .reset_index()
        .sort_values("valor_total", ascending=False)
    )

    indicadores["valor_por_categoria"] = (
        base.groupby("categoria")["valor_total"]
        .sum()
        .reset_index()
        .sort_values("valor_total", ascending=False)
    )

    indicadores["sla_por_hospital"] = (
        base.groupby("hospital")["dentro_sla_48h"]
        .apply(lambda x: (x.eq("SIM").mean() * 100))
        .reset_index(name="percentual_dentro_sla_48h")
        .sort_values("percentual_dentro_sla_48h", ascending=False)
    )

    indicadores["pedidos_por_status"] = (
        base.groupby("status")["id_pedido"]
        .nunique()
        .reset_index(name="quantidade_pedidos")
        .sort_values("quantidade_pedidos", ascending=False)
    )

    return indicadores

def main():
    pedidos_raw, fornecedores_raw = carregar_dados()

    pedidos = tratar_pedidos(pedidos_raw)
    fornecedores = tratar_fornecedores(fornecedores_raw)

    base = pedidos.merge(fornecedores, on="id_fornecedor", how="left")
    base["fornecedor"] = base["fornecedor"].fillna("SEM CADASTRO")
    base["uf"] = base["uf"].fillna("NAO INFORMADO")
    base["categoria_fornecedor"] = base["categoria_fornecedor"].fillna("NAO INFORMADO")

    base.to_csv(PROCESSED_DIR / "base_compras_tratada.csv", index=False, sep=";", encoding="utf-8-sig")

    indicadores = criar_indicadores(base)

    for nome, df in indicadores.items():
        df.to_csv(OUTPUTS_DIR / f"{nome}.csv", index=False, sep=";", encoding="utf-8-sig")

    print("Projeto executado com sucesso!")
    print(f"Base tratada salva em: {PROCESSED_DIR / 'base_compras_tratada.csv'}")
    print(f"Indicadores salvos em: {OUTPUTS_DIR}")

if __name__ == "__main__":
    main()