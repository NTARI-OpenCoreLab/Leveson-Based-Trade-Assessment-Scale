> Tradução comunitária (rascunho) — Política NTARI P2-002, Transmissão Multilíngue Global. Fonte: contributing.md (original em inglês, snapshot de 2026-07-29). Rascunho comunitário assistido por máquina, pendente de revisão por mantenedor regional conforme P2-002 §3.1. As especificações técnicas centrais permanecem em inglês conforme §2.2.
>
> Notou algum erro nesta tradução? Correções de tradução são contribuições
> valiosas e muito bem-vindas: faça um fork do repositório e abra um pull
> request em
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

# Contribuindo para o LBTAS

## Como Contribuir

As contribuições são feitas por meio do workspace da NTARI no Slack.

**Participe da discussão**: https://ntari.slack.com/archives/C09N88JN2SH

## Tipos de Contribuição

### Contribuições de Código
- Correções de bugs
- Implementações de funcionalidades
- Melhorias de desempenho
- Atualizações de documentação

### Contribuições de Pesquisa
- Estudos de caso de uso
- Artigos acadêmicos que utilizam o LBTAS
- Exemplos de integração
- Análise da eficácia das avaliações

### Contribuições da Comunidade
- Relato de issues
- Sugestões de funcionalidades
- Melhorias na documentação
- Apoio à tradução

## Processo de Desenvolvimento

### 1. Discussão
Discuta as alterações propostas no canal do Slack antes de começar o trabalho.

### 2. Fork e Branch
```bash
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale
git checkout -b feature/your-feature-name
```

### 3. Padrões de Código

**Estilo Python**
- Siga o PEP 8
- Use type hints
- Inclua docstrings em todas as funções e classes
- Mantenha as funções focadas e com menos de 50 linhas

**Estilo de Documentação**
- Escreva em linguagem factual e técnica
- Evite adjetivos e advérbios
- Inclua exemplos de código
- Teste todos os exemplos

### 4. Testes

Teste suas alterações:
```bash
# Test basic functionality
python3 lbtas.py rate --exchange "TestService"
python3 lbtas.py view --exchange "TestService"
python3 lbtas.py report

# Test as library
python3 -c "from lbtas import LevesonRatingSystem; rs = LevesonRatingSystem(); rs.add_exchange('test'); print('OK')"
```

### 5. Mensagens de Commit

Formato: `type: brief description`

Tipos:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `refactor`: Reestruturação de código
- `test`: Adições ou alterações de testes
- `chore`: Tarefas de manutenção

Exemplos:
```
feat: add CSV export format
fix: handle empty rating lists in report
docs: update installation instructions
```

### 6. Pull Request

1. Faça push da sua branch para o seu fork
2. Abra um pull request para a branch main
3. Referencie quaisquer issues relacionadas
4. Descreva as alterações feitas e a justificativa
5. Aguarde a revisão e a discussão no Slack

## Código de Conduta

### Padrões

- Respeite todos os contribuidores
- Concentre-se no mérito técnico
- Forneça feedback construtivo
- Aceite críticas às suas contribuições
- Priorize os objetivos do projeto em vez de preferências pessoais

### Comportamento Proibido

- Ataques pessoais ou assédio
- Linguagem ou comportamento discriminatório
- Trolling ou comentários inflamatórios
- Compartilhamento de informações privadas de terceiros
- Conduta antiética ou não profissional

### Aplicação

Violações podem resultar em:
1. Advertência
2. Suspensão temporária do projeto
3. Banimento permanente do projeto

Relate violações para: forge@ntari.org

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a AGPL-3.0.

Todas as contribuições devem:
- Ser trabalho original seu ou devidamente atribuído
- Não violar direitos de terceiros
- Cumprir os requisitos da AGPL-3.0

## Dúvidas

Para dúvidas sobre como contribuir:
1. Pergunte no Slack: https://ntari.slack.com/archives/C09N88JN2SH
2. Abra uma issue no GitHub
3. E-mail: forge@ntari.org

## Reconhecimento

Os contribuidores são reconhecidos em:
- Histórico de commits do Git
- Notas de lançamento
- Documentação do projeto

Tipos de contribuição reconhecidos:
- Contribuições de código (commits)
- Contribuições de pesquisa (citações)
- Contribuições de documentação (créditos de documentação)
- Apoio à comunidade (agradecimentos)
