import os
import shutil
import json

def main():
    print("\n=== Assistente de Configuração Inicial ===")
    
    # 1. Garantir diretório data
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Diretório '{data_dir}' criado.")

    # 2. Copiar ou Criar CSV
    print("\n[1/2] Configuração do Arquivo de Dados (CSV)")
    print("Informe o caminho do arquivo CSV que deseja importar.")
    csv_path = input("Caminho para o arquivo CSV (deixe em branco para criar um exemplo): ").strip()
    
    target_csv_name = "exemplo.csv"
    
    if csv_path:
        # Remove aspas que terminais as vezes adicionam ao arrastar arquivos
        csv_path = csv_path.replace("'", "").replace('"', "")
        
        if os.path.exists(csv_path):
            filename = os.path.basename(csv_path)
            target_path = os.path.join(data_dir, filename)
            shutil.copy2(csv_path, target_path)
            target_csv_name = filename
            print(f"Arquivo copiado para: {target_path}")
        else:
            print(f"AVISO: Arquivo '{csv_path}' não encontrado. Gerando arquivo de exemplo...")
            create_dummy_csv(os.path.join(data_dir, target_csv_name))
    else:
        create_dummy_csv(os.path.join(data_dir, target_csv_name))
        print(f"Arquivo de exemplo criado em: {os.path.join(data_dir, target_csv_name)}")

    # 3. Gerar JSON
    print(f"\n[2/2] Configuração do JSON para '{target_csv_name}'")
    print("Preencha os dados abaixo para gerar o arquivo de configuração obrigatório.")
    
    config = {}
    config["api_key"] = input("API Key do Gov.br: ").strip()
    
    env_input = input("Ambiente (1-HOMOLOGACAO, 2-PRODUCAO) [1]: ").strip()
    config["env"] = "PRODUCAO" if env_input == "2" else "HOMOLOGACAO"
    
    config["assunto"] = input("Assunto da Mensagem: ").strip()
    config["template_id"] = input("ID do Template: ").strip()
    config["versao"] = input("Versão do Template: ").strip()
    
    tags_str = input("Tags/Variáveis do CSV (separadas por vírgula, ex: nome,data): ").strip()
    config["tags"] = [t.strip() for t in tags_str.split(",") if t.strip()]

    # Salvar JSON
    json_filename = f"{target_csv_name}.json"
    json_path = os.path.join(data_dir, json_filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        
    print(f"\nSucesso! Arquivo de configuração gerado: {json_path}")

def create_dummy_csv(path):
    content = "cpf,nome\n00000000000,Cidadão Exemplo"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    main()