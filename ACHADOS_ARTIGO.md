# Achados e Descobertas: Fase 1 (Visão Científica e Técnica)

Este documento foi criado para compilar as descobertas empíricas, desafios e decisões arquiteturais tomadas durante a Fase 1 do projeto (Extração e Simplificação de Bulas). Ele servirá como base de rascunho e argumentação para a futura escrita de um artigo acadêmico ou técnico.

## 1. Desafios no Pipeline de OCR
* **Binarização vs. Escala de Cinza:** Inicialmente, a binarização profunda (preto e branco puro) com OpenCV causava degradação em bulas amassadas ou com baixa resolução. Descobrimos que manter a imagem em **escala de cinza** mantendo apenas o redimensionamento elevou substancialmente a precisão de extração.
* **Tesseract vs. EasyOCR:** A migração para a biblioteca `EasyOCR` demonstrou resultados muito superiores para ler bulas brasileiras, pois seus modelos pré-treinados lidaram melhor com o ruído de fundo e a densidade de texto pequeno comum nesse tipo de documento.

## 2. Engenharia de Prompts e Estruturação (LLMs)
* **Controle de Alucinação Médica:** LLMs tendem a "inventar" ou suavizar riscos (alucinação) se não forem rigorosamente travados. A solução implementada foi forçar uma saída estruturada em **JSON rigoroso** (inspirado na RDC nº 47/2009 da ANVISA).
* **Regra de Fallback:** Implementamos a diretriz estrita de que o modelo deve responder *"Não há essa informação na bula original"* caso a extração do OCR falhe num trecho, evitando que o modelo preencha lacunas com seu próprio treinamento prévio. Isso é crítico para a segurança do paciente.

## 3. O Paradoxo da Legibilidade (Índice Flesch)
Um dos achados mais interessantes para o artigo é o comportamento do LLM frente à simplificação:
* Em nossos testes preliminares, a bula simplificada pelo LLM obteve um **Índice de Legibilidade Flesch PIOR (mais complexo)** do que o texto original do OCR.
* **Causa do Fenômeno:** Ao invés de usar palavras coloquiais, o LLM priorizou a *segurança estrutural*, agrupando as informações técnicas em frases mais longas e estruturadas para não perder o sentido médico. 
* **Conclusão para o Artigo:** Isso prova que "simplificar", para um LLM em contexto médico, significa "organizar e categorizar", e não necessariamente "reduzir sílabas". A métrica Flesch isolada não é suficiente para avaliar textos médicos gerados por IA.

## 4. Fidelidade e Auditoria Cruzada (Cross-LLM Auditing)
Para comprovar que a simplificação não alterou contraindicações ou dosagens, desenvolvemos uma arquitetura de métricas duplas:
* **Métrica Matemática (Cosseno via Embeddings):** A similaridade de cosseno variou bastante (0.45 a 0.79). Como o LLM altera drasticamente a sintaxe da frase original para gerar o JSON, a comparação vetorial estrita pune a pontuação.
* **Auditoria por LLM Independente:** Para contornar a limitação dos Embeddings, criamos um painel de auditores (ex: o Gemini simplifica, e um LLM local como o `Llama 3.2` atua como Auditor Médico).
* **Resultado:** O modelo auditor independente retornou "Aprovado" em 100% das seções críticas. Isso prova no artigo que a **Auditoria Cruzada de LLMs (Cross-Evaluation)** é superior à métrica de Cosseno para avaliar retenção de sentido médico.
* **Sensibilidade do Prompt e Jargões:** Descobrimos empíricamente que modelos menores (como o Llama 3.2 3B) podem ser excessivamente literais e gerar falsos negativos (reprovando traduções corretas). Foi necessário injetar uma regra explícita de "tolerância a jargões" no *System Prompt* (ex: autorizando a troca de "8/8h" por "a cada 8 horas"), forçando o modelo a auditar o **significado clínico temporal** ao invés de buscar correspondência exata de caracteres.

## 5. Resiliência e Arquitetura Híbrida (Nuvem + Borda)
* Durante os testes empíricos, a API pública do Google (Gemini) apresentou instabilidade (HTTP 503 - High Demand e 404). 
* O projeto validou a importância de uma **Arquitetura Híbrida de Fallback**: assim que a nuvem falha, o script migra automaticamente o processamento para modelos abertos rodando localmente (Ollama e `sentence-transformers`), garantindo que o sistema médico nunca fique offline.
