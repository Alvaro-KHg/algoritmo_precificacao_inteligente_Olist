import pandas as pd
import numpy as np

# ============================================================
# 1. Carregar os dados (você precisa baixar os CSVs do Kaggle)
# ============================================================
print("⏳ Carregando dados...")
items = pd.read_csv('olist_order_items_dataset.csv')
products = pd.read_csv('olist_products_dataset.csv')

# ============================================================
# 2. Contar vendas por produto dentro de cada categoria
# ============================================================
print("📊 Analisando produtos por categoria...")

# Contar quantas vendas cada produto tem
vendas_por_produto = items.groupby('product_id').agg({
    'order_id': 'count',
    'price': ['mean', 'std', 'min', 'max']
}).reset_index()

vendas_por_produto.columns = ['product_id', 'num_vendas', 'preco_medio', 'preco_std', 'preco_min', 'preco_max']

# Adicionar categoria
vendas_por_produto = vendas_por_produto.merge(
    products[['product_id', 'product_category_name', 'product_weight_g']], 
    on='product_id', 
    how='left'
)

# ============================================================
# 3. Filtrar produtos com MUITAS vendas (>= 50 vendas)
# ============================================================
produtos_muito_vendidos = vendas_por_produto[vendas_por_produto['num_vendas'] >= 50].copy()

print(f"\n✅ Produtos com >= 50 vendas: {len(produtos_muito_vendidos)}")

# ============================================================
# 4. Calcular variação de preço (coeficiente de variação)
# ============================================================
produtos_muito_vendidos['coef_variacao_preco'] = (
    produtos_muito_vendidos['preco_std'] / produtos_muito_vendidos['preco_medio']
)

# Calcular variação de preço em %
produtos_muito_vendidos['variacao_preco_percent'] = (
    (produtos_muito_vendidos['preco_max'] - produtos_muito_vendidos['preco_min']) 
    / produtos_muito_vendidos['preco_medio'] * 100
)

# ============================================================
# 5. Ordenar: MAIS VENDAS + MAIOR VARIAÇÃO DE PREÇO
# ============================================================
produtos_ordenados = produtos_muito_vendidos.sort_values(
    ['num_vendas', 'variacao_preco_percent'], 
    ascending=[False, False]
)

# ============================================================
# 6. Mostrar os TOP 10 melhores produtos
# ============================================================
print("\n" + "="*80)
print("🏆 TOP 10 PRODUTOS COM MAIS VENDAS + BOA VARIAÇÃO DE PREÇO")
print("="*80)

top_10 = produtos_ordenados.head(10)

for i, row in top_10.iterrows():
    print(f"\n{i+1}. Categoria: {row['product_category_name']}")
    print(f"   Product ID: {row['product_id']}")
    print(f"   Vendas: {row['num_vendas']}")
    print(f"   Preço médio: R$ {row['preco_medio']:.2f}")
    print(f"   Preço mínimo: R$ {row['preco_min']:.2f}")
    print(f"   Preço máximo: R$ {row['preco_max']:.2f}")
    print(f"   Variação de preço: {row['variacao_preco_percent']:.1f}%")
    print(f"   Peso: {row['product_weight_g']}g")

# ============================================================
# 7. Escolher o MELHOR produto (recomendado)
# ============================================================
melhor_produto = produtos_ordenados.iloc[0]

print("\n" + "="*80)
print("⭐ PRODUTO RECOMENDADO PARA SEU TRABALHO")
print("="*80)
print(f"\nProduct ID: {melhor_produto['product_id']}")
print(f"Categoria: {melhor_produto['product_category_name']}")
print(f"Vendas: {melhor_produto['num_vendas']}")
print(f"Preço médio: R$ {melhor_produto['preco_medio']:.2f}")
print(f"Variação de preço: {melhor_produto['variacao_preco_percent']:.1f}%")

# ============================================================
# 8. Salvar o dataset final deste produto
# ============================================================
product_id_escolhido = melhor_produto['product_id']

df_final = items[items['product_id'] == product_id_escolhido].copy()
df_final = df_final.merge(
    products[['product_id', 'product_category_name', 'product_weight_g', 
              'product_length_cm', 'product_height_cm', 'product_width_cm']], 
    on='product_id'
)

# Criar colunas que você precisa
df_final['ID'] = df_final['order_id']
df_final['Data'] = pd.to_datetime(df_final['shipping_limit_date'])
df_final['Preço_unitário'] = df_final['price']
df_final['Quantidade_vendida'] = df_final['quantity']
df_final['Valor_total'] = df_final['price'] * df_final['quantity']
df_final['Custo_produto'] = df_final['price'] * 0.65  # Estimativa: 65%

# Ordenar por data
df_final = df_final.sort_values('Data')

# Salvar
df_final.to_csv('dataset_sku_escolhido_final.csv', index=False)

print(f"\n✅ Dataset salvo: 'dataset_sku_escolhido_final.csv'")
print(f"   Total de vendas: {len(df_final)}")
print(f"   Período: {df_final['Data'].min()} até {df_final['Data'].max()}")

# ============================================================
# 9. Mostrar estatísticas do dataset final
# ============================================================
print("\n" + "="*80)
print("📈 ESTATÍSTICAS DO DATASET FINAL")
print("="*80)
print(f"\nVendas totais: {len(df_final)}")
print(f"Preço mínimo: R$ {df_final['Preço_unitário'].min():.2f}")
print(f"Preço máximo: R$ {df_final['Preço_unitário'].max():.2f}")
print(f"Preço médio: R$ {df_final['Preço_unitário'].mean():.2f}")
print(f"Std de preço: R$ {df_final['Preço_unitário'].std():.2f}")
print(f"\nQuantidade mínima: {df_final['Quantidade_vendida'].min()}")
print(f"Quantidade máxima: {df_final['Quantidade_vendida'].max()}")
print(f"Quantidade média: {df_final['Quantidade_vendida'].mean():.1f}")
print(f"\nValor total médio: R$ {df_final['Valor_total'].mean():.2f}")
print(f"Custo médio: R$ {df_final['Custo_produto'].mean():.2f}")
print(f"Margem média: {(1 - 0.65) * 100:.1f}%")

# ============================================================
# 10. Mostrar as primeiras linhas do dataset
# ============================================================
print("\n" + "="*80)
print("📄 PRIMEIRAS 5 LINHAS DO DATASET")
print("="*80)
print(df_final.head().to_string())