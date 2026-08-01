"""Camada de aplicação do UltraStats AI.

A camada de aplicação coordena os casos de uso do sistema.

Ela pode:

- receber comandos;
- executar consultas;
- carregar agregados;
- chamar serviços de domínio;
- controlar Unit of Work;
- publicar eventos;
- retornar DTOs.

Ela não deve conter regras centrais de negócio.
"""