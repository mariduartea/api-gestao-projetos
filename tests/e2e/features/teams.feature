Feature: Team management

Scenario: Update a team and verify that the changes appear in the project list
  Given the API has a registered team
  And this team is associated with a project
  When this team is edited
  Then the updates should be reflected in the project

Scenario: Deleting a team and verify if it doesn't exist in a certain project
  Given the API has a registered team
  And this team is associated with a project
  And another random team is created
  And the project list is updated with the new team
  When this team is deleted
  Then the deleted team have to disappear in project list

# Scenario: Fluxo completo e feliz com time
# Scenario: Tentar criar um time com um usuário inexistente, criar o usuário e validar que é adicionado no time com sucesso
# Scenario: Atualizar um time e verificar a alteração na lista de times
# Scenario: Deletar um time e tentar criar um projeto com esse time (falha)
