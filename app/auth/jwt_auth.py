from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token

from app import flask_app

jwt = JWTManager(flask_app)


def create_jwt_access_token(identity: str, additional_claims: dict) -> str:
    """
    生成 jwt access_token
    """
    return create_access_token(
        identity=identity,
        additional_claims=additional_claims,
    )



