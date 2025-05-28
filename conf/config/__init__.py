import os


run_env = os.environ.get("RUN_ENV", "develop").lower()

if run_env in ("prod", "product"):
    from conf.config import product
    config = product
elif run_env in ("test", "testing"):
    from conf.config import testing
    config = testing
else:
    from conf.config import develop
    config = develop


__all__ = ["config"]


