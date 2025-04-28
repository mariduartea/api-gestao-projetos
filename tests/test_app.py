# biblioteca padrão

# import do projeto

# # teste para criar um usuário com sucesso
# def test_create_user(client, create_user):
#     response = create_user()
#     # Voltou o status code correto?
#     assert response.status_code == HTTPStatus.CREATED
#     # Validar o UserPublic
#     assert response.json() == {
#         'username': 'testusername',
#         'email': 'teste@teste.com',
#         'id': 1,
#     }
