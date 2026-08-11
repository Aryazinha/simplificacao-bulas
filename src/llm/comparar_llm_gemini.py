from google import genai
import sys
import os

# Defina a variável de ambiente GEMINI_API_KEY com sua chave da API
CHAVE_API = os.environ.get("GEMINI_API_KEY")

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def reconstruir_bula_com_gemini() -> str:

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

    if not CHAVE_API:
        print("Erro: defina a variável de ambiente GEMINI_API_KEY com sua chave da API.")
        return None

    try:
        client = genai.Client(api_key=CHAVE_API)

        resposta = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

    except Exception as e:
        print(f"Erro ao se comunicar com o Gemini: {e}")
        return None

    texto_resposta = resposta.text

    nome_arquivo = "resultados/resultado_gemini.txt"

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(texto_resposta)

    print(f"Resultado salvo em '{nome_arquivo}'")

    return texto_resposta


if __name__ == "__main__":

    resultado = reconstruir_bula_com_gemini()

    if resultado:
        print("\n===== TEXTO RECONSTRUÍDO PELO GEMINI =====\n")
        print(resultado)