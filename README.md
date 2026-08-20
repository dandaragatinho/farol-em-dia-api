# Farol em Dia — API

API REST para o sistema **Farol em Dia**, criada para organizar clientes, veículos e ordens de serviço de uma oficina especializada em manutenção de faróis.

## Tecnologias

- Python 3.10 ou superior;
- Flask;
- SQLite;
- Flasgger/Swagger (OpenAPI);
- Flask-Cors.

## Funcionalidades

- Cadastro e consulta de clientes;
- Cadastro e consulta de veículos vinculados aos clientes;
- Criação, consulta, atualização de status e exclusão de ordens de serviço;
- Relacionamentos entre três tabelas SQLite;
- Indicadores para a tela inicial;
- Validação dos dados e respostas de erro em JSON;
- Documentação interativa de todas as rotas.

## Instalação

1. Clone este repositório e acesse a pasta do projeto.
2. Crie um ambiente virtual:

```bash
python -m venv .venv
```

3. Ative o ambiente virtual.

No Windows:

```powershell
.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Inicialização

Execute:

```bash
python app.py
```

A API ficará disponível em `http://127.0.0.1:5000`.

Na primeira execução, o banco `instance/farol_em_dia.db` será criado automaticamente com dados de demonstração.

## Documentação Swagger

Com a API em execução, abra:

```text
http://127.0.0.1:5000/apidocs/
```

A página permite consultar os métodos HTTP, estruturas de requisição e resposta e códigos de status esperados.

## Rotas principais

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/saude` | Verifica a disponibilidade da API |
| `GET` | `/api/dashboard` | Retorna indicadores e ordens recentes |
| `GET` | `/api/clientes` | Lista clientes |
| `POST` | `/api/clientes` | Cadastra um cliente |
| `DELETE` | `/api/clientes/{id}` | Exclui um cliente sem vínculos |
| `GET` | `/api/veiculos` | Lista veículos |
| `POST` | `/api/veiculos` | Cadastra um veículo |
| `DELETE` | `/api/veiculos/{id}` | Exclui um veículo sem ordens |
| `GET` | `/api/ordens` | Lista ordens de serviço |
| `POST` | `/api/ordens` | Cria uma ordem de serviço |
| `PATCH` | `/api/ordens/{id}` | Atualiza o status de uma ordem |
| `DELETE` | `/api/ordens/{id}` | Exclui uma ordem |

## Banco de dados

O SQLite utiliza três tabelas relacionadas:

- `clientes`;
- `veiculos`, vinculada a `clientes`;
- `ordens_servico`, vinculada a `veiculos`.

Os arquivos `schema.sql` e `seed.sql` documentam a estrutura e os dados iniciais.

## Testes

Com as dependências instaladas, execute:

```bash
python -m unittest discover -s tests -v
```

Os testes usam um banco temporário e verificam o fluxo completo de cadastro, atualização, consulta e exclusão.
