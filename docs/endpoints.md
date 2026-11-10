# Endpoints

Documentação interativa (Swagger): `http://<ip-do-servidor>:8000/docs`.
Autenticação: `Authorization: Bearer <token>`. Câmeras usam o header `X-Camera-Key`.

## Autenticação (`/auth`)
| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/auth/login` | público | `{email, senha}` → token. `primeiro_acesso=true` exige troca. Bloqueia após 5 falhas/5 min. |
| POST | `/auth/trocar-senha` | logado (inclui 1º acesso) | `{senha_atual, nova_senha}` → novo token. |
| GET | `/auth/me` | logado | Dados do usuário (CPF mascarado). |

## Usuários (`/usuarios`)
| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/usuarios` | Admin, Super | Cria usuário e envia senha temporária. Só Super cria Admin. |
| GET | `/usuarios` | Admin, Super | Lista (filtros `papel`, `ativo`, `busca`, `limite`, `offset`). |
| GET | `/usuarios/moradores` | Porteiro, Admin, Super | Lista enxuta (id, nome, unidade) para cadastrar visitantes. |
| GET | `/usuarios/{id}` | Admin, Super | Detalhe. |
| PATCH | `/usuarios/{id}` | Admin, Super | Atualiza dados/papel/ativo. |
| POST | `/usuarios/{id}/resetar-senha` | Admin, Super | Nova senha temporária. |
| DELETE | `/usuarios/{id}` | Admin, Super | Desativação lógica. |

## Veículos (`/veiculos`)
| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/veiculos/moradores` | Admin, Super | Carro fixo `{placa, modelo, cor, dono_id}`. |
| POST | `/veiculos/visitantes` | Porteiro, Super | `{placa, modelo, cor, morador_id, duracao_horas (1–168), notas}`. Máx. 2 ativos por morador. |
| GET | `/veiculos` | logado (escopo por perfil) | Filtros `tipo`, `status`, `morador_id`. |
| GET | `/veiculos/{id}` | logado (escopo por perfil) | Detalhe. |
| PATCH | `/veiculos/{id}` | Admin (fixos), Porteiro (visitantes), Super | Edita modelo/cor/placa/notas; `status` só em fixos. |
| POST | `/veiculos/{id}/saida` | Porteiro, Super | Visitante → `DESATIVADO`. |
| POST | `/veiculos/{id}/reativar` | Porteiro, Super | Reativa visitante desativado há ≤ 48h (`{duracao_horas}` opcional). |
| DELETE | `/veiculos/{id}` | Admin, Super (visitantes: só Super) | Remove preservando o histórico. |

## Acessos e LPR (`/acessos`)
| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/acessos/lpr/imagem` | Câmera | Corpo = bytes da imagem (até 10 MB). Roda YOLO + EasyOCR e decide. |
| POST | `/acessos/lpr/placa` | Câmera | `{placa, confianca?}` para câmeras que já fazem OCR. |
| POST | `/acessos/abertura-manual` | Porteiro, Super | `{motivo, placa?}`. |
| GET | `/acessos` | logado (morador vê só o seu) | Filtros `data_inicio`, `data_fim`, `placa`, `resultado`, `origem`, `limite`, `offset`. |
| GET | `/acessos/relatorio` | Admin, Super | Totais do período (padrão 30 dias). `?formato=csv` exporta. |
| GET | `/acessos/logs-tecnicos` | Super | Últimas linhas do log (`?linhas=200`). |

Resposta de decisão: `{acesso_id, placa, liberado, motivo, rele_acionado, confianca}`.

### Exemplos

```bash
# Login
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
  -d '{"email":"admin@condominio.local","senha":"Trocar@123"}'

# Câmera enviando uma foto
curl -X POST http://localhost:8000/acessos/lpr/imagem -H "X-Camera-Key: $CAMERA_API_KEY" \
  --data-binary @placa.jpg

# Câmera enviando só o texto
curl -X POST http://localhost:8000/acessos/lpr/placa -H "X-Camera-Key: $CAMERA_API_KEY" \
  -H "Content-Type: application/json" -d '{"placa":"ABC1D23","confianca":0.93}'
```

## Sistema
`GET /saude` → `{"status":"ok"}` (health check).
