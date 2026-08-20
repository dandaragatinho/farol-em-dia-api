import os
import tempfile
import unittest

from app import create_app


class FarolEmDiaApiTest(unittest.TestCase):
    def setUp(self):
        arquivo = tempfile.NamedTemporaryFile(delete=False)
        arquivo.close()
        self.caminho_db = arquivo.name
        self.app = create_app({"TESTING": True, "DATABASE": self.caminho_db, "SEED_DATA": False})
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.caminho_db)

    def test_fluxo_completo(self):
        saude = self.client.get("/api/saude")
        self.assertEqual(saude.status_code, 200)

        cliente = self.client.post(
            "/api/clientes",
            json={"nome": "João Teste", "telefone": "(85) 90000-0000", "email": "joao@teste.com"},
        )
        self.assertEqual(cliente.status_code, 201)
        cliente_id = cliente.get_json()["id"]

        veiculo = self.client.post(
            "/api/veiculos",
            json={"cliente_id": cliente_id, "marca": "Ford", "modelo": "Ka", "ano": 2020, "placa": "ABC-1D23", "cor": "Prata"},
        )
        self.assertEqual(veiculo.status_code, 201)
        veiculo_id = veiculo.get_json()["id"]

        ordem = self.client.post(
            "/api/ordens",
            json={"veiculo_id": veiculo_id, "farol": "Dianteiro esquerdo", "servico": "Vedação", "valor": 200},
        )
        self.assertEqual(ordem.status_code, 201)
        ordem_id = ordem.get_json()["id"]

        atualizada = self.client.patch(f"/api/ordens/{ordem_id}", json={"status": "em_servico"})
        self.assertEqual(atualizada.status_code, 200)
        self.assertEqual(atualizada.get_json()["status"], "em_servico")

        dashboard = self.client.get("/api/dashboard")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.get_json()["contagens"]["em_servico"], 1)

        self.assertEqual(self.client.delete(f"/api/ordens/{ordem_id}").status_code, 204)
        self.assertEqual(self.client.delete(f"/api/veiculos/{veiculo_id}").status_code, 204)
        self.assertEqual(self.client.delete(f"/api/clientes/{cliente_id}").status_code, 204)

    def test_rejeita_dados_invalidos(self):
        self.assertEqual(self.client.post("/api/clientes", json={"nome": "Sem telefone"}).status_code, 400)
        self.assertEqual(self.client.patch("/api/ordens/999", json={"status": "inexistente"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
