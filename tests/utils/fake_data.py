import random

from faker import Faker

faker = Faker('en_US')

# Temas personalizados
GIRL_NAMES = [
    'Florzinha',
    'Lindinha',
    'Docinho',
    'Seduza',
    'Him',
    'ProfessorUtonio',
    'JomoMomo',
]


def fake_user_data():
    name = random.choice(GIRL_NAMES)
    return {
        'username': name.lower(),
        'email': f'{name.lower()}@cidadeville.com',
        'password': faker.password(length=8),
    }


def fake_team_name():
    return (
        f'Time {random.choice(["X", "Z", "Superpoderoso", "Cidade Segura"])}'
    )


def fake_project_name():
    return f'Projeto {faker.word().capitalize()}'
