# Controle de acesso — perfis, regras e hardware

## Perfis e permissões

| Funcionalidade | Super ADM | Admin | Porteiro | Morador |
|---|:-:|:-:|:-:|:-:|
| Criar usuários (moradores/porteiros) | ✅ | ✅ | ❌ | ❌ |
| Criar/editar Admins | ✅ | ❌ | ❌ | ❌ |
| Carros fixos (criar/editar/remover) | ✅ | ✅ | ❌ (não vê) | Só visualiza os seus |
| Visitantes — criar / registrar saída / reativar | ✅ | ❌ (só visualiza) | ✅ | Visualiza os seus (até 2 ativos) |
| Abertura manual do portão | ✅ | ❌ | ✅ | ❌ |
| Histórico de acessos | Todos | Todos | Todos | Apenas o seu |
| Relatórios (JSON/CSV) | ✅ | ✅ | ❌ | ❌ |
| Logs técnicos (hardware/software) | ✅ | ❌ | ❌ | ❌ |
| CPF completo | ✅ | ✅ | mascarado | mascarado |

## Primeiro acesso

1. Admin cadastra o usuário → o sistema gera uma **senha temporária** e envia por e-mail.
2. No primeiro login, `/auth/login` devolve `primeiro_acesso: true` e um token **restrito** (15 min).
3. Esse token só funciona em `/auth/trocar-senha`. Após a troca, um novo token completo é emitido e os antigos são invalidados.

## LGPD

CPF é armazenado somente com dígitos e exibido como `***.***.123-**` para quem não é Admin/Super ADM.
Listagens enxutas (`/usuarios/moradores`, usada pelo porteiro) nunca incluem CPF nem telefone.

## Ciclo de vida do visitante

```
cadastro (duração 1h/12h/24h…) ──▶ ATIVO ──(prazo vence OU porteiro registra saída)──▶ DESATIVADO
                                                                                         │
                       ≤ 48h: porteiro pode REATIVAR ◀──────────────────────────────────┤
                       > 48h: job diário APAGA a placa ◀─────────────────────────────────┘
```

- Limite de **2 visitantes ativos por morador** (`MAX_VISITANTES_POR_MORADOR`).
- A expiração é aplicada em tempo real (na leitura e nas listagens) **e** pelo job diário (`JOB_LIMPEZA_HORARIO`, padrão 03:00; roda também ao subir a API).
- Carros fixos nunca são apagados pelo job.

## Abertura manual

`POST /acessos/abertura-manual` (porteiro). Registra `Abertura Manual por [Nome]: [motivo]`, origem `MANUAL`, com o operador.

## Hardware: relé e fallback

A API **nunca mantém o portão aberto**. Ela envia apenas um pulso:

```json
POST {RELE_URL}   Header: X-Rele-Token
{"acao": "pulso", "duracao_ms": 3000}
```

O microcontrolador fecha o relé sozinho ao fim do pulso. Assim, se o servidor cair no meio da operação, o portão não fica aberto. Se o microcontrolador não responder, a API registra `Autorizado, mas houve falha no acionamento do relé`, nega o acesso e grava erro crítico nos logs técnicos.

Esboço do firmware (ESP32/Arduino) — adapte pinos e autenticação:

```cpp
// POST /portao com JSON {"acao":"pulso","duracao_ms":N}
void tratarPulso(unsigned long ms) {
  ms = constrain(ms, 200, 5000);   // limite de segurança no próprio hardware
  digitalWrite(PINO_RELE, HIGH);
  delay(ms);                       // o hardware decide quando soltar
  digitalWrite(PINO_RELE, LOW);
}
```

Recomendações: botoeira/controle físico em paralelo ao relé (funciona sem o sistema), rede da câmera e do microcontrolador em VLAN/segmento isolado, e `X-Rele-Token` diferente da `CAMERA_API_KEY`.

## Rede

`SOMENTE_LAN=true` faz a API responder 403 para IPs públicos. Faça o bind do Uvicorn na interface interna (`--host 192.168.x.x`) e **não** exponha a porta no roteador. Para VPN, use `REDES_PERMITIDAS`.
