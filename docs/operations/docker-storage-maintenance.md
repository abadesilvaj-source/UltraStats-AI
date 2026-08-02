# Manutenção segura do armazenamento Docker

Atualizado em: 2 de agosto de 2026.

Esta rotina controla o crescimento do disco virtual do Docker sem remover dados
do PostgreSQL. Ela integra a G27.1 e não deve ser executada parcialmente ou sem
as verificações obrigatórias.

## Princípio de segurança

Volumes são dados; cache de build é descartável. A manutenção automática só
pode atuar sobre cache de build e imagens sem uso. Volumes, bancos, diretórios
de exportação e backups ficam fora do escopo de limpeza.

Comandos que incluam `--volumes`, remoção explícita de volume ou exclusão do
diretório de dados do PostgreSQL são proibidos nesta rotina.

## Fotografia inicial

Em 2 de agosto de 2026:

| Componente | Uso | Potencialmente recuperável |
|---|---:|---:|
| Cache de build | 22,12 GB | 19,30 GB |
| Imagens | 3,44 GB | 1,24 GB |
| Volumes locais | 2,97 GB | 162 MB |
| Volume PostgreSQL ativo | 2,77 GB | não removível |

Esses valores expiram e devem ser medidos novamente antes de cada execução.

## Gate obrigatório antes da limpeza

- [ ] identificar nominalmente o volume PostgreSQL ativo;
- [ ] registrar `docker system df` e `docker system df -v`;
- [ ] confirmar todos os serviços saudáveis;
- [ ] gerar backup lógico do banco fora do volume PostgreSQL;
- [ ] calcular checksum SHA-256 do backup;
- [ ] restaurar o backup em banco temporário isolado;
- [ ] comparar tabelas críticas e contagens mínimas;
- [ ] confirmar espaço suficiente no Windows para backup e restore;
- [ ] registrar responsável, horário e motivo da manutenção.

Se qualquer item falhar, a limpeza é cancelada.

## Escopo permitido

1. Remover somente cache de build não referenciado.
2. Remover somente imagens dangling ou comprovadamente sem container associado.
3. Preservar imagens dos cinco serviços ativos até o smoke test terminar.
4. Repetir a medição de armazenamento.
5. Executar health checks e smoke tests web/mobile/API.

Exemplos de operações permitidas após o gate:

```powershell
docker builder prune
docker image prune
```

Os comandos devem permanecer interativos ou usar filtros de idade previamente
revisados. A opção `-a` exige inventário nominal adicional das imagens.

## Operações proibidas

```text
docker system prune --volumes
docker volume prune
docker volume rm <volume-postgresql>
docker compose down -v
exclusão manual de arquivos dentro de PGDATA
```

Também é proibido selecionar alvos por glob ou nome parcial sem conferir o nome
completo do volume.

## Validação posterior

- [ ] PostgreSQL, backend, scheduler, web e mobile estão saudáveis;
- [ ] login funciona;
- [ ] partidas e competições carregam;
- [ ] contagens de partidas, usuários, apostas e previsões não diminuíram;
- [ ] uma leitura de banca do usuário autenticado funciona;
- [ ] o scheduler registra heartbeat;
- [ ] o espaço recuperado foi documentado;
- [ ] o backup continua íntegro e acessível.

## Rollback e recuperação

Limpeza de cache não exige rollback: builds futuros recriam as camadas. Se uma
imagem necessária tiver sido removida, ela deve ser reconstruída a partir do
código sem alterar volumes. Se qualquer validação de dados falhar, interrompa os
jobs de escrita, preserve o volume atual e restaure o backup verificado em um
novo volume; nunca sobrescreva o volume original antes da comparação.

## Frequência e alertas

- medir semanalmente e antes de builds grandes;
- alerta amarelo em 75% do limite do disco virtual;
- alerta laranja em 85%;
- alerta vermelho em 90%, suspendendo builds e backfills não essenciais;
- executar limpeza quando cache recuperável superar 5 GB ou uso total atingir
  75%, sempre respeitando o gate.

## Evidência mínima

Cada execução deve registrar: uso antes/depois, cache removido, imagens
removidas, volume PostgreSQL preservado, checksum do backup, resultado do teste
de restore e smoke tests posteriores.
## Retenção automatizada protegida

`SafeRetentionService` apenas executa compactação se
`DATA_RETENTION_ENABLED=true` **e** existir backup com status `verified` nos
últimos sete dias. A execução ocorre em lotes; apostas fictícias e as
recomendações que lhes deram origem nunca são removidas. O padrão permanece
`false`, permitindo medir o volume candidato antes de autorizar exclusões.
