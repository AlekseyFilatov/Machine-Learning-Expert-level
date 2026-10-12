import os
import polars as pl
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Указываем точные абсолютные пути к исходным CSV
INPUT_DIR = PROJECT_ROOT / "data" / "raw"
path_interactions_csv = INPUT_DIR / "interactions_df.csv"
path_items_csv = INPUT_DIR / "items.csv"
path_users_csv = INPUT_DIR / "users.csv"

# Указываем точный путь для сохранения Parquet
output_dir = PROJECT_ROOT / "data" / "processed"
os.makedirs(output_dir, exist_ok=True)

print(f"🏠 Корень проекта определен как: {PROJECT_ROOT}")
print(f"🔍 Ищем исходные файлы в: {INPUT_DIR}")

# =====================================================================
# 1. ОБРАБОТКА ТАБЛИЦЫ ВЗАИМОДЕЙСТВИЙ (interactions_df.csv)
# =====================================================================
print("⏳ Polars: Обработка interactions_df.csv...")
try:
    interactions = (
        pl.scan_csv(path_interactions_csv) # Lazy-режим для экономии памяти
        .with_columns([
            pl.col('user_id').cast(pl.Int32),
            pl.col('item_id').cast(pl.Int32),
            # Парсим дату строго в формат Date
            pl.col('last_watch_dt').str.to_date('%Y-%m-%d'),
            pl.col('total_dur').cast(pl.Int32),
            pl.col('watched_pct').cast(pl.Float32)
        ])
        .unique(subset=['user_id', 'item_id', 'last_watch_dt']) # Удаление дубликатов
    ).collect() # Запуск вычислений
    
    interactions.write_parquet(os.path.join(output_dir, "interactions.parquet"))
    print(f"💾 Сохранен interactions.parquet. Размер: {interactions.shape}")
except Exception as e:
    print(f"❌ Ошибка в interactions: {e}")

# =====================================================================
# 2. ОБРАБОТКА ТАБЛИЦЫ КОНТЕНТА (items.csv)
# =====================================================================
print("\n⏳ Polars: Обработка items.csv...")
try:
    items = (
        pl.scan_csv(path_items_csv, null_values=['', 'NA', 'NaN'])
        .with_columns([
            pl.col('item_id').cast(pl.Int32),
            pl.col('release_year').cast(pl.Int32) # Polars нативно поддерживает Int32 с null!
        ])
    ).collect()
    
    items.write_parquet(os.path.join(output_dir, "items.parquet"))
    print(f"💾 Сохранен items.parquet. Размер: {items.shape}")
except Exception as e:
    print(f"❌ Ошибка в items: {e}")

# =====================================================================
# 3. ОБРАБОТКА И УМНОЕ КОДИРОВАНИЕ ПОЛЬЗОВАТЕЛЕЙ (users.csv)
# =====================================================================
print("\n⏳ Polars: Очистка и кодирование пользователей users.csv...")
try:
    # Задаем строгие списки порядков для маппинга
    age_order = ['age_18_24', 'age_25_34', 'age_35_44', 'age_45_54', 'age_55_64', 'age_65_inf']
    income_order = ['income_0_20', 'income_20_40', 'income_40_60', 'income_60_90', 'income_90_150', 'income_150_inf']
    
    users = pl.read_csv(path_users_csv, null_values=['', 'NA', 'NaN'])
    
    # Строим выражение для порядкового кодирования через pl.when().then()
    age_expr = pl.when(pl.col('age').is_null()).then(-1)
    for idx, val in enumerate(age_order):
        age_expr = age_expr.when(pl.col('age') == val).then(idx)
    age_expr = age_expr.otherwise(-1).cast(pl.Int8).alias('age_encoded')

    income_expr = pl.when(pl.col('income').is_null()).then(-1)
    for idx, val in enumerate(income_order):
        income_expr = income_expr.when(pl.col('income') == val).then(idx)
    income_expr = income_expr.otherwise(-1).cast(pl.Int8).alias('income_encoded')

    # Собираем все трансформации в один быстрый параллельный проход
    users_processed = users.with_columns([
        age_expr,
        income_expr,
        # Кодируем пол: М -> 1, Ж -> 0, прочие/null -> -1
        pl.when(pl.col('sex') == 'М').then(1)
          .when(pl.col('sex') == 'Ж').then(0)
          .otherwise(-1).cast(pl.Int8).alias('sex_encoded'),
        # Заполняем пропуски в флагах детей
        pl.col('kids_flg').fill_null(-1).cast(pl.Int8)
    ]).drop(['age', 'income', 'sex']) # Удаляем старые текстовые колонки
    
    users_processed.write_parquet(os.path.join(output_dir, "users.parquet"))
    print(f"💾 Сохранен кодированный users.parquet. Размер: {users_processed.shape}")
    print("\n👀 Первые 5 строк таблицы users:")
    print(users_processed.head(5))
except Exception as e:
    print(f"❌ Ошибка в users: {e}")

print(f"\n🎉 [Polars Конвейер] Все шаги выполнены на максимальной скорости Rust!")

'''text
🏠 Корень проекта определен как: /mnt/d/ds_project
🔍 Ищем исходные файлы в: /mnt/d/ds_project/data/raw
⏳ Polars: Обработка interactions_df.csv...
💾 Сохранен interactions.parquet. Размер: (5476251, 5)

⏳ Polars: Обработка items.csv...
💾 Сохранен items.parquet. Размер: (15963, 14)

⏳ Polars: Очистка и кодирование пользователей users.csv...
💾 Сохранен кодированный users.parquet. Размер: (840197, 5)

👀 Первые 5 строк таблицы users:
shape: (5, 5)
┌─────────┬──────────┬─────────────┬────────────────┬─────────────┐
│ user_id ┆ kids_flg ┆ age_encoded ┆ income_encoded ┆ sex_encoded │
│ ---     ┆ ---      ┆ ---         ┆ ---            ┆ ---         │
│ i64     ┆ i8       ┆ i8          ┆ i8             ┆ i8          │
╞═════════╪══════════╪═════════════╪════════════════╪═════════════╡
│ 973171  ┆ 1        ┆ 1           ┆ 3              ┆ 1           │
│ 962099  ┆ 0        ┆ 0           ┆ 1              ┆ 1           │
│ 1047345 ┆ 0        ┆ 3           ┆ 2              ┆ 0           │
│ 721985  ┆ 0        ┆ 3           ┆ 1              ┆ 0           │
│ 704055  ┆ 0        ┆ 2           ┆ 3              ┆ 0           │
└─────────┴──────────┴─────────────┴────────────────┴─────────────┘

🎉 [Polars Конвейер] Все шаги выполнены на максимальной скорости Rust!
'''
