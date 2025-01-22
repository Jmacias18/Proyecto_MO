class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'esterilizadores':
            if model.__name__ == 'TempEsterilizadores':
                return 'spf_calidad'
        elif model._meta.app_label == 'production':
            if model.__name__ == 'Maquinaria':
                return 'spf_info'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'esterilizadores':
            if model.__name__ == 'TempEsterilizadores':
                return 'spf_calidad'
        elif model._meta.app_label == 'production':
            if model.__name__ == 'Maquinaria':
                return 'spf_info'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'esterilizadores' and obj2._meta.app_label == 'esterilizadores':
            return True
        elif obj1._meta.app_label == 'production' and obj2._meta.app_label == 'esterilizadores':
            return True
        elif obj1._meta.app_label == 'esterilizadores' and obj2._meta.app_label == 'production':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'esterilizadores':
            if model_name == 'TempEsterilizadores':
                return db == 'spf_calidad'
        elif app_label == 'production':
            if model_name == 'Maquinaria':
                return db == 'spf_info'
        return None