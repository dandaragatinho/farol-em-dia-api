INSERT INTO clientes (nome, telefone, email, criado_em) VALUES
    ('Marcos Lima', '(85) 98822-4106', 'marcos.lima@email.com', '2026-08-18T08:00:00-03:00'),
    ('Ana Souza', '(85) 99910-3385', 'ana.souza@email.com', '2026-08-18T09:00:00-03:00'),
    ('Lucas Reis', '(85) 98774-2219', NULL, '2026-08-19T10:00:00-03:00'),
    ('Carla Mendes', '(85) 99672-8031', 'carla.mendes@email.com', '2026-08-19T14:00:00-03:00');

INSERT INTO veiculos (cliente_id, marca, modelo, ano, placa, cor, criado_em) VALUES
    (1, 'Toyota', 'Corolla', 2020, 'OXY-4J21', 'Prata', '2026-08-18T08:05:00-03:00'),
    (2, 'Chevrolet', 'Onix', 2019, 'PNK-8A12', 'Branco', '2026-08-18T09:05:00-03:00'),
    (3, 'Hyundai', 'HB20', 2021, 'QYZ-2D45', 'Cinza', '2026-08-19T10:05:00-03:00'),
    (4, 'Honda', 'Civic', 2018, 'POE-7F09', 'Preto', '2026-08-19T14:05:00-03:00');

INSERT INTO ordens_servico
    (veiculo_id, farol, servico, defeito, previsao, valor, status, criado_em, atualizado_em)
VALUES
    (1, 'Dianteiro direito', 'Polimento técnico', 'Lente opaca e iluminação fraca', '2026-08-20T14:00', 180.00, 'em_servico', '2026-08-20T08:15:00-03:00', '2026-08-20T09:20:00-03:00'),
    (2, 'Par dianteiro', 'Troca de lente', 'Lentes trincadas', '2026-08-21T17:00', 650.00, 'aguardando_peca', '2026-08-19T15:00:00-03:00', '2026-08-20T08:30:00-03:00'),
    (3, 'Dianteiro esquerdo', 'Vedação e limpeza', 'Entrada de água após chuva', '2026-08-20T11:30', 240.00, 'pronta', '2026-08-19T16:00:00-03:00', '2026-08-20T10:45:00-03:00'),
    (4, 'Par dianteiro', 'Recuperação de LED', 'DRL intermitente', '2026-08-22T16:00', 520.00, 'recebida', '2026-08-20T10:10:00-03:00', '2026-08-20T10:10:00-03:00');
