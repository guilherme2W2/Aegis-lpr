# Configuração da conexão com o banco

# Pontos de alerta: A. Relação entre veículos e moradores

# A tabela veiculos_moradores possui id_residencia, em vez de id_morador.

# Isso significa que o veículo está vinculado diretamente à residência, e não a uma pessoa específica.

# Não é necessariamente um problema: pode ser uma decisão adequada para condomínios, onde vários moradores compartilham veículos.

# B. Ativação e desativação dos veículos

# A tabela veiculos_moradores não possui um campo explícito para indicar se o veículo está ativo ou inativo.

# Entretanto, o Integrante 3 precisa implementar essa funcionalidade.

# Precisaremos discutir a inclusão de um campo como:
# ativo BOOLEAN NOT NULL DEFAULT TRUE


# C. Horários permitidos

# A tabela agendamento_acesso possui data e horários de início e fim, mas está relacionada a visitantes e prestadores.

# Não encontramos, no script, uma estrutura explícita para horários de autorização dos veículos dos moradores.

# Isso precisa ser discutido com o Integrante 4 antes da implementação das regras de negócio.
# condominio.sql
# Minha recomendação: não modifique o banco agora. Preserve o script original e registre essas três questões para discussão com os responsáveis pelos módulos.