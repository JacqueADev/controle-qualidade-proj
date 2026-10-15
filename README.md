# Controle de Qualidade

Ferramenta de cadastro e análise de problemas de qualidade de produto, em um único arquivo: `controle-qualidade.html`.

- **Tela 1 — Recebimento no CD:** nota, fornecedor, transportadora e, por produto com problema: SKU, lote, situação da caixa, avaria, fotos, quantidades (UN/CX/PCT) e valor pago. Calcula o prejuízo estimado.
- **Tela 2 — Recebimento pelo Cliente:** pedido, canal, CEP, fornecedor, transportadora e, por produto com problema: nome, lote, situação da caixa, avaria, fotos e quantidades.
- **Tela 3 — Análise:** KPIs, tendência semanal, mapa de calor por estado (a partir do CEP), rankings (fornecedor, produto, avaria, situação da caixa, canal), produtos com mais de um fornecedor, lotes recorrentes e resumo por produto, com insights automáticos.

## Importante: onde ele funciona de verdade

O arquivo foi feito para rodar em um ambiente que forneça um banco de dados compartilhado (`db`) e o armazenamento de fotos (`assets`). Esse ambiente é onde a ferramenta está em uso hoje.

Aberto fora desse ambiente (duplo clique, GitHub Pages etc.) ele carrega e os formulários aparecem, mas **nada é salvo** e a análise fica vazia — a página mostra um aviso no topo. Este repositório serve como versionamento do código-fonte.

Para hospedar em outro lugar seria preciso trocar a camada de dados por um backend próprio (por exemplo Firebase ou Supabase).

## Modelo de dados (coleções do banco)

- `config/listas`: listas dos menus (`fornecedores`, `skus`, `produtos`, `situacoesCaixa`, `tiposAvaria`, `canaisAtendimento`, `transportadoras`) e o vínculo `produtoSkuMap` (produto → SKUs).
- `cd_recebimento`: `numeroNota`, `dataCompra`, `dataChegada`, `fornecedor`, `transportadora`, `itens[]` (`sku`, `lote`, `situacaoCaixa`, `tipoAvaria`, `fotos[]`, `qtdComprada{valor,unidade,valorPago}`, `qtdProblema{valor,unidade}`, `unidadesEmbalagem`), `createdAt`.
- `cliente_recebimento`: `numeroPedido`, `dataReclamacao`, `canalAtendimento`, `fornecedor`, `transportadora`, `cep`, `uf`, `itens[]` (`produto`, `lote`, `situacaoCaixa`, `tipoAvaria`, `fotos[]`, `qtdComprada{valor,unidade}`, `qtdProblema{valor,unidade}`), `createdAt`.

Os dados em si não estão neste repositório.

## Como atualizar a versão em uso

Publicar o conteúdo de `controle-qualidade.html` no mesmo ambiente, mantendo o acesso ao banco (`db`) e ao armazenamento de fotos (`assets`).
