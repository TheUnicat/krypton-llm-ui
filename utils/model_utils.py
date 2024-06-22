import sqlite3


class LLMModelsDB:
    def __init__(self, db_name='llm_models.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def get_model(self, model):
        provider, family, version = model
        query = '''
        SELECT m.name
        FROM models m
        JOIN model_families mf ON m.family_id = mf.family_id
        JOIN providers p ON mf.provider_id = p.provider_id
        WHERE p.name = ? AND mf.name = ? AND m.version = ?
        '''
        self.cursor.execute(query, (provider, family, version))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_model_info(self, model):
        provider, family, version = model
        query = '''
        SELECT m.*
        FROM models m
        JOIN model_families mf ON m.family_id = mf.family_id
        JOIN providers p ON mf.provider_id = p.provider_id
        WHERE p.name = ? AND mf.name = ? AND m.version = ?
        '''
        self.cursor.execute(query, (provider, family, version))
        result = self.cursor.fetchone()
        if result:
            return {
                'name': result[3],
                'vision': bool(result[4]),
                'path': result[5],
                'input_cost': result[6],
                'output_cost': result[7]
            }
        return None

    def get_model_path(self, model):
        model_info = self.get_model_info(model)
        return model_info['path'] if model_info else None

    def get_model_family_info(self, api, product_family):
        query = '''
        SELECT m.*
        FROM models m
        JOIN model_families mf ON m.family_id = mf.family_id
        JOIN providers p ON mf.provider_id = p.provider_id
        WHERE p.name = ? AND mf.name = ?
        '''
        self.cursor.execute(query, (api, product_family))
        results = self.cursor.fetchall()
        if results:
            return {row[2]: {
                'name': row[3],
                'vision': bool(row[4]),
                'path': row[5],
                'input_cost': row[6],
                'output_cost': row[7]
            } for row in results}
        return None

    def is_local_model(self, api, product_family, model_version=None):
        query = '''
        SELECT COUNT(*)
        FROM model_families mf
        JOIN providers p ON mf.provider_id = p.provider_id
        WHERE p.name = ? AND mf.name = ?
        '''
        params = [api, product_family]

        if api != 'Local' and model_version:
            query += ' AND EXISTS (SELECT 1 FROM models m WHERE m.family_id = mf.family_id AND m.version = ?)'
            params.append(model_version)

        self.cursor.execute(query, params)
        count = self.cursor.fetchone()[0]
        return count > 0

    def get_all_local_models(self):
        query = '''
        SELECT mf.name
        FROM model_families mf
        JOIN providers p ON mf.provider_id = p.provider_id
        WHERE p.name = 'Local'
        '''
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def __del__(self):
        self.conn.close()


db = LLMModelsDB()
def get_model(model):
    return db.get_model(model)

def get_model_info(model):
    return db.get_model_info(model)

def get_model_path(model):
    return db.get_model_path(model)

def get_model_family_info(api, product_family):
    return db.get_model_family_info(api, product_family)

def is_local_model(api, product_family, model_version=None):
    return db.is_local_model(api, product_family, model_version)

def get_all_local_models():
    return db.get_all_local_models()

