import os
import polars as pl


def load_and_convert_dataset():
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    csv_path = os.path.join(raw_dir, "epilepsy_raw.csv")
    parquet_path = os.path.join(raw_dir, "epilepsy_raw.parquet")
    
    if not os.path.exists(csv_path):
        print(f"❌ Ошибка! Файл не найден: {csv_path}")
        return

    print(f"⏳ Шаг 1: Чтение csv файла через Polars...")
    # Нативный движок Polars сам разберется с типами данных в разы быстрее Pandas
    df = pl.read_csv(csv_path)
    
    print(f"✅ Данные загружены. Формат таблицы: {df.shape}")
    
    print("⏳ Шаг 2: Нормализация структуры...")
    # Очищаем имена колонок от случайных пробелов по краям (в стиле Polars)
    df = df.select(pl.all().name.map(lambda col: col.strip()))
    
    print("⏳ Шаг 3: Сохранение в формат Parquet...")
    # Запись в Parquet «из коробки»
    df.write_parquet(parquet_path)
    
    file_size_mb = os.path.getsize(parquet_path) / (1024 * 1024)
    print(f"🎉 Успех! Файл сохранен по пути: {parquet_path}")
    print(f"📊 Размер Parquet-файла: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    load_and_convert_dataset()
