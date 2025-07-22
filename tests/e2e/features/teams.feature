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

Scenario: Successful end-to-end flow with a team
  Given a user is created
  When the user creates a new team
  Then the team appears in the team list
  And the team can be retrieved by its ID
  When the user updates the team data
  Then the updated team appears in the team list
  And the updated team can be retrieved by its ID
  When the user deletes the team
  Then the team no longer appears in the team list
  And the team cannot be retrieved by its ID

# Scenario: Tentar criar um time com um usuário inexistente, criar o usuário e validar que é adicionado no time com sucesso
# Scenario: Atualizar um time e verificar a alteração na lista de times
# Scenario: Deletar um time e tentar criar um projeto com esse time (falha)
