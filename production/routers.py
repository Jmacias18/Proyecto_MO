class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'production':
            if model.__name__ == 'Procesos':
                return 'default'  # Lee desde SPF_HRS_MO para Procesos
            elif model.__name__ in ['Maquinaria', 'Clientes', 'Conceptos']:  # Añadir Conceptos aquí
                return 'spf_info'  # Lee desde spf_info para Maquinaria, Clientes y Conceptos
            elif model.__name__ == 'ParosProduccion':
                return 'spf_calidad'  # Lee desde la base de datos SPF_Calidad para ParosProduccion
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'production':
            if model.__name__ == 'Procesos':
                return 'default'  # Escribe en SPF_HRS_MO para Procesos
            elif model.__name__ in ['Maquinaria', 'Clientes', 'Conceptos']:  # Añadir Conceptos aquí
                return 'spf_info'  # Escribe en spf_info para Maquinaria, Clientes y Conceptos
            elif model.__name__ == 'ParosProduccion':
                return 'spf_calidad'  # Escribe en SPF_Calidad para ParosProduccion
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'production' and obj2._meta.app_label == 'production':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'production':
            if model_name == 'procesos':
                return db == 'default'
            elif model_name in ['maquinaria', 'clientes', 'conceptos']:  # Añadir Conceptos aquí
                return db == 'spf_info'
            elif model_name == 'parosproduccion':
                return db == 'spf_calidad'
        return None