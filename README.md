# Simplificação Automática de Bulas de Medicamentos

Projeto de pesquisa que combina **OCR** (Reconhecimento Ótico de Caracteres) e **PLN** (Processamento de Linguagem Natural) com **LLMs** para extrair e simplificar automaticamente o conteúdo de bulas farmacêuticas, tornando-as acessíveis a pacientes com baixo letramento em saúde.

## Motivação

Bulas de medicamentos costumam usar linguagem técnica de difícil compreensão para o público leigo, o que compromete a adesão ao tratamento e aumenta o risco de erros de uso. O objetivo deste projeto é desenvolver uma solução que extraia o texto de bulas físicas (via foto) e reescreva seu conteúdo em linguagem acessível, preservando a fidelidade e a segurança das informações clínicas.

## Objetivo geral

Desenvolver um aplicativo móvel assistivo, integrado a módulos de OCR e PLN, para extrair e simplificar automaticamente o conteúdo de bulas farmacêuticas.

## Objetivos específicos

- Mapear o estado da arte sobre simplificação automática de texto (ATS) e engenharia de prompts aplicadas ao domínio farmacêutico.
- Desenvolver um pipeline de OCR para extração de texto de bulas físicas fotografadas.
- Integrar módulos de PLN baseados em LLMs para simplificação automática do conteúdo farmacológico extraído.
- Projetar uma interface móvel acessível, com suporte a leitura em voz alta (Text-to-Speech) e agenda posológica.
- Avaliar a qualidade das simplificações geradas por métricas computacionais de legibilidade (Índice Flesch) e de similaridade semântica, garantindo que nenhuma informação clínica seja perdida ou distorcida.

## Arquitetura planejada

- **OCR**: extração de texto de fotos de bulas físicas.
- **PLN / LLMs**: simplificação da terminologia farmacológica via APIs de modelos de linguagem (Gemini, com avaliação de alternativas como GPT-4o e Claude), usando técnicas de engenharia de prompts (Few-Shot, Chain-of-Thought) para manter fidelidade semântica ao conteúdo original.
- **Backend**: API em Python (FastAPI) mediando a comunicação entre o app móvel e os serviços de OCR/IA.
- **Frontend móvel**: aplicativo multiplataforma (Flutter), com navegação temática guiada por perguntas simples (ex: "Para que serve?", "Como devo tomar?"), mapeadas às seções obrigatórias das bulas de paciente.
- **Avaliação**: comparação do Índice de Legibilidade Flesch antes/depois da simplificação e verificação de similaridade semântica (embeddings) entre o texto original e o simplificado, para detectar perdas de informação ou alucinações do modelo.

## Estado atual

Este repositório contém experimentos exploratórios da fase inicial do projeto, usados para validar a viabilidade técnica do pipeline antes da construção do backend/app definitivos:

- **OCR** ([src/ocr/bula.py](src/ocr/bula.py), [src/ocr/teste_ocr.py](src/ocr/teste_ocr.py)) — pré-processamento de imagem com OpenCV (resize, denoising, binarização adaptativa) e extração de texto com Tesseract.
- **Reconstrução/simplificação via LLM** ([src/llm/comparar_llm_gemini.py](src/llm/comparar_llm_gemini.py), [src/llm/testar_llm.py](src/llm/testar_llm.py)) — testes com Gemini e modelos locais via Ollama para reconstruir o texto extraído por OCR.
- **Avaliação de precisão** ([src/comparacao/comparar_ocr.py](src/comparacao/comparar_ocr.py), [src/comparacao/comparar_llm.py](src/comparacao/comparar_llm.py)) — cálculo da taxa de erro de caracteres (CER) comparando o texto extraído/reconstruído com um gabarito de referência.
- **Dados de referência externos** ([src/api/buscar_api.py](src/api/buscar_api.py)) — consulta à API pública openFDA para enriquecer o contexto sobre princípios ativos.

## Estrutura de pastas

```
src/
  ocr/          Extração de texto de imagens de bulas (Tesseract)
  llm/          Reconstrução/simplificação do texto via LLMs (Gemini, Ollama)
  comparacao/   Cálculo de precisão (CER) contra o gabarito
  api/          Consulta a dados de referência externos (openFDA)
dados/
  entrada/      Imagens e PDFs de bulas usados como entrada
  processadas/  Imagens intermediárias geradas pelo pré-processamento do OCR
  gabarito/     Texto de referência usado para medir a precisão
resultados/     Textos extraídos/reconstruídos e histórico de métricas
```

Os scripts usam caminhos relativos e devem ser executados a partir da raiz do projeto, por exemplo:

```
python src/ocr/bula.py
```

Os caminhos são resolvidos a partir da raiz do projeto, então os scripts também
funcionam quando chamados de outro diretório. Todos aceitam `--help`.

## Requisitos

- Python 3
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract) instalado localmente
- Dependências Python: `pip install -r requirements.txt`
- [Ollama](https://ollama.com/) rodando localmente, com os modelos usados em [src/llm/testar_llm.py](src/llm/testar_llm.py) baixados

## Configuração

Copie `.env.example` para `.env` e preencha os valores. Os scripts carregam esse
arquivo automaticamente (sem sobrescrever variáveis já definidas no ambiente):

```
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

`GEMINI_MODEL` e `TESSERACT_CMD` são opcionais: o modelo tem um padrão embutido e,
sem `TESSERACT_CMD`, usa-se o `tesseract` disponível no PATH.

## Fluxo de uso

```
python src/ocr/bula.py                                    # foto -> resultados/bula_extraida.txt
python src/comparacao/comparar_ocr.py                     # CER do OCR bruto
python src/llm/comparar_llm_gemini.py                     # reconstrução via Gemini
python src/llm/testar_llm.py --modelo qwen2.5vl:7b        # reconstrução via Ollama
python src/comparacao/comparar_llm.py resultados/resultado_gemini.txt --modelo Gemini
```

## Medição de precisão (CER)

[src/comparacao/comparar_llm.py](src/comparacao/comparar_llm.py) recebe o arquivo a
medir como argumento e grava o nome do modelo informado em
`resultados/historico_resultados.txt`, de modo que cada linha do histórico
corresponda ao arquivo efetivamente comparado.

Antes de calcular o CER, os textos passam por uma normalização que remove marcação
Markdown (negrito, títulos, marcadores de lista, blocos de código) e uniformiza
espaços. As LLMs devolvem o texto formatado e o gabarito não é formatado; sem essa
etapa, a formatação entra na conta como erro de reconstrução. Use `--bruto` para
comparar sem normalizar.

> As linhas do histórico anteriores a esta mudança foram geradas com o arquivo e o
> nome do modelo fixos no código, e sem normalização — não são comparáveis diretamente
> com as linhas novas, que trazem o sufixo `| Texto: normalizado`.
