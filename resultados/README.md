# Baseline de Extração OCR

Os arquivos nesta pasta (como `baseline_ocr.txt`) representam o "Padrão Ouro" da etapa de OCR da Fase 1, usados para garantir que refatorações arquiteturais não causem regressão (mudanças indesejadas no texto extraído).

**Commit Base:** `482e9a9` (Ponto Zero pré-refatoração)
**Última Atualização:** Fase 2 - Refatoração em Camadas

> Nota: Durante os testes automatizados, qualquer execução de script que gere o `bula_extraida.txt` deve resultar em um arquivo perfeitamente idêntico a nível de bytes ao `baseline_ocr.txt`.
