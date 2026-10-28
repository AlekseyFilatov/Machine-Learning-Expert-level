#!/usr/bin/env bash
set -euo pipefail

# Переходим в директорию скрипта, чтобы пути были абсолютными
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "🧹 [CLEANUP] Очистка локального Data Science окружения..."

# 1. Завершение работы фоновых серверов Jupyter и MLflow
echo "⏹️ Проверка и остановка фоновых серверов разработки..."

# Ищем и тушим Jupyter Lab / Notebook
JUPYTER_PIDS=$(pgrep -f "jupyter-lab|jupyter-notebook" || true)
if [ -n "$JUPYTER_PIDS" ]; then
    echo "⏹️ Закрываем активные серверы Jupyter..."
    echo "$JUPYTER_PIDS" | xargs kill -15 2>/dev/null || true
fi

# Ищем и тушим локальный сервер трекинга MLflow
MLFLOW_PIDS=$(pgrep -f "mlflow server|mlflow ui" || true)
if [ -n "$MLFLOW_PIDS" ]; then
    echo "⏹️ Закрываем сервер трекинга MLflow..."
    echo "$MLFLOW_PIDS" | xargs kill -15 2>/dev/null || true
fi


# 2. Уничтожение зависших скриптов обучения и обработки данных
MY_USER=$(whoami)
echo "⏹️ Поиск зависших процессов обучения и обработки данных..."

# Типичные паттерны для DS: jupyter-kernel (зависшие вычисления внутри блокнотов), 
# train.py (обучение моделей), preprocess.py (обработка временных рядов/сигналов)
for pattern in "jupyter-behavior" "ipykernel_launcher" "train.py" "preprocess.py" "eda.py"; do
    PIDS=$(pgrep -u "$MY_USER" -f "$pattern" | grep -v "$$" || true)
    if [ -n "$PIDS" ]; then
        echo "   -> Принудительное уничтожение процессов для '$pattern'..."
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
    fi
done


# 3. Безопасное удаление временных файлов кода и чекпоинтов блокнотов
echo "🧹 Очистка кэша компиляции и временных файлов блокнотов..."

# Удаляем __pycache__ (освобождает место)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Удаляем скрытые кэши jupyter-блокнотов (чекпоинты, автосохранения), не трогая сами блокноты
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

# Удаляем кэши графической библиотеки Plotly (иногда оставляет временный мусор)
find . -type d -name ".plotly_images" -exec rm -rf {} + 2>/dev/null || true


# 4. Очищаем системный кэш RAM WSL (критично для Pandas и больших матриц Scipy/UMAP)
if [ "$EUID" -eq 0 ]; then
    sync && echo 3 > /proc/sys/vm/drop_caches
    echo "🧠 Системный кэш RAM успешно очищен."
else
    echo "ℹ️ Пропуск очистки кэша RAM (требуются права root)."
    echo "   Чтобы освободить ОЗУ ноутбука, запустите: sudo $0"
fi

echo "✅ Окружение очищено. Память освобождена, фоновые серверы остановлены!"
