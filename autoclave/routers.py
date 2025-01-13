class AutoclaveDatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'autoclave':
            if model.__name__ == 'Refrigerador':
                return 'spf_info'  # Usar la base de datos 'spf_info' para 'Refrigerador'
            return 'default'  # Para otros modelos, usa la base de datos predeterminada
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'autoclave':
            if model.__name__ == 'Refrigerador':
                return 'spf_info'  # Usar 'spf_info' para las escrituras en 'Refrigerador'
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'autoclave' or obj2._meta.app_label == 'autoclave':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'autoclave':
            return db == 'spf_info' if model_name == 'Refrigerador' else db == 'default'
        return None
