Feature: Gerenciamento de usuários

# Scenario: Fluxo completo e feliz com usuário
# Scenario: Atualizar um usuário e verificar a alteração na lista de usuários  
# Scenario: Deletar um usuário e tentar criar um time com esse usuário (falha)

Scenario: Update a user and verify that the change appears in the team list
    Given a random user is created
    And a random team is created with that user
    When the user changes their name
    Then the team must list the new name as a member

Scenario: Update a user and verify that the change appears in the project list
    Given a random user is created
    And a random team is created with that user
    And a random project is created with that team
    When the user changes their name
    Then the project must list the new name as a member

Scenario: Delete a user and verify that they no longer appear as a member of a team
    Given a random user is created
    And a random team is created with that user
    And another random user is created
    And the team list is updated with the new user
    When the other user is deleted
    Then the team must not list the deleted user as a member

Scenario: Delete a user and verify that they no longer appear as a member of a project
    Given a random user is created
    And a random team is created with that user
    And another third random user is created
    And the team list is updated with the third user
    And a random project is created with that updated team
    When the third user is deleted
    Then the project must not list the deleted user as a member