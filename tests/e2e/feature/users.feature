Feature: Gerenciamento de usuários

# Scenario: Deletar um usuário e verificar que ele não existe mais em um determinado time
# Scenario: Deletar um usuário e verificar que ele não existe mais em um determinado projeto
# Scenario: Fluxo completo e feliz com usuário
# Scenario: Atualizar um usuário e verificar a alteração na lista de usuários  
# Scenario: Deletar um usuário e tentar criar um time com esse usuário (falha)

Scenario: Update a user and verify that the change appears in the team list
  Given a user called "florzinha" with email "florzinha@cidadeville.com" and password "docinho123"
  And a team called "Laboratório do Professor" is created with user "florzinha"
  When the user "florzinha" changes their name to "superflorzinha"
  Then the team "Laboratório do Professor" must list "superflorzinha" as a member

Scenario: update a user and verify that the change appears in the project list
    Given a user called "lindinha" with email "lindinha@cidadeville.com" and password "docinho123"
    And a team called "Laboratório X" is created with user "lindinha"
    And a project called "Salvar o planeta" is created with team "Laboratório X"
    When the user "lindinha" changes their name to "superlindinha"
    Then the project "Salvar o planeta" must list "superlindinha" as a member
