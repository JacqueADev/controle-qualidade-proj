"""Gera uma base fictícia de pedidos (clientes, endereços, itens) para o modo demonstração.

CPFs são sintéticos e propositalmente inválidos (dígitos verificadores errados), para nunca coincidirem com um CPF real.
"""
import datetime
import random

CIDADES = {
    'SP': ('São Paulo', (1000, 5999)), 'RJ': ('Rio de Janeiro', (20000, 23999)), 'MG': ('Belo Horizonte', (30000, 31999)),
    'PR': ('Curitiba', (80000, 82999)), 'RS': ('Porto Alegre', (90000, 91999)), 'BA': ('Salvador', (40000, 42999)),
    'PE': ('Recife', (50000, 52999)), 'CE': ('Fortaleza', (60000, 61999)), 'GO': ('Goiânia', (74000, 74999)),
    'SC': ('Florianópolis', (88000, 88999)), 'DF': ('Brasília', (70000, 71999)), 'PA': ('Belém', (66000, 66999)),
    'AM': ('Manaus', (69000, 69099)), 'ES': ('Vitória', (29000, 29099)), 'MA': ('São Luís', (65000, 65099)),
    'MT': ('Cuiabá', (78000, 78099)), 'PB': ('João Pessoa', (58000, 58099)), 'RN': ('Natal', (59000, 59099)),
}
PESO_UF = {'SP': 22, 'RJ': 10, 'MG': 9, 'PR': 6, 'RS': 6, 'BA': 6, 'PE': 4, 'CE': 4, 'GO': 4, 'SC': 4, 'DF': 3, 'PA': 3,
           'AM': 2, 'ES': 3, 'MA': 2, 'MT': 2, 'PB': 2, 'RN': 2}
RUAS = ['Rua das Acácias', 'Avenida Central', 'Rua do Comércio', 'Rua das Palmeiras', 'Avenida Brasil', 'Rua Sete de Setembro',
        'Rua XV de Novembro', 'Rua das Flores', 'Avenida Paulista', 'Rua do Sol']
BAIRROS = ['Centro', 'Jardim América', 'Vila Nova', 'Boa Vista', 'São José', 'Industrial', 'Santa Maria', 'Parque das Águas']


def _cpf_invalido(rng):
    n = [rng.randint(0, 9) for _ in range(9)]
    d1 = (sum(v * (10 - i) for i, v in enumerate(n)) * 10 % 11) % 10
    d2 = (sum(v * (11 - i) for i, v in enumerate(n + [d1])) * 10 % 11) % 10
    d2 = (d2 + 1) % 10  # força dígito verificador inválido
    return ''.join(map(str, n + [d1, d2]))


def gerar(rng, produtos, transportadoras, canais, hoje=None, n_clientes=45, numero_inicial=100231):
    """produtos: lista de dicts {produto, sku, preco, fornecedores}. Retorna (docs, amostras)."""
    hoje = hoje or datetime.date.today()
    docs, amostras = {}, []
    numero = numero_inicial
    ufs, pesos = list(PESO_UF), list(PESO_UF.values())
    for c in range(1, n_clientes + 1):
        uf = rng.choices(ufs, pesos)[0]
        cidade, (lo, hi) = CIDADES[uf]
        cpf = _cpf_invalido(rng)
        cep = '%05d%03d' % (rng.randint(lo, hi), rng.randint(0, 999))
        entrega = {'logradouro': rng.choice(RUAS), 'numero': str(rng.randint(10, 2400)), 'bairro': rng.choice(BAIRROS),
                   'cidade': cidade, 'uf': uf, 'cep': cep}
        recentes = 0
        for _ in range(rng.choice([1, 1, 2, 2, 3, 4, 5])):
            dias = int(rng.random() * 230)
            data = hoje - datetime.timedelta(days=dias)
            itens = []
            for p in rng.sample(produtos, rng.randint(1, min(4, len(produtos)))):
                itens.append({'sku': p['sku'], 'produto': p['produto'], 'lote': 'L%02d-%03d' % (rng.randint(1, 9), rng.choice([11, 12, 21, 22, 31, 40])),
                              'fornecedor': rng.choice(p['fornecedores']), 'qtd': rng.choice([1, 1, 1, 2, 2, 3]),
                              'precoUnit': round(p['preco'] * rng.uniform(0.95, 1.1), 2)})
            numero += rng.randint(1, 9)
            num = 'PED-%06d' % numero
            docs[num] = {'numero': num, 'numeroBusca': '%06d' % numero, 'cpf': cpf, 'cliente': 'Cliente Exemplo %02d' % c,
                         'dataPedido': data.isoformat(), 'canal': rng.choices(canais, [30, 25, 20, 10, 10, 5][:len(canais)])[0],
                         'transportadora': rng.choice(transportadoras), 'entrega': entrega, 'itens': itens}
            if dias <= 183:
                recentes += 1
        if recentes >= 2 and len(amostras) < 3:
            amostras.append(cpf)
    return docs, amostras
