# Controle de Qualidade

Ferramenta de cadastro e análise de problemas de qualidade de produto.

- **Tela 1 — Recebimento no CD:** nota, fornecedor, transportadora e, por produto com problema: SKU, lote, situação da caixa, avaria, fotos, quantidades (UN/CX/PCT) e valor pago. Calcula o prejuízo estimado.
- **Tela 2 — Recebimento pelo Cliente:** busca o pedido na base de pedidos pelo **CPF** (lista os pedidos dos últimos 6 meses) ou pelo **número do pedido** (com sugestões enquanto digita). Ao clicar no pedido, abre uma janela com endereço, transportadora e itens; o atendente marca o que teve problema, informa a quantidade, a situação da caixa e o motivo, e salva. Lote e fornecedor vêm do próprio pedido.
- **Tela 3 — Análise:** KPIs, tendência semanal, mapa de calor do Brasil por estado de entrega, rankings (fornecedor, produto, avaria, situação da caixa, canal), produtos com mais de um fornecedor, lotes recorrentes e resumo por produto, com insights automáticos.

## Ver funcionando

Abra `index.html` (ou a página publicada no GitHub Pages deste repositório). Fora do ambiente de produção a página entra em **modo demonstração**:

- carrega 26 notas do CD, 70 reclamações de clientes e uma base de 116 pedidos **fictícios**, com nomes genéricos (Fornecedor A, Produto 1, SKU-001...);
- para testar a Tela 2, use o CPF `877.893.287-44` (4 pedidos), o CPF `100.200.300-50` (10 pedidos, um em cada canal: site, aplicativo, TikTok, Mercado Livre e Shopee) ou o pedido `PED-100240`;
- tudo que você cadastrar fica salvo **só no seu navegador** (localStorage) e nunca é enviado a lugar nenhum;
- o botão "Restaurar exemplos" no topo apaga o que foi cadastrado e recarrega os dados de exemplo.

## Arquivos

- `index.html` — a aplicação inteira (formulários, análise e mapa de calor).
- `local-runtime.js` — banco de dados e armazenamento de fotos locais, usados no modo demonstração.
- `dados-exemplo.js` — dados fictícios, gerados por `gerar_exemplos.py` (usa `pedidos_base.py` para a base de pedidos).

## Uso em produção

Em produção a ferramenta roda em um ambiente que forneça um banco de dados compartilhado (`db`) e o armazenamento de fotos (`assets`); nesse caso `local-runtime.js` não é necessário e a página usa o ambiente. Para hospedar em outro lugar com dados compartilhados entre pessoas, seria preciso trocar essa camada por um backend próprio (por exemplo Firebase ou Supabase).

## Modelo de dados (coleções do banco)

- `pedidos`: base de pedidos consultada na Tela 2 (`numero`, `numeroBusca`, `cpf`, `cliente`, `dataPedido`, `canal`, `transportadora`, `entrega{logradouro,numero,bairro,cidade,uf,cep}`, `itens[]` com `sku`, `produto`, `lote`, `fornecedor`, `qtd`, `precoUnit`). Os CPFs de exemplo são sintéticos e inválidos. Para integrar com uma API real, basta trocar as três funções de `PedidosAPI` (`porCpf`, `porNumero`, `sugerir`) no `index.html`.
- `config/listas`: listas dos menus (`fornecedores`, `skus`, `produtos`, `situacoesCaixa`, `tiposAvaria`, `canaisAtendimento`, `transportadoras`) e o vínculo `produtoSkuMap` (produto → SKUs).
- `cd_recebimento`: `numeroNota`, `dataCompra`, `dataChegada`, `fornecedor`, `transportadora`, `itens[]` (`sku`, `lote`, `situacaoCaixa`, `tipoAvaria`, `fotos[]`, `qtdComprada{valor,unidade,valorPago}`, `qtdProblema{valor,unidade}`, `unidadesEmbalagem`), `createdAt`.
- `cliente_recebimento`: `numeroPedido`, `dataReclamacao`, `canalAtendimento`, `transportadora`, `cidade`, `cep`, `uf`, `itens[]` (`produto`, `sku`, `lote`, `fornecedor`, `situacaoCaixa`, `tipoAvaria`, `fotos[]`, `qtdComprada{valor,unidade}`, `qtdProblema{valor,unidade}`), `createdAt`.

Os dados reais não estão neste repositório.
