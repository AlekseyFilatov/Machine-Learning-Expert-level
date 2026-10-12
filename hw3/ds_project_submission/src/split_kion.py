import polars as pl
from pathlib import Path
from datetime import timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent if '__file__' in globals() else Path(os.getcwd())
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "interactions.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

print("⏳ Загрузка interactions.parquet для глубокого временного анализа...")
df = pl.read_parquet(INPUT_PATH)

# Находим максимальную дату в датасете (финал истории KION)
max_date = df['last_watch_dt'].max()
print(f"📅 Финальная дата в датасете: {max_date}")

# =====================================================================
#  МЕТОДОЛОГИЧЕСКИЙ КОНТРАКТ (60 ДНЕЙ ПОД 2-Й УРОВЕНЬ)
# =====================================================================
# Фиксируем жесткие границы отсечения по лекционному ТЗ
test_threshold = max_date - pl.duration(days=7)                 # Последняя неделя на чистый тест
val_threshold = test_threshold - pl.duration(days=60)           #  2 МЕСЯЦА ПОД ВТОРОЙ УРОВЕНЬ!

print(f"✂️ Лекционная граница обучения 1-го уровня (Train Cutoff): {val_threshold}")
print(f"✂️ Лекционная граница обучения 2-го уровня (Val Cutoff):   {test_threshold}")

# 1. Блок А: Всё, что накоплено ДО val_threshold — база для латентных векторов 1-го уровня
train_filters = df.filter(pl.col('last_watch_dt') < val_threshold)

# 2. Блок Б: Мощное 60-дневное окно для генерации кандидатов, фич и обучения бустингов/нейросетей
val_iterations = df.filter((pl.col('last_watch_dt') >= val_threshold) & (pl.col('last_watch_dt') < test_threshold))

# 3. Блок В: Полностью изолированный тест для финального замера Precision@20 (последние 7 дней)
test_final = df.filter(pl.col('last_watch_dt') >= test_threshold)

# =====================================================================
# 3. ЭКСПОРТ В PARQUET И КОНТРОЛЬНЫЙ ВЫВОД МАСШТАБОВ ВОРОНКИ
# =====================================================================
print("\n💾 Сохранение оптимизированных пулов на диск KION...")
train_filters.write_parquet(OUTPUT_DIR / "kion_train_filters.parquet")
val_iterations.write_parquet(OUTPUT_DIR / "kion_val_iterations.parquet")
test_final.write_parquet(OUTPUT_DIR / "kion_test_final.parquet")

print(f"\n🏆 СИНХРОНИЗАЦИЯ С ЛЕКЦИЕЙ ВЫПОЛНЕНА УСПЕШНО:")
print(f"  ├── train (Слой 1 ──> implicit матрица):  {train_filters.shape[0]} строк")
print(f"  ├── val   (Слой 2 ──> 60 дней под LTR):    {val_iterations.shape[0]} строк")
print(f"  └── test  (Слой замера Precision@20):      {test_final.shape[0]} строк")
