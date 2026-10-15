#!/usr/bin/env bash
set -euo pipefail

echo "📦 [SETUP] Накатываем Data Science окружение на Ubuntu (Классический ML)..."

# 1. Определение окружения
ENV_DIR=""
if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo "✅ Зафиксировано активное окружение в терминале: $(basename "$VIRTUAL_ENV")"
    ENV_DIR="$VIRTUAL_ENV"
elif [ -d ".venv" ]; then
    echo "🔄 Найдена папка .venv. Используем её..."
    ENV_DIR="$(pwd)/.venv"
elif [ -d "ds_env" ]; then
    echo "🔄 Найдена папка ds_env. Используем её..."
    ENV_DIR="$(pwd)/ds_env"
else
    echo "🔄 Локальное окружение не найдено. Создаем чистый .venv..."
    if ! python3 -m venv .venv 2>/dev/null; then
        echo "❌ Ошибка: В системе отсутствует пакет python3-venv."
        echo "💡 Выполните: sudo apt update && sudo apt install -y python3-venv"
        exit 1
    fi
    ENV_DIR="$(pwd)/.venv"
fi

# Путь к pip внутри окружения
ENV_PIP="$ENV_DIR/bin/pip"

if [ ! -f "$ENV_PIP" ]; then
    echo "❌ Не удалось найти pip в окружении по пути: $ENV_PIP"
    exit 1
fi

echo "🚀 Обновляем pip..."
"$ENV_PIP" install --upgrade pip --timeout 100 --retries 5 -q

echo "📥 Установка пула Data Science библиотек (~1.3 ГБ)..."
"$ENV_PIP" install \
    numpy \
    pandas \
    scikit-learn \
    scipy \
    tsfel \
    tsfresh \
    dtaidistance \
    openpyxl \
    polars \
    networkx \
    MiniSom \
    cryptocompare \
    tslearn \
    umap-learn \
    matplotlib \
    ucimlrepo \
    pyarrow \
    seaborn \
    plotly \
    jupyter \
    mlflow \
    catboost \
    --timeout 1000 \
    --retries 10 \
    -q

echo "✅ [SUCCESS] Все библиотеки успешно установлены!"

echo "📝 Фиксация зависимостей в локальный requirements.txt..."
"$ENV_PIP" freeze --local > requirements.txt

echo "🧹 Очистка временного кэша pip..."
"$ENV_PIP" cache purge -q
echo "✅ Кэш pip очищен."

# Создаем структуру каталогов проекта
echo "📂 Создаем структуру каталогов проекта..."
mkdir -p "$(pwd)/data/raw"
mkdir -p "$(pwd)/data/processed"
mkdir -p "$(pwd)/notebooks"
mkdir -p "$(pwd)/src"
mkdir -p "$(pwd)/models"
mkdir -p "$(pwd)/reports"
mkdir -p "$(pwd)/src/storage/mlflow_cache"

echo -e "\n💡 Чтобы начать работу, активируйте окружение командой:"
echo -e "   \033[1;32mset +u && source $ENV_DIR/bin/activate && set -u\033[0m"

echo -e "\n📦 Рекомендуется экспортировать путь для локального хранения логов MLflow:"
echo -e "   \033[1;36mexport MLFLOW_TRACKING_URI=\"$(pwd)/src/storage/mlflow_cache\"\033[0m\n"
