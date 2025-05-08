# from http import HTTPStatus

# from fastapi import HTTPException

# from task_flow.database import get_user_by_email, get_user_count


# def check_already_registered_email(email: str):
#     if get_user_by_email(email):
#         raise HTTPException(
#             status_code=HTTPStatus.CONFLICT,
#             detail="Email already registered"
#         )


# def check_user_not_found(user_id: int):
#     if user_id < 1 or user_id > get_user_count():
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND, detail='User not found'
#         )
