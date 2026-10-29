---
name: granatum-financeiro
description: >
  Use this skill whenever the user asks about Granatum or the company's
  financial data, including cash flow, DRE, monthly summaries, pending bills,
  entries, statements, balances, configuration, or creating, correcting,
  deleting and paying entries, including series, split entries, transfers
  and attachments, and reconciling the bank statement.
  Apply the shared Granatum rules first, then load the reference that matches
  the requested operation.
metadata:
  version: "1.3.0"
---

# Granatum Financeiro

This skill consolidates the Granatum Financeiro workflows originally maintained
as separate Claude plugin skills. Use the shared rules for every Granatum
conversation. For a specific request, read only the matching reference below.

- Shared rules and guardrails: [granatum-fundamentos.md](references/granatum-fundamentos.md)
- Initial connection and company selection: [granatum-config.md](references/granatum-config.md)
- Cash-flow report: [fluxo-caixa.md](references/fluxo-caixa.md)
- Income statement (DRE): [dre.md](references/dre.md)
- Monthly financial overview: [resumo-mes.md](references/resumo-mes.md)
- Open payables and receivables: [pendencias.md](references/pendencias.md)
- Entry search and statement: [extrato.md](references/extrato.md)
- Creating a financial entry: [novo-lancamento.md](references/novo-lancamento.md), plus [regras-de-campo.md](references/regras-de-campo.md)
- Advanced writes (editing or deleting existing entries, series and changing a series' number of installments, batch edits, tags, split entries, transfers and recurring transfers, installments and recurrence, creating a person): [escrita-avancada.md](references/escrita-avancada.md)
- Bank reconciliation (pending statement movements, reconciling, undoing a reconciliation): [conciliacao.md](references/conciliacao.md)
- Payment (settling, partial payment, changing or reversing a payment, including transfers and mixed requests in one call) and attachments: [pagamento-e-anexos.md](references/pagamento-e-anexos.md)

Preserve the confirmation and safety requirements in the shared rules before
performing any write operation. Read [escrita-avancada.md](references/escrita-avancada.md)
before changing or deleting an existing entry, or before any write that reaches
more than one entry. If the target environment exposes Granatum
tools through a connector, use those tools; otherwise explain that the
connection is unavailable instead of fabricating data or a successful result.
