# Referência de produto do frontend

## Superfícies atuais

O produto mantém dois frontends sobre a mesma API e o mesmo isolamento de
usuário: web em `localhost:8516` e mobile em `localhost:8517`. Eles compartilham
estética, serviços e contratos, mas podem evoluir em composição e navegação sem
duplicar regras de banca, apostas, recomendação ou autenticação.

A operação externa permanece pausada. O piloto G31 será local até nova decisão
explícita de hospedagem ou VPN privada.

O protótipo `Interactive Sports Betting Site.zip`, fornecido pelo proprietário,
é a referência de experiência do frontend React.

## Elementos adotados

- tema escuro e ação primária verde;
- página inicial centrada nas partidas;
- agrupamento por competição;
- página detalhada com abas ao vivo, escalação, estatísticas, mercados,
  análise e confrontos;
- bilhete lateral persistente;
- apostas simples e múltiplas;
- gestão de banca, favoritos e histórico;
- layout responsivo.

## Adaptações operacionais

- dados mock foram substituídos por chamadas `/api/v1`;
- horário vem convertido pelo backend;
- odds são revalidadas ao confirmar o bilhete;
- risco real é aplicado no backend;
- partidas encerradas não entram em análises/recomendações;
- erros de fontes e dados degradados são apresentados ao usuário;
- Streamlit deixa de controlar a navegação principal.

## Evolução de componentes

O protótipo ainda concentra componentes em `App.tsx`. A decomposição em
componentes e rotas ocorrerá sem alterar os contratos de API, permitindo
evolução incremental com testes visuais.
