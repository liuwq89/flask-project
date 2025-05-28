from passlib.hash import bcrypt


def generate_password_hash(password: str) -> str:
    """
    根据明文密码生成 hash密码串
    """
    return bcrypt.hash(password)


def verify_password(password: str, hash_password) -> bool:
    """
    校验明文密码和哈希密码是否匹配
    """
    return bcrypt.verify(password, hash_password)




