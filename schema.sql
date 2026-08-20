CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL,
    email TEXT,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS veiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    ano INTEGER,
    placa TEXT NOT NULL UNIQUE,
    cor TEXT,
    criado_em TEXT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ordens_servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    veiculo_id INTEGER NOT NULL,
    farol TEXT NOT NULL,
    servico TEXT NOT NULL,
    defeito TEXT,
    previsao TEXT,
    valor REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'recebida'
        CHECK (status IN ('recebida', 'em_servico', 'aguardando_peca', 'pronta', 'entregue')),
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos (id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_veiculos_cliente ON veiculos (cliente_id);
CREATE INDEX IF NOT EXISTS idx_ordens_veiculo ON ordens_servico (veiculo_id);
CREATE INDEX IF NOT EXISTS idx_ordens_status ON ordens_servico (status);
