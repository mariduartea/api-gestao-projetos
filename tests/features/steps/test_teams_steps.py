from behave import given, when, then

@given("the API has a registered team")
def verify_registered_team(context):
    pass

@given("this team is associated with a project")
def verify_associated_team_with_project(context):
    pass

@when("this team is edited")
def edit_team(context):
    pass

@then("the updates should be reflected in the project")
def verify_updated_team_in_project(context):
    pass