Feature: Gerenciamento de projetos

#Scenario: Tentar criar um projeto com um usuário inexistente, criar o time e validar que é adicionado no projeto com sucesso

Scenario: Update a projet and verify that the change appears in the project list
    Given a random user is created
    And a random team is created with that user
    And a random project is created with that team
    When the user updates the project name
    Then the project list should display the updated name

Scenario: Successful end-to-end flow with a project
    Given a random user is created
    And a random team is created with that user
    And a random project is created with that team
    And the user updates the project teams
    When the user deletes the project
    Then the project should no longer appear in the project list