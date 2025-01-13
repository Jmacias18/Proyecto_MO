class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'esterilizadores':
            if model.__name__ == 'Refrigerador':
                return 'spf_info'
            elif model.__name__ == 'TempEsterilizadores':
                return 'spf_calidad'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'esterilizadores':
            if model.__name__ == 'Refrigerador':
                return 'spf_info'
            elif model.__name__ == 'TempEsterilizadores':
                return 'spf_calidad'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'esterilizadores' and obj2._meta.app_label == 'esterilizadores':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'esterilizadores':
            if model_name == 'Refrigerador':
                return db == 'spf_info'
            elif model_name == 'TempEsterilizadores':
                return db == 'spf_calidad'
        return None
