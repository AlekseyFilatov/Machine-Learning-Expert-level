import os
import zipfile
from datetime import datetime

def pack_ds_project():
    # Имя будущего архива с текущей датой
    current_date = datetime.now().strftime("%Y%m%d")
    zip_filename = f"ds_project_submission_{current_date}.zip"
    
    # Список папок, которые МЫ ХОТИМ упаковать
    folders_to_include = ['data/raw', 'data/processed', 'notebooks', 'src', 'models', 'reports']
    
    # Список файлов в корне, которые нужно включить
    files_to_include = ['requirements.txt', 'README.md']
    
    # Список исключений (что мы НЕ берем ни при каких условиях)
    exclude_extensions = ('.pyc', '.pyd', '.pyo')
    exclude_dirs = ['__pycache__', '.pytest_cache', '.ipynb_checkpoints', '.venv', 'mlruns', '.git']

    print(f"⏳ Начинаю упаковку проекта в архив: {zip_filename}...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Упаковываем разрешенные папки и их содержимое
        for folder in folders_to_include:
            if not os.path.exists(folder):
                continue
                
            for root, dirs, files in os.walk(folder):
                # Фильтруем запрещенные папки (модифицируем dirs на лету)
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    # Фильтруем запрещенные файлы по расширению
                    if file.endswith(exclude_extensions):
                        continue
                        
                    file_path = os.path.join(root, file)
                    # Добавляем файл в архив, сохраняя относительный путь
                    zipf.write(file_path, file_path)
                    print(f"  [+] Добавлен: {file_path}")

        # 2. Упаковываем отдельные файлы из корня проекта
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file, file)
                print(f"  [+] Добавлен корень: {file}")

    file_size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    print("-" * 60)
    print(f"🎉 Успех! Проект упакован.")
    print(f"📦 Имя архива: {zip_filename}")
    print(f"📊 Размер архива: {file_size_mb:.2f} MB")


if __name__ == "__main__":
    pack_ds_project()
