> Tradução comunitária (rascunho) — Política NTARI P2-002, Transmissão Multilíngue Global. Fonte: README.md (original em inglês, snapshot de 2026-07-29). Rascunho comunitário assistido por máquina, pendente de revisão por mantenedor regional conforme P2-002 §3.1. As especificações técnicas centrais permanecem em inglês conforme §2.2.
>
> Notou algum erro nesta tradução? Correções de tradução são contribuições
> valiosas e muito bem-vindas: faça um fork do repositório e abra um pull
> request em
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

# Leveson-Based Trade Assessment Scale (LBTAS)

Um sistema de avaliação para o comércio digital baseado na metodologia de avaliação de software aeronáutico de Nancy Leveson, com critérios de avaliação bidirecional.

## Visão Geral

A Escala de Avaliação Comercial Baseada em Leveson (LBTAS) implementa a metodologia de avaliação de software aeronáutico de Nancy Leveson, desenvolvida para aplicações aeroespaciais, adaptada para contextos de comércio digital e avaliação econômica. A LBTAS fornece um framework para capturar dados de qualidade de transações usando uma escala de 6 pontos.

## O Problema dos Sistemas de Avaliação Tradicionais

Sistemas de 5 estrelas não fornecem dados que motivem a melhoria dos produtores. O sistema de 5 estrelas foi desenvolvido em 1958 pelo Forbes Travel Guide (antigo Mobil Travel Guide) para divulgar a qualidade de hotéis ao longo das rodovias interestaduais dos EUA. Ele foi projetado como um sistema de comunicação unidirecional para viagens rodoviárias, não para o comércio digital.

**Limitações:**
- As avaliações oferecem valor limitado em contextos de e-commerce
- Gerentes de relações públicas criam barreiras a mudanças de política
- A granularidade não consegue capturar a complexidade das transações
- A avaliação unidirecional ignora a responsabilidade do consumidor
- A insuficiência de dados força a dependência de seções de comentários

## Por que a Abordagem Leveson?

O Sistema Leveson tem origem no desenvolvimento de software aeronáutico, em que falhas de sistema resultam em perda de vidas ou em investimento de P&D desperdiçado. Essa metodologia:

- Usa uma escala de 6 pontos (de +4 a -1) com definições por categoria
- Comprime significado em cada nível de avaliação
- Reduz a dependência de seções de comentários para obtenção de dados
- Permite avaliação bidirecional (tanto do produtor quanto do consumidor)
- Dá suporte a ciclos de melhoria orientados por dados

## Definições da Escala

### +4 **Encantamento**
A interação antecipa a evolução das práticas e preocupações do usuário após a transação

### +3 **Sem Consequências Negativas**
Interação projetada para prevenir perdas, superando os padrões básicos de qualidade

### +2 **Satisfação Básica**
A interação atende a padrões socialmente aceitáveis, superando as demandas articuladas pelo usuário

### +1 **Promessa Básica**
A interação atende a todas as demandas articuladas pelo usuário, nada mais

### 0 **Satisfação Cínica**
A interação cumpre uma promessa básica exigindo pouca ou nenhuma disciplina voltada à satisfação do usuário

### -1 **Sem Confiança**
O usuário foi prejudicado, explorado ou recebeu um produto/serviço com evidências de ausência de disciplina ou de intenção maliciosa

## Avaliação Bidirecional

A LBTAS possibilita a responsabilização de mão dupla em redes digitais ao manter avaliações tanto para:

- **Produtores**: Identifica fornecedores
- **Consumidores**: Identifica clientes

Essa abordagem facilita a autorregulação comunitária e reduz a necessidade de moderação centralizada.

## Interpretando a reputação

As avaliações nunca são calculadas como média. Uma reputação é a contagem de avaliações recebidas em cada nível (de `-1` a `+4`) mais o total. O total importa por si só: ele reflete o volume de transações e, indiretamente, o tempo em serviço. Uma distribuição limpa ao longo de 5.000 avaliações é um sinal mais forte do que o mesmo formato ao longo de 5 — e a média apagaria essa diferença ao colapsar ambas para o mesmo número. (A contagem é uma contagem de avaliações; números precisos de transações e de tempo de atuação vêm da API, que registra o timestamp de cada evento de avaliação.)

Um `-1` ("Sem Confiança") nunca é diluído: o comando `report` exibe cada troca que recebeu uma ou mais avaliações `-1` em uma lista `harm_flagged`, e o `list` anexa um sinalizador de dano a qualquer troca com um `-1`.

## Funcionalidades

- **Metodologia**: Baseada em frameworks de avaliação aeroespacial
- **Avaliação Bidirecional**: Avalie ambas as partes nas transações
- **Granularidade**: Escala de 6 pontos com definições
- **Dependências**: Integração em sistemas
- **Suporte a Banco de Dados**: Suporte a camada de persistência
- **Código Aberto**: Desenvolvimento e customização orientados pela comunidade

## Instalação

```bash
# Clone the repository
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale

# Make executable (optional)
chmod +x lbtas.py

# Run directly
python3 lbtas.py --help
```

Nenhuma dependência externa é necessária. Usa apenas a biblioteca padrão do Python 3.

## Início Rápido

```python
from lbtas import LevesonRatingSystem

# Initialize the rating system
rating_system = LevesonRatingSystem()

# Add an exchange (transaction)
rating_system.add_exchange("transaction_001")

# Add ratings (categories: reliability, usability, performance, support)
rating_system.add_rating(
    exchange_name="transaction_001",
    criterion="reliability",
    rating=3  # No Negative Consequences
)

# Read the distribution (ratings are never averaged)
ratings = rating_system.view_ratings("transaction_001")
print(ratings["reliability"])
# {'distribution': {'-1': 0, '0': 0, '1': 0, '2': 0, '3': 1, '4': 0}, 'total': 1}
```

### Interface de Linha de Comando

```bash
# Interactive rating
python3 lbtas.py rate --exchange "MyService"

# Programmatic rating
python3 lbtas.py add --exchange "MyService" --criterion reliability --rating 3

# View ratings
python3 lbtas.py view --exchange "MyService"

# Generate report
python3 lbtas.py report

# Export data
python3 lbtas.py export --format json --output ratings.json
```

## Armazenamento

A LBTAS usa armazenamento em arquivo JSON para persistência:

```python
# Initialize with storage file
rating_system = LevesonRatingSystem(storage_file='ratings.json')

# Ratings are saved automatically to the file
rating_system.add_exchange("service_001")
rating_system.add_rating("service_001", "reliability", 3)
```

Formato do arquivo de armazenamento:
```json
{
  "service_001": {
    "reliability": [3, 4, 3],
    "usability": [2, 3],
    "performance": [4],
    "support": [3, 3, 2],
    "_metadata": {
      "created": "2024-09-04T10:30:00",
      "total_ratings": 10
    }
  }
}
```

### Categorias de Avaliação

Categorias padrão:
- **Reliability** (confiabilidade): Confiabilidade e consistência
- **Usability** (usabilidade): Facilidade de uso e experiência do usuário
- **Performance** (desempenho): Velocidade e eficiência
- **Support** (suporte): Qualidade do atendimento ao cliente

Categorias personalizadas podem ser definidas durante a inicialização.

## Casos de Uso

### Pesquisa Acadêmica
- Estudar como o design da escala de avaliação afeta o comportamento dos usuários e os resultados de mercado
- Medir os efeitos da avaliação bidirecional sobre a confiança e a cooperação
- Analisar alternativas de avaliação baseadas em qualidade em relação a outros frameworks

### Plataformas de E-Commerce
- Implementar métricas de qualidade para transações de marketplace
- Habilitar sistemas de reputação orientados pela comunidade
- Reduzir a sobrecarga de moderação por meio da autorregulação

### Cooperativas Digitais
- Facilitar a responsabilização entre pares (peer-to-peer)
- Dar suporte a estruturas de governança
- Habilitar melhorias de políticas orientadas por dados

## Arquitetura

A LBTAS é implementada como um único módulo Python com:

1. **Classe principal**: `LevesonRatingSystem` gerencia as avaliações e o armazenamento
2. **Persistência em JSON**: Armazenamento baseado em arquivo com salvamento automático
3. **Interface CLI**: Ferramenta de linha de comando para uso interativo e programático
4. **Sem dependências externas**: Usa apenas a biblioteca padrão do Python

O sistema oferece suporte a:
- Coleta interativa de avaliações
- Envio programático de avaliações
- Categorias de avaliação personalizadas
- Geração de relatórios e exportação de dados

## Documentação

- [Documentação Completa](docs/README.md)
- [Referência da API](docs/api.md)
- [Guia de Integração](docs/integration.md)
- [Aplicações em Pesquisa](docs/research.md)

## Como Contribuir

As contribuições são feitas por meio do workspace do Slack da NTARI:

**Participe da discussão**: https://ntari.slack.com/archives/C09N88JN2SH

Consulte nossas [Diretrizes de Contribuição](CONTRIBUTING.md) para:

- Estilo e padrões de código
- Requisitos de testes
- Processo de pull request
- Código de conduta da comunidade

## Pesquisa e Desenvolvimento

Este programa foi produzido pelo **Forge Laboratory do Network Theory Applied Research Institute** (atual NTARI Research & Development) por Jodson B. Graves usando o ChatGPT-3 em 4 de setembro de 2024.

### Sobre o NTARI Research & Development

O NTARI Research & Development é o programa de desenvolvimento de software da NTARI para a criação de sistemas e protocolos digitais que aproveitam a teoria de redes para aprimorar as capacidades cooperativas em toda a internet. Desenvolvemos ferramentas, plataformas e frameworks de código aberto que capacitam comunidades a construir ecossistemas online.

**Saiba mais e apoie a NTARI**: [https://ntari.org](https://ntari.org)

## Citação

Se você usar a LBTAS em sua pesquisa, cite:

```bibtex
@software{lbtas2024,
  title={Leveson-Based Trade Assessment Scale},
  author={Graves, Jodson B.},
  organization={Network Theory Applied Research Institute},
  year={2024},
  url={https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale}
}
```

## Referências

- Leveson, N. G. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press.
- Leveson, N. G. (2020). *CAST Handbook: How to Learn More from Incidents and Accidents*. MIT.

## Licença

Este projeto é licenciado sob a GNU Affero General Public License v3.0 (AGPL-3.0) — consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

A licença AGPL-3.0 exige que:
- O código-fonte seja disponibilizado quando o software for usado por meio de uma rede
- As modificações sejam publicadas sob a mesma licença
- As alterações sejam documentadas
- O uso em rede seja considerado distribuição

## Agradecimentos

- **Nancy Leveson** — Desenvolvimento da metodologia original
- **NTARI Research & Development** — Pesquisa e implementação
- **Comunidade de Código Aberto** — Contribuições e feedback

---

**Mantido por**: [NTARI Research & Development](https://ntari.org)  
**Dúvidas?** Abra uma issue ou entre em contato pelo e-mail info@ntari.org
