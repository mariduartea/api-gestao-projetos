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

used_names = set()


def fake_user_data():
    # Garante que o nome escolhido não foi usado ainda
    available_names = [n for n in GIRL_NAMES if n.lower() not in used_names]

    if not available_names:
        # Se acabaram os nomes, gera um nome faker único
        name = faker.unique.user_name()
    else:
        name = random.choice(available_names)
        used_names.add(name.lower())

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
