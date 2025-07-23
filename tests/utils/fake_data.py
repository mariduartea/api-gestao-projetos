import random

from faker import Faker

faker = Faker('en_US')
used_names = set()

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
    'Meninos Desordeiros',
]


def unique_name():
    available_names = [name for name in GIRL_NAMES if name not in used_names]
    name = (
        random.choice(available_names)
        if available_names
        else faker.first_name()
    )
    used_names.add(name)
    return name.lower()


def fake_user_data():
    name = unique_name()
    return {
        'username': name,
        'email': f'{name}@cidadeville.com',
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
        'user_list': [user['username'] for user in users],
    }


def fake_project_name():
    return f'Projeto {faker.word().capitalize()}'
