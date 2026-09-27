import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flasgger import Swagger


STATUS_VALIDOS = {
    "recebida",
    "em_servico",
    "aguardando_peca",
    "pronta",
    "entregue",
}


def agora_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def linha_para_dict(linha):
    return dict(linha) if linha is not None else None


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(g.app_config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def fechar_db(_erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def resposta_erro(mensagem, status=400, detalhes=None):
    corpo = {"erro": mensagem}
    if detalhes:
        corpo["detalhes"] = detalhes
    return jsonify(corpo), status


def campos_obrigatorios(dados, campos):
    return [campo for campo in campos if not str(dados.get(campo, "")).strip()]


def criar_especificacao_swagger():
    return {
        "swagger": "2.0",
        "info": {
            "title": "Farol em Dia API",
            "description": "API para clientes, veículos e ordens de serviço de uma oficina especializada em faróis.",
            "version": "1.0.0",
        },
        "basePath": "/api",
        "schemes": ["http"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "definitions": {
            "ClienteEntrada": {
                "type": "object",
                "required": ["nome", "telefone"],
                "properties": {
                    "nome": {"type": "string", "example": "Marcos Lima"},
                    "telefone": {"type": "string", "example": "(85) 98822-4106"},
                    "email": {"type": "string", "example": "marcos@email.com"},
                },
            },
            "VeiculoEntrada": {
                "type": "object",
                "required": ["cliente_id", "marca", "modelo", "placa"],
                "properties": {
                    "cliente_id": {"type": "integer", "example": 1},
                    "marca": {"type": "string", "example": "Toyota"},
                    "modelo": {"type": "string", "example": "Corolla"},
                    "ano": {"type": "integer", "example": 2020},
                    "placa": {"type": "string", "example": "OXY-4J21"},
                    "cor": {"type": "string", "example": "Prata"},
                },
            },
            "OrdemEntrada": {
                "type": "object",
                "required": ["veiculo_id", "farol", "servico"],
                "properties": {
                    "veiculo_id": {"type": "integer", "example": 1},
                    "farol": {"type": "string", "example": "Dianteiro direito"},
                    "servico": {"type": "string", "example": "Polimento técnico"},
                    "defeito": {"type": "string", "example": "Farol opaco e com pouca iluminação"},
                    "previsao": {"type": "string", "example": "2026-08-21T14:00"},
                    "valor": {"type": "number", "format": "float", "example": 180.0},
                },
            },
            "StatusEntrada": {
                "type": "object",
                "required": ["status"],
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": sorted(STATUS_VALIDOS),
                        "example": "em_servico",
                    }
                },
            },
            "Erro": {
                "type": "object",
                "properties": {"erro": {"type": "string"}},
            },
        },
        "paths": {
            "/saude": {
                "get": {
                    "summary": "Verifica se a API está disponível",
                    "responses": {"200": {"description": "API disponível"}},
                }
            },
            "/dashboard": {
                "get": {
                    "summary": "Retorna os totais e as ordens recentes",
                    "responses": {"200": {"description": "Resumo da oficina"}},
                }
            },
            "/clientes": {
                "get": {
                    "summary": "Lista os clientes",
                    "parameters": [{"name": "q", "in": "query", "type": "string", "required": False}],
                    "responses": {"200": {"description": "Lista de clientes"}},
                },
                "post": {
                    "summary": "Cadastra um cliente",
                    "parameters": [{"name": "cliente", "in": "body", "required": True, "schema": {"$ref": "#/definitions/ClienteEntrada"}}],
                    "responses": {
                        "201": {"description": "Cliente criado"},
                        "400": {"description": "Dados inválidos", "schema": {"$ref": "#/definitions/Erro"}},
                    },
                },
            },
            "/clientes/{cliente_id}": {
                "delete": {
                    "summary": "Exclui um cliente sem registros vinculados",
                    "parameters": [{"name": "cliente_id", "in": "path", "required": True, "type": "integer"}],
                    "responses": {
                        "204": {"description": "Cliente excluído"},
                        "404": {"description": "Cliente não encontrado"},
                        "409": {"description": "Cliente possui registros vinculados"},
                    },
                }
            },
            "/veiculos": {
                "get": {
                    "summary": "Lista veículos com seus proprietários",
                    "responses": {"200": {"description": "Lista de veículos"}},
                },
                "post": {
                    "summary": "Cadastra um veículo",
                    "parameters": [{"name": "veiculo", "in": "body", "required": True, "schema": {"$ref": "#/definitions/VeiculoEntrada"}}],
                    "responses": {
                        "201": {"description": "Veículo criado"},
                        "400": {"description": "Dados inválidos"},
                        "409": {"description": "Placa já cadastrada"},
                    },
                },
            },
            "/veiculos/{veiculo_id}": {
                "delete": {
                    "summary": "Exclui um veículo sem ordens vinculadas",
                    "parameters": [{"name": "veiculo_id", "in": "path", "required": True, "type": "integer"}],
                    "responses": {
                        "204": {"description": "Veículo excluído"},
                        "404": {"description": "Veículo não encontrado"},
                        "409": {"description": "Veículo possui ordens vinculadas"},
                    },
                }
            },
            "/ordens": {
                "get": {
                    "summary": "Lista ordens de serviço",
                    "parameters": [{"name": "status", "in": "query", "type": "string", "required": False}],
                    "responses": {"200": {"description": "Lista de ordens"}},
                },
                "post": {
                    "summary": "Cria uma ordem de serviço",
                    "parameters": [{"name": "ordem", "in": "body", "required": True, "schema": {"$ref": "#/definitions/OrdemEntrada"}}],
                    "responses": {
                        "201": {"description": "Ordem criada"},
                        "400": {"description": "Dados inválidos"},
                        "404": {"description": "Veículo não encontrado"},
                    },
                },
            },
            "/ordens/{ordem_id}": {
                "patch": {
                    "summary": "Altera o status de uma ordem",
                    "parameters": [
                        {"name": "ordem_id", "in": "path", "required": True, "type": "integer"},
                        {"name": "status", "in": "body", "required": True, "schema": {"$ref": "#/definitions/StatusEntrada"}},
                    ],
                    "responses": {
                        "200": {"description": "Ordem atualizada"},
                        "400": {"description": "Status inválido"},
                        "404": {"description": "Ordem não encontrada"},
                    },
                },
                "delete": {
                    "summary": "Exclui uma ordem de serviço",
                    "parameters": [{"name": "ordem_id", "in": "path", "required": True, "type": "integer"}],
                    "responses": {
                        "204": {"description": "Ordem excluída"},
                        "404": {"description": "Ordem não encontrada"},
                    },
                },
            },
        },
    }


def create_app(configuracao_teste=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.environ.get("DATABASE_PATH", os.path.join(app.instance_path, "farol_em_dia.db")),
        JSON_SORT_KEYS=False,
        SEED_DATA=True,
    )
    if configuracao_teste:
        app.config.update(configuracao_teste)

    os.makedirs(app.instance_path, exist_ok=True)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    Swagger(
        app,
        template=criar_especificacao_swagger(),
        config={
            "headers": [],
            "specs": [{"endpoint": "apispec", "route": "/apispec.json", "rule_filter": lambda _regra: True, "model_filter": lambda _tag: True}],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/apidocs/",
        },
    )

    @app.before_request
    def disponibilizar_configuracao():
        g.app_config = app.config

    app.teardown_appcontext(fechar_db)

    with app.app_context():
        g.app_config = app.config
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as arquivo_schema:
            db.executescript(arquivo_schema.read())
        if app.config["SEED_DATA"] and db.execute("SELECT COUNT(*) AS total FROM clientes").fetchone()["total"] == 0:
            with app.open_resource("seed.sql", mode="r") as arquivo_seed:
                db.executescript(arquivo_seed.read())
        db.commit()

    @app.get("/")
    def inicio():
        return jsonify(
            {
                "servico": "Farol em Dia API",
                "status": "online",
                "saude": "/api/saude",
                "documentacao": "/apidocs/",
            }
        )

    @app.get("/api/saude")
    def saude():
        return jsonify({"status": "online", "servico": "Farol em Dia API", "horario": agora_iso()})

    @app.get("/api/dashboard")
    def dashboard():
        db = get_db()
        contagens = {status: 0 for status in STATUS_VALIDOS}
        for linha in db.execute("SELECT status, COUNT(*) AS total FROM ordens_servico GROUP BY status").fetchall():
            contagens[linha["status"]] = linha["total"]
        recentes = db.execute(
            """
            SELECT o.id, o.status, o.servico, o.farol, o.previsao, o.criado_em,
                   c.nome AS cliente_nome, v.marca, v.modelo, v.placa
            FROM ordens_servico o
            JOIN veiculos v ON v.id = o.veiculo_id
            JOIN clientes c ON c.id = v.cliente_id
            ORDER BY o.id DESC
            LIMIT 5
            """
        ).fetchall()
        return jsonify(
            {
                "contagens": contagens,
                "total_clientes": db.execute("SELECT COUNT(*) AS total FROM clientes").fetchone()["total"],
                "total_veiculos": db.execute("SELECT COUNT(*) AS total FROM veiculos").fetchone()["total"],
                "ordens_recentes": [linha_para_dict(item) for item in recentes],
            }
        )

    @app.route("/api/clientes", methods=["GET", "POST"])
    def clientes():
        db = get_db()
        if request.method == "GET":
            termo = request.args.get("q", "").strip()
            parametro = f"%{termo}%"
            linhas = db.execute(
                """
                SELECT c.*,
                       COUNT(DISTINCT v.id) AS total_veiculos,
                       COUNT(DISTINCT o.id) AS total_ordens
                FROM clientes c
                LEFT JOIN veiculos v ON v.cliente_id = c.id
                LEFT JOIN ordens_servico o ON o.veiculo_id = v.id
                WHERE c.nome LIKE ? OR c.telefone LIKE ? OR COALESCE(c.email, '') LIKE ?
                GROUP BY c.id
                ORDER BY c.nome
                """,
                (parametro, parametro, parametro),
            ).fetchall()
            return jsonify([linha_para_dict(item) for item in linhas])

        dados = request.get_json(silent=True) or {}
        faltantes = campos_obrigatorios(dados, ["nome", "telefone"])
        if faltantes:
            return resposta_erro("Preencha os campos obrigatórios.", 400, faltantes)
        cursor = db.execute(
            "INSERT INTO clientes (nome, telefone, email, criado_em) VALUES (?, ?, ?, ?)",
            (dados["nome"].strip(), dados["telefone"].strip(), dados.get("email", "").strip() or None, agora_iso()),
        )
        db.commit()
        cliente = db.execute("SELECT * FROM clientes WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return jsonify(linha_para_dict(cliente)), 201

    @app.delete("/api/clientes/<int:cliente_id>")
    def excluir_cliente(cliente_id):
        db = get_db()
        if db.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,)).fetchone() is None:
            return resposta_erro("Cliente não encontrado.", 404)
        try:
            db.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return resposta_erro("Não é possível excluir um cliente com veículos cadastrados.", 409)
        return "", 204

    @app.route("/api/veiculos", methods=["GET", "POST"])
    def veiculos():
        db = get_db()
        if request.method == "GET":
            linhas = db.execute(
                """
                SELECT v.*, c.nome AS cliente_nome, COUNT(o.id) AS total_ordens
                FROM veiculos v
                JOIN clientes c ON c.id = v.cliente_id
                LEFT JOIN ordens_servico o ON o.veiculo_id = v.id
                GROUP BY v.id
                ORDER BY v.id DESC
                """
            ).fetchall()
            return jsonify([linha_para_dict(item) for item in linhas])

        dados = request.get_json(silent=True) or {}
        faltantes = campos_obrigatorios(dados, ["cliente_id", "marca", "modelo", "placa"])
        if faltantes:
            return resposta_erro("Preencha os campos obrigatórios.", 400, faltantes)
        if db.execute("SELECT id FROM clientes WHERE id = ?", (dados["cliente_id"],)).fetchone() is None:
            return resposta_erro("Cliente não encontrado.", 404)
        try:
            cursor = db.execute(
                """
                INSERT INTO veiculos (cliente_id, marca, modelo, ano, placa, cor, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dados["cliente_id"],
                    dados["marca"].strip(),
                    dados["modelo"].strip(),
                    dados.get("ano") or None,
                    dados["placa"].strip().upper(),
                    dados.get("cor", "").strip() or None,
                    agora_iso(),
                ),
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return resposta_erro("Já existe um veículo com essa placa.", 409)
        veiculo = db.execute("SELECT * FROM veiculos WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return jsonify(linha_para_dict(veiculo)), 201

    @app.delete("/api/veiculos/<int:veiculo_id>")
    def excluir_veiculo(veiculo_id):
        db = get_db()
        if db.execute("SELECT id FROM veiculos WHERE id = ?", (veiculo_id,)).fetchone() is None:
            return resposta_erro("Veículo não encontrado.", 404)
        try:
            db.execute("DELETE FROM veiculos WHERE id = ?", (veiculo_id,))
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return resposta_erro("Não é possível excluir um veículo com ordens de serviço.", 409)
        return "", 204

    @app.route("/api/ordens", methods=["GET", "POST"])
    def ordens():
        db = get_db()
        if request.method == "GET":
            status = request.args.get("status", "").strip()
            filtro = "WHERE o.status = ?" if status else ""
            parametros = (status,) if status else ()
            linhas = db.execute(
                f"""
                SELECT o.*, c.nome AS cliente_nome, c.telefone AS cliente_telefone,
                       v.marca, v.modelo, v.ano, v.placa, v.cor
                FROM ordens_servico o
                JOIN veiculos v ON v.id = o.veiculo_id
                JOIN clientes c ON c.id = v.cliente_id
                {filtro}
                ORDER BY o.id DESC
                """,
                parametros,
            ).fetchall()
            return jsonify([linha_para_dict(item) for item in linhas])

        dados = request.get_json(silent=True) or {}
        faltantes = campos_obrigatorios(dados, ["veiculo_id", "farol", "servico"])
        if faltantes:
            return resposta_erro("Preencha os campos obrigatórios.", 400, faltantes)
        if db.execute("SELECT id FROM veiculos WHERE id = ?", (dados["veiculo_id"],)).fetchone() is None:
            return resposta_erro("Veículo não encontrado.", 404)
        cursor = db.execute(
            """
            INSERT INTO ordens_servico
                (veiculo_id, farol, servico, defeito, previsao, valor, status, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, 'recebida', ?, ?)
            """,
            (
                dados["veiculo_id"],
                dados["farol"].strip(),
                dados["servico"].strip(),
                dados.get("defeito", "").strip() or None,
                dados.get("previsao") or None,
                dados.get("valor") or 0,
                agora_iso(),
                agora_iso(),
            ),
        )
        db.commit()
        ordem = db.execute("SELECT * FROM ordens_servico WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return jsonify(linha_para_dict(ordem)), 201

    @app.patch("/api/ordens/<int:ordem_id>")
    def atualizar_ordem(ordem_id):
        db = get_db()
        dados = request.get_json(silent=True) or {}
        status = dados.get("status", "").strip()
        if status not in STATUS_VALIDOS:
            return resposta_erro("Status inválido.", 400, sorted(STATUS_VALIDOS))
        if db.execute("SELECT id FROM ordens_servico WHERE id = ?", (ordem_id,)).fetchone() is None:
            return resposta_erro("Ordem não encontrada.", 404)
        db.execute(
            "UPDATE ordens_servico SET status = ?, atualizado_em = ? WHERE id = ?",
            (status, agora_iso(), ordem_id),
        )
        db.commit()
        ordem = db.execute("SELECT * FROM ordens_servico WHERE id = ?", (ordem_id,)).fetchone()
        return jsonify(linha_para_dict(ordem))

    @app.delete("/api/ordens/<int:ordem_id>")
    def excluir_ordem(ordem_id):
        db = get_db()
        cursor = db.execute("DELETE FROM ordens_servico WHERE id = ?", (ordem_id,))
        db.commit()
        if cursor.rowcount == 0:
            return resposta_erro("Ordem não encontrada.", 404)
        return "", 204

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
