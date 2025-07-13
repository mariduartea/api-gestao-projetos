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
    'MojoJojo',
]

# Nomes de times 
TEAM_NAMES = [
    'Elemento X',
    'Gangue Gangrena',
    'Escola Carvalhinho',
    'Trio Ameba',
    'Superpoderosas',
    'Townsville',
    'Meninos Desordeiros'
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

def fake_team_data(num_users=1):
    team_name = random.choice(TEAM_NAMES)
    users = [fake_user_data() for _ in range(num_users)]
    return {
        'team_name': team_name,
        'user_list': [user['username'] for user in users]
    }


def fake_project_name():
    return f'Projeto {faker.word().capitalize()}'
