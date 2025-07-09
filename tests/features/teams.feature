Feature: Team management

Scenario: Update a team and verify that the changes appear in the project list
  Given the API has a registered team
  And this team is associated with a project
  When this team is edited
  Then the updates should be reflected in the project

# Scenario: Deletar um time e verificar que ele não existe mais em um determinado projeto
# Scenario: Fluxo completo e feliz com time
# Scenario: Tentar criar um time com um usuário inexistente, criar o usuário e validar que é adicionado no time com sucesso
# Scenario: Atualizar um time e verificar a alteração na lista de times
# Scenario: Deletar um time e tentar criar um projeto com esse time (falha)
