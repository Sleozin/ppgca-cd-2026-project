---

### 3. Dicionário de Dados (`docs/dicionario_dados.md`)
Aqui está a estrutura de base Markdown exigida para o dicionário[cite: 93, 94]. 

```markdown
# Dicionário de Dados - Camada Mart

O modelo dimensional foi implementado no formato *Star Schema* otimizado para agregações. A granularidade da tabela Fato é ao nível de **cada emenda individual registrada no Portal da Transparência**.

### `fato_emendas`
**Granularidade:** Uma linha por registro de emenda parlamentar.

| Coluna | Tipo | Chave | Aditividade | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `sk_emenda` | VARCHAR | PK | Não-aditiva | Surrogate Key (Hash MD5) única da emenda. |
| `fk_autor` | VARCHAR | FK | Não-aditiva | Chave estrangeira ligando à `dim_autor`. |
| `fk_status` | VARCHAR | FK | Não-aditiva | Chave estrangeira ligando à `dim_status`. |
| `fk_data` | DATE | FK | Não-aditiva | Chave estrangeira ligando à data de emissão na `dim_calendario`. |
| `valor_emenda` | DOUBLE | - | Totalmente aditiva | Valor financeiro bruto da emenda (em Reais). |
| `kpi_valor_milhoes` | DOUBLE | - | Totalmente aditiva | **KPI**: Valor financeiro dividido por 1.000.000 para facilitar visualização de painéis de larga escala. Unidade: R$ Milhões. |
| `kpi_alto_impacto` | INT | - | Semi-aditiva | **KPI**: Flag binária (1=Sim, 0=Não). Emendas superiores a R$ 1.000.000,00 recebem a flag 1. Utilizada para sumarizar e filtrar as emendas mais expressivas. |

### `dim_autor`
**Granularidade:** Uma linha por Parlamentar/Autor único.

| Coluna | Tipo | Chave | Descrição |
| :--- | :--- | :--- | :--- |
| `sk_autor` | VARCHAR | PK | Surrogate key (Hash do Nome + Partido). |
| `nome_autor` | VARCHAR | - | Nome oficial do autor da emenda. |
| `partido_autor` | VARCHAR | - | Sigla do partido político associado no momento da emenda. |
| `uf_autor` | VARCHAR | - | Unidade Federativa (Estado) de representação. |

### `dim_calendario`
**Granularidade:** Uma linha por dia do calendário, cobrindo dinamicamente o período dos dados reais.

| Coluna | Tipo | Chave | Descrição |
| :--- | :--- | :--- | :--- |
| `sk_data` | DATE | PK | Data civil no formato YYYY-MM-DD. |
| `dia` | INT | - | Dia do mês (1 a 31). |
| `mes` | INT | - | Mês do ano (1 a 12). |
| `ano` | INT | - | Ano com quatro dígitos (ex: 2024). |
| `trimestre` | INT | - | Trimestre do ano (1 a 4). |
| `dia_semana` | VARCHAR | - | Nome do dia da semana (ex: Monday, Tuesday). |