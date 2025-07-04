Feature: Gerenciamento de usuários


# Scenario: Atualizar um usuário e verificar que o que foi alterado aparece na lista de projetos
# Scenario: Deletar um usuário e verificar que ele não existe mais em um determinado time
# Scenario: Deletar um usuário e verificar que ele não existe mais em um determinado projeto
# Scenario: Fluxo completo e feliz com usuário
# Scenario: Atualizar um usuário e verificar a alteração na lista de usuários  
# Scenario: Deletar um usuário e tentar criar um time com esse usuário (falha)

Scenario: Atualizar um usuário e verificar que o que foi alterado aparece na lista de times
  Given um usuário chamado "florzinha" com email "florzinha@cidadeville.com" e senha "docinho123"
  And um time chamado "Laboratório do Professor" é criado com o usuário "florzinha"
  When o usuário "florzinha" altera seu nome para "superflorzinha"
  Then o time "Laboratório do Professor" deve listar "superflorzinha" como membro

