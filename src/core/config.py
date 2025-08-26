from environs import Env


class Settings:

    def __init__(self):
        env = Env()
        env.read_env()

        self.DB_URL = env.str('DB_URL', 'database.db') 



settings = Settings()