TORTOISE_ORM = {
    'connections': {
        # Dict format for connection
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': 'pgdb',
                'port': '5432',
                'user': 'postgres',
                'password': 'postgres',
                'database': 'postgres',
            },
        },
    },
    'apps': {
        'models': {
            'models': ["models", "aerich.models"],
            'default_connection': 'default',
        }
    },
}
