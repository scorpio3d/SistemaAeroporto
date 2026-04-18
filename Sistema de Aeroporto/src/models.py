class Voo:
    def __init__(self, numero, origem, destino, capacidade=30, estado="Programado", passageiros=None):
        self.numero = numero.upper().strip()
        self.origem = origem.strip()
        self.destino = destino.strip()
        self.capacidade = capacidade
        self.estado = estado
        self.passageiros = passageiros if passageiros else []

    def to_dict(self):
        return {
            "numero_voo": self.numero,
            "origem": self.origem,
            "destino": self.destino,
            "capacidade": self.capacidade,
            "estado": self.estado,
            "passageiros": self.passageiros
        }

def verificar_duplicado(num, lista_voos):
    return any(v["numero_voo"] == num.upper().strip() for v in lista_voos)