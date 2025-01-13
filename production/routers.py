class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'production':
            if model.__name__ in ['Procesos', 'Maquinaria', 'Clientes']:
                return 'spf_info'  # Lee desde spf_info para Procesos y Maquinaria
            elif model.__name__ == 'ParosProduccion':
                return 'spf_calidad'  # Lee desde la base de datos SPF_Calidad para ParosProduccion
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'production':
            if model.__name__ in ['Procesos', 'Maquinaria', 'Clientes']:
                return 'spf_info'  # Escribe en spf_info para Procesos y Maquinaria
            elif model.__name__ == 'ParosProduccion':
                return 'spf_calidad'  # Escribe en SPF_Calidad para ParosProduccion
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'production' and obj2._meta.app_label == 'production':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'production':
            if model_name in ['procesos', 'maquinaria', 'clientes']:
                return db == 'spf_info'
            elif model_name == 'parosproduccion':
                return db == 'spf_calidad'
        return None