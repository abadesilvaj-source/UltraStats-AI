# Release Candidate e Validação Integrada

## Gate

O release gate recebe um manifesto imutável e evidências da execução. Uma
candidata só é aprovada quando todos os critérios passam:

1. checksum do manifesto;
2. quantidade mínima de testes;
3. 100% de cobertura;
4. zero linhas ausentes;
5. zero branches parciais;
6. exatamente um migration head esperado;
7. dependências íntegras;
8. smoke test;
9. E2E;
10. backup/restore;
11. taxa de falha de carga dentro do limite;
12. worktree controlado.

O manifesto usa versão semântica `x.y.z-rc.n`, commit, migration head,
componentes ordenados, instante e SHA-256.

## CI

`.github/workflows/release-candidate.yml` inicia PostgreSQL 17 e executa:

- instalação reproduzível;
- `pip check`;
- migrations até o head;
- suíte completa;
- smoke test;
- build da imagem Docker.

O workflow roda em pull requests, na branch da G15 e em tags de RC.

## Staging

`docker-compose.staging.yml` separa banco, migrations, scheduler, API e
frontend. Credenciais são obrigatórias e vêm do arquivo de ambiente local; os
containers usam health checks e somente os diretórios estritamente necessários
são graváveis. Migrations precisam terminar antes dos serviços.

## Integração E2E

O teste de release:

- calcula snapshot estatístico;
- registra e executa modelo preditivo;
- avalia e persiste recomendação;
- dimensiona e persiste portfólio;
- salva perfil e notificação;
- processa evento ao vivo e efeitos push;
- registra métrica, auditoria, backup e job operacional.

Outro teste aplica toda a cadeia Alembic em um banco vazio e confirma tabelas
representativas de cada fase.
