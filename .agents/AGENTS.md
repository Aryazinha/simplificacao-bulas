# Regras de Versionamento

Siga estas regras em todo trabalho neste repositório, sem precisar de lembrete.

## 1. Branch por conjunto de alterações

Antes da primeira alteração, crie uma branch com nome descritivo do trabalho:

```bash
git checkout -b <nome-do-trabalho>
```

Nunca commite direto na branch principal. Se perceber que está nela, crie a branch antes de continuar. Aprovação de um merge não vale para o merge seguinte.

## 2. Commite em blocos que se sustentam sozinhos

Um commit por unidade coerente de trabalho — um script novo, uma correção, uma decisão registrada na documentação. Não acumule alterações não relacionadas num commit só, e não deixe trabalho pronto sem commitar: o que não está commitado se perde se a sessão terminar.

Commite também antes de qualquer operação arriscada (reescrever arquivo grande, mexer em configuração, rodar processo longo).

## 3. Escolha o que entra, arquivo por arquivo

```bash
git add caminho/do/arquivo.py outro/arquivo.md
```

Nunca use `git add .` nem `git add -A`. Confira antes com `git status --short` o que está modificado, e nomeie só o que pertence àquele commit. Dados gerados, saídas de execução e arquivos grandes não entram no repositório — se aparecerem como não rastreados, avise em vez de commitar.

## 4. Mensagem com o que mudou e por quê

```bash
git commit -F - <<'EOF'
Titulo curto no imperativo, ate 72 caracteres

- o que mudou, em uma linha por ponto
- por que mudou: o problema que resolve ou a decisao que registra
- o que ficou de fora e por que, se for o caso
EOF
```

A mensagem é para quem ler o histórico daqui a seis meses sem o contexto da conversa. Registre a razão, não só o efeito.

## 5. Envie a branch, e pare aí

```bash
git push -u origin <nome-do-trabalho>
```

**Não integre à branch principal por conta própria.** Ao terminar o trabalho, relate o que foi commitado e pergunte se pode integrar. Só com resposta afirmativa explícita:

```bash
git checkout main
git pull --ff-only origin main
git merge --no-ff <nome-do-trabalho> -m "Integra <nome-do-trabalho>: <resumo>"
git push origin main
git branch -d <nome-do-trabalho>
git push origin --delete <nome-do-trabalho>
```

O `--no-ff` preserva o bloco de trabalho como unidade no histórico. Apagar a branch depois do merge evita que a lista sugira trabalho pendente inexistente.

## 6. Proibições

- Não use `--no-verify` nem desative hooks; se um hook falhar, corrija a causa.
- Não use `git push --force` nem reescreva histórico já enviado.
- Não use comandos interativos (`rebase -i`, `add -i`), que travam a sessão.
- Não faça `git reset --hard`, `checkout --` ou descarte de alterações sem autorização explícita — pode apagar trabalho não commitado.
- Não altere configuração de usuário nem credenciais do Git.

## 7. Relate sempre

Depois de cada commit, informe o hash curto, a branch e, em uma linha, o que entrou. Ao fim do trabalho, informe o que está commitado, o que está enviado e o que continua sem commitar, se houver.
