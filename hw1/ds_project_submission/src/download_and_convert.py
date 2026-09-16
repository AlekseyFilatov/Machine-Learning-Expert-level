import os
import polars as pl

def load_and_convert_dataset():
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    excel_path = os.path.join(raw_dir, "Online Retail.xlsx")
    parquet_path = os.path.join(raw_dir, "online_retail.parquet")
    
    if not os.path.exists(excel_path):
        print(f"❌ Ошибка! Файл не найден: {excel_path}")
        return

    print(f"⏳ Шаг 1: Чтение Excel файла через Polars...")
    # Polars прочитает файл и автоматически разрешит конфликты типов в строках
    df = pl.read_excel(excel_path, engine="openpyxl")
    
    print(f"✅ Данные загружены. Формат таблицы: {df.shape}")
    
    print("⏳ Шаг 2: Нормализация структуры...")
    # Переименуем колонки, убрав пробелы по краям
    df = df.rename({col: col.strip() for col in df.columns})
    
    # Корректируем CustomerID (если колонка есть)
    if "CustomerID" in df.columns:
        df = df.with_columns(
            pl.col("CustomerID")
            .cast(pl.String)
            .str.split(".")
            .list.get(0)
            .replace("nan", None)
        )
        
    print("⏳ Шаг 3: Сохранение в формат Parquet...")
    # У Polars встроенная и очень стабильная запись в Parquet без капризов pyarrow
    df.write_parquet(parquet_path)
    
    file_size_mb = os.path.getsize(parquet_path) / (1024 * 1024)
    print(f"🎉 Успех! Файл сохранен по пути: {parquet_path}")
    print(f"📊 Размер Parquet-файла: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    load_and_convert_dataset()
