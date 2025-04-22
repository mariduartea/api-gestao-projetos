database = []


def get_all_users():
    return database


def get_user_count():
    return len(database)


def get_user_by_email(email: str):
    for user in database:
        if user.email == email:
            return user
    return None
