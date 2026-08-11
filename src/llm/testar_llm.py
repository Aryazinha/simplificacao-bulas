import ollama
import sys
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def escolher_modelo_ollama() -> str:

    print("Modelos disponíveis no Ollama:")
    print("1 - qwen2.5vl:7b")
    print("2 - llama3.2")
    print("3 - granite3.2")

    modelos = {
        "1": "qwen2.5vl:7b",
        "2": "llama3.2",
        "3": "granite3.2"
    }

    opcao = input("Escolha um modelo: ")

    if opcao not in modelos:
        print("Opção inválida.")
        return None

    return modelos.get(opcao)

def extrair_dados_com_ollama() -> str:

    modelo = escolher_modelo_ollama()

    if not modelo:
        print("Nenhum modelo válido foi escolhido.")
        return None

    print(f"Modelo escolhido: {modelo}")
    
    arquivo_ocr = "resultados/bula_extraida.txt"

    if not os.path.exists(arquivo_ocr):
        print(f"Arquivo '{arquivo_ocr}' não encontrado. Execute o OCR primeiro.")
        return None
    
    with open(arquivo_ocr, "r", encoding="utf-8") as f:
        texto_bula = f.read()

    prompt = f"""
        Você recebeu um texto extraído por OCR de uma bula de medicamento.

        O texto pode conter erros de reconhecimento de caracteres, palavras incompletas,
        linhas quebradas e problemas de formatação causados pelo processo de OCR.

        Sua tarefa é reconstruir o texto da bula da forma mais fiel possível ao documento original.

        REGRAS OBRIGATÓRIAS:

        - Responda exclusivamente em Português do Brasil.
        - Corrija apenas erros evidentes causados pelo OCR.
        - Não invente informações que não estejam presentes no texto.
        - Não utilize conhecimento prévio sobre o medicamento.
        - Não resuma o conteúdo.
        - Não omita nenhuma informação.
        - Preserve a estrutura da bula sempre que possível.
        - Preserve títulos, subtítulos, listas e ordem das informações.
        - Caso alguma palavra esteja ilegível ou não possa ser determinada com segurança, mantenha-a como foi reconhecida pelo OCR.

        Texto obtido pelo OCR:

        {texto_bula}
        """
        # "Símbolos soltos, barras (|), pontos de exclamação no início de frases ou caracteres aleatórios gerados por ruído na imagem devem ser ignorados e removidos."
    try:
        resposta = ollama.chat(
            model=modelo,
            messages=[
                {"role": "user", "content": prompt} # "o usuário escreveu isso"
            ]
        )
    except Exception as e:
        print(f"Erro ao se comunicar com o Ollama: {e}")
        return None

    nome_arquivo_saida = f"resultados/resultado_ollama_{modelo.replace(':', '_').replace('.', '_')}.txt"
    texto_resposta = resposta["message"]["content"].strip()

    with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
        f.write(texto_resposta)

    print(f"Resultado salvo em '{nome_arquivo_saida}'")

    return texto_resposta

if __name__ == "__main__":
    resultado = extrair_dados_com_ollama()

    if resultado:
        print("Dados extraídos com sucesso:")
        print(resultado)