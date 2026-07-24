# Produção, Segurança e Escalabilidade

## Objetivo

A G14 fornece os contratos necessários para operar o UltraStats AI de forma
contínua, segura, observável e recuperável. As primitives são independentes de
cloud e podem receber adapters específicos sem acoplar o domínio.

## Segurança

### Identidade e acesso

- tokens assinados com HMAC-SHA256, emissor e expiração;
- senhas derivadas com PBKDF2-SHA256, salt e custo mínimo;
- autorização por interseção de papéis (RBAC);
- credenciais somente por referências de ambiente;
- redação de segredos em mensagens e logs.

### API

O `APIRequestGuard` aplica:

- HTTPS obrigatório;
- limite de corpo;
- content types explícitos;
- allowlist de origens;
- rate limiting por janela deslizante.

Validação de assinatura ocorre antes do parsing do token. Tokens expirados,
claims inválidos e emissores desconhecidos são rejeitados.

## Resiliência e escala

- circuit breaker com limiar e timeout de recuperação;
- cache TTL com capacidade limitada e evicção;
- fila idempotente com ack, nack, retries e dead-letter;
- fila SQL persistente para jobs operacionais;
- cálculo de réplicas com mínimo e máximo;
- harness de carga com volume, falhas e latência;
- revisão de dependências bloqueadas e versões mínimas.

## Observabilidade

O registro em memória suporta counters, gauges e histogramas. Métricas
persistentes possuem labels e instante. Limiares geram alertas operacionais
ordenados; alertas persistentes mantêm severidade, mensagem e estado.

O painel `18_Operacoes_de_Producao.py` apresenta métricas e alertas, além da
postura dos controles implantados.

## Backup, recuperação e auditoria

Backups usam JSON canônico e checksum SHA-256. A recuperação só ocorre após a
verificação do checksum e exige um objeto válido. O catálogo persistente guarda
localização, tamanho, status e instante de verificação.

Eventos de segurança formam uma cadeia hash: sequência, ação, ator, instante e
hash anterior integram cada digest. Alteração ou remoção intermediária invalida
a verificação.

Políticas de retenção são explícitas por categoria e rejeitam períodos
inválidos ou categorias sem contrato.

## Persistência

A migration reversível `a7e23594a440` cria:

- `operational_metrics`;
- `operational_alerts`;
- `security_audit`;
- `backup_catalog`;
- `operational_queue`.

## Garantias

A G14 foi concluída com 2.585 testes e 100% de cobertura de linhas e branches.
Os cenários incluem autenticação, RBAC, proteção de segredo, API security,
cache, fila, dead-letter, circuit breaker, backup/restore, auditoria,
observabilidade, alertas, retenção, autoscaling, carga, dependências,
persistência e reversão da migration.
