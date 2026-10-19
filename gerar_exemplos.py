"""Gera dados-exemplo.js com registros fictícios (nomes genéricos) para o modo demonstração."""
import datetime
import json
import os
import random

import pedidos_base

random.seed(7)
HERE = os.path.dirname(os.path.abspath(__file__))

FORNECEDORES = ['Fornecedor A', 'Fornecedor B', 'Fornecedor C', 'Fornecedor D', 'Fornecedor E', 'Fornecedor F']
PRODUTOS = ['Produto 1', 'Produto 2', 'Produto 3', 'Produto 4', 'Produto 5', 'Produto 6', 'Produto 7']
SKUS = ['SKU-%03d' % i for i in range(1, 12)]
SKU_MAP = {PRODUTOS[i]: [SKUS[i]] for i in range(7)}
TRANSPORTADORAS = ['Loggi', 'J&T', 'SPI', 'Imile', 'Correios']
CANAIS = ['TikTok', 'Instagram', 'Shopee', 'Mercado Livre', 'SAC - Interno', 'Live - APP', 'Site', 'Aplicativo']
SIT = ['Caixa íntegra', 'Caixa amassada', 'Caixa molhada/úmida', 'Caixa violada/aberta', 'Caixa rasgada', 'Sem caixa (a granel)']
AVA = ['Produto vencido', 'Produto quebrado/danificado', 'Vazamento', 'Embalagem violada', 'Divergência de lote', 'Produto incorreto',
       'Falta de itens', 'Produto amassado', 'Mofo/contaminação']

UF_RANGES = {
    'SP': [(1000, 5999), (13000, 19999)], 'RJ': [(20000, 28999)], 'MG': [(30000, 39999)], 'PR': [(80000, 87999)], 'RS': [(90000, 99999)],
    'BA': [(40000, 48999)], 'PE': [(50000, 56999)], 'CE': [(60000, 63999)], 'GO': [(73700, 76799)], 'SC': [(88000, 89999)],
    'DF': [(70000, 72799)], 'PA': [(66000, 68899)], 'AM': [(69000, 69299)], 'ES': [(29000, 29999)], 'MA': [(65000, 65999)],
    'MT': [(78000, 78899)], 'PB': [(58000, 58999)], 'RN': [(59000, 59999)], 'AL': [(57000, 57999)], 'SE': [(49000, 49999)],
    'PI': [(64000, 64999)], 'MS': [(79000, 79999)], 'TO': [(77000, 77999)], 'RO': [(76800, 76999)]}
UF_W = {'SP': 22, 'RJ': 10, 'MG': 9, 'PR': 6, 'RS': 6, 'BA': 6, 'PE': 4, 'CE': 4, 'GO': 4, 'SC': 4, 'DF': 3, 'PA': 3, 'AM': 2, 'ES': 3,
        'MA': 2, 'MT': 2, 'PB': 2, 'RN': 2, 'AL': 1, 'SE': 1, 'PI': 1, 'MS': 1, 'TO': 1, 'RO': 1}
NNE = {'PA', 'AM', 'MA', 'CE', 'PE', 'BA', 'PB', 'RN', 'AL', 'SE', 'PI', 'RO', 'TO'}
PROD_W = [24, 16, 12, 14, 6, 14, 14]


def today_offset(days):
    return datetime.date.today() - datetime.timedelta(days=days)


def iso(d):
    return datetime.datetime(d.year, d.month, d.day, random.randint(8, 18), random.randint(0, 59)).strftime('%Y-%m-%dT%H:%M:%S.000Z')


def rand_date(max_days_ago):
    return today_offset(int(max_days_ago * (random.random() ** 1.4)))


def lote():
    return 'L%02d-%03d' % (random.randint(1, 9), random.choice([11, 12, 21, 22, 31, 40]))


def cep(uf):
    lo, hi = random.choice(UF_RANGES[uf])
    return '%05d%03d' % (random.randint(lo, hi), random.randint(0, 999))


def cl_item(uf):
    if uf in NNE:
        sit = random.choices(SIT, [15, 30, 25, 12, 10, 8])[0]
        ava = random.choices(AVA, [4, 22, 14, 10, 5, 3, 6, 20, 16])[0]
    else:
        sit = random.choices(SIT, [30, 22, 8, 15, 12, 13])[0]
        ava = random.choices(AVA, [10, 18, 12, 14, 8, 6, 14, 10, 8])[0]
    comprada = random.choice([1, 1, 1, 2, 2, 3])
    return {'produto': random.choices(PRODUTOS, PROD_W)[0], 'lote': lote(), 'situacaoCaixa': sit, 'tipoAvaria': ava, 'fotos': [],
            'qtdComprada': {'valor': comprada, 'unidade': 'UN'}, 'qtdProblema': {'valor': random.randint(1, comprada), 'unidade': 'UN'}}


def cd_item():
    kind = random.choices(['UN', 'CX', 'PCT', 'CXCX', 'PCTPCT'], [35, 25, 15, 15, 10])[0]
    price = round(random.uniform(4, 22), 2)
    fator = None
    if kind == 'UN':
        q = random.choice([30, 40, 50, 60, 80, 100, 120])
        total, comprada, pu = q, {'valor': q, 'unidade': 'UN'}, 'UN'
        prob = random.randint(1, max(2, q // 10))
    else:
        cu = 'CX' if kind in ('CX', 'CXCX') else 'PCT'
        fator = random.choice([24, 48, 100, 200]) if cu == 'CX' else random.choice([10, 20, 50])
        q = random.randint(2, 10) if cu == 'CX' else random.randint(5, 20)
        total, comprada = q * fator, {'valor': q, 'unidade': cu}
        if kind in ('CXCX', 'PCTPCT'):
            pu, prob = cu, random.randint(1, max(1, q // 4))
        else:
            pu, prob = 'UN', random.randint(1, max(2, total // 20))
    comprada['valorPago'] = round(price * total, 2)
    return {'sku': random.choice(SKUS), 'lote': lote(), 'situacaoCaixa': random.choices(SIT, [20, 28, 12, 15, 15, 10])[0],
            'tipoAvaria': random.choices(AVA, [8, 18, 10, 14, 10, 6, 12, 14, 8])[0], 'fotos': [], 'qtdComprada': comprada,
            'qtdProblema': {'valor': prob, 'unidade': pu}, 'unidadesEmbalagem': fator}


cliente, cd = {}, {}
for i in range(70):
    uf = random.choices(list(UF_W), list(UF_W.values()))[0]
    d = rand_date(60)
    itens = [cl_item(uf)] + ([cl_item(uf)] if random.random() < 0.15 else [])
    cliente['demo_cl_%d' % (i + 1)] = {
        'numeroPedido': 'PED-%04d' % (1001 + i), 'dataReclamacao': d.isoformat(), 'canalAtendimento': random.choices(CANAIS[:6], [25, 10, 30, 20, 10, 5])[0],
        'fornecedor': random.choice(FORNECEDORES), 'transportadora': random.choice(TRANSPORTADORAS), 'cep': cep(uf), 'uf': uf,
        'itens': itens, 'createdAt': iso(d)}
for i in range(26):
    d = rand_date(60)
    itens = [cd_item()] + ([cd_item()] if random.random() < 0.3 else [])
    cd['demo_cd_%d' % (i + 1)] = {
        'numeroNota': 'NF-%04d' % (101 + i), 'dataCompra': (d - datetime.timedelta(days=random.randint(3, 7))).isoformat(),
        'dataChegada': d.isoformat(), 'fornecedor': random.choice(FORNECEDORES), 'transportadora': random.choice(TRANSPORTADORAS),
        'itens': itens, 'createdAt': iso(d)}

catalogo = [{'produto': PRODUTOS[i], 'sku': SKUS[i], 'preco': [89.9, 64.9, 119.9, 79.9, 54.9, 99.9, 72.9][i],
             'fornecedores': FORNECEDORES[i % 6::3][:2] or [FORNECEDORES[i % 6]]} for i in range(7)]
pedidos, amostras = pedidos_base.gerar(random.Random(11), catalogo, TRANSPORTADORAS, CANAIS[:6])
CANAIS_PEDIDO = ['Site', 'Aplicativo', 'TikTok', 'Mercado Livre', 'Shopee']
pedidos.update(pedidos_base.gerar_cliente(random.Random(21), '10020030050', 'Cliente Exemplo 31', CANAIS_PEDIDO * 2, catalogo,
                                          TRANSPORTADORAS, max(int(x['numeroBusca']) for x in pedidos.values()) + 10))

seed = {
    'config': {'listas': {
        'fornecedores': FORNECEDORES, 'skus': SKUS, 'produtos': PRODUTOS, 'produtoSkuMap': SKU_MAP,
        'situacoesCaixa': SIT, 'tiposAvaria': AVA, 'canaisAtendimento': CANAIS, 'transportadoras': TRANSPORTADORAS}},
    'cd_recebimento': cd, 'cliente_recebimento': cliente, 'pedidos': pedidos}

with open(os.path.join(HERE, 'dados-exemplo.js'), 'w', encoding='utf-8') as fh:
    fh.write('// Dados fictícios para o modo demonstração (nomes genéricos).\n')
    fh.write('window.QC_SEED = ' + json.dumps(seed, ensure_ascii=False) + ';\n')
print(len(cd), 'notas CD;', len(cliente), 'reclamações;', len(pedidos), 'pedidos; CPFs de teste:', amostras)
