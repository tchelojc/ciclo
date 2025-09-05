import os

TARGET_IMPORT = "from shared_imports import QLineEdit"
KEYWORD = "QLineEdit"

for root, _, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.readlines()

            if any(KEYWORD in line for line in content) and not any("QLineEdit" in line and "import" in line for line in content):
                print(f"🛠️ Corrigindo importação em {file_path}")
                # Insere no topo após comentários iniciais
                insert_index = 0
                for i, line in enumerate(content):
                    if not line.strip().startswith("#") and line.strip() != "":
                        insert_index = i
                        break
                content.insert(insert_index, TARGET_IMPORT + "\n")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(content)
