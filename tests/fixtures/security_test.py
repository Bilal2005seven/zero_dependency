import hashlib


def dangerous_function(user_input):
    result = eval(user_input)

    exec(user_input)

    password_hash = hashlib.md5(
        user_input.encode()
    )

    return result, password_hash