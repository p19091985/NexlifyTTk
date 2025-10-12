                 
import pandas as pd
import time
import threading


class MockAuth:
    @staticmethod
    def verify_user_credentials(username, password):
        time.sleep(0.05)
        return {'username': username} if username == 'admin' and password == 'admin' else None


class MockDataService:
    @staticmethod
    def rename_especie_gato_e_logar(old_name, new_name, user):
        time.sleep(0.1)
        if "falha" in new_name.lower() or "fail" in new_name.lower():
            raise ValueError("Simulação de falha de integridade no log")
        return True, "Sucesso no Mock"

                                                                
    @staticmethod
    def reclassificar_vegetal_e_logar(nome_vegetal, novo_tipo_nome, usuario):
        """Mock para a transação de reclassificação de vegetais."""
        time.sleep(0.1)
        if "falha" in novo_tipo_nome.lower():
            raise ValueError("Simulação de falha de integridade na reclassificação")
        return True, "Vegetal reclassificado com sucesso no mock."


class MockRepository:
    _data = {}
    _lock = threading.Lock()

    @staticmethod
    def write_dataframe_to_table(df, table):
        with MockRepository._lock:
            if table not in MockRepository._data:
                MockRepository._data[table] = pd.DataFrame()
                                                                                         
            df.columns = [col.lower() for col in df.columns]
            MockRepository._data[table] = pd.concat([MockRepository._data[table], df], ignore_index=True)
            return True

    @staticmethod
    def read_table_to_dataframe(table, where_conditions=None):
        with MockRepository._lock:
            if table not in MockRepository._data:
                return pd.DataFrame()
            df_copy = MockRepository._data[table].copy()

        if not where_conditions:
            return df_copy

                                                                                  
        where_lower = {k.lower(): v for k, v in where_conditions.items()}
        q = ' & '.join([f'`{k}` == "{v}"' for k, v in where_lower.items()])
        try:
            return df_copy.query(q)
        except:
            return pd.DataFrame()

    @staticmethod
    def update_table(table, updates, where_conditions):
        with MockRepository._lock:
            if table not in MockRepository._data: return 0
            df = MockRepository._data[table]
            if df.empty: return 0

            idx = pd.Series([True] * len(df), index=df.index)
            where_lower = {k.lower(): v for k, v in where_conditions.items()}
            for k, v in where_lower.items():
                if k in df.columns:
                    idx &= (df[k] == v)

            if not any(idx): return 0

            updates_lower = {k.lower(): v for k, v in updates.items()}
            for k, v in updates_lower.items():
                if k in df.columns:
                    df.loc[idx, k] = v
            return len(df[idx])

    @staticmethod
    def delete_from_table(table, where_conditions):
        with MockRepository._lock:
            if table not in MockRepository._data:
                return 0
            df = MockRepository._data[table]
            if df.empty:
                return 0

            initial_len = len(df)
            keep_mask = pd.Series([True] * len(df), index=df.index)

            where_lower = {k.lower(): v for k, v in where_conditions.items()}
            for k, v in where_lower.items():
                if k in df.columns:
                    keep_mask &= (df[k] != v)

            new_df = df[keep_mask]

            MockRepository._data[table] = new_df.reset_index(drop=True)
            return initial_len - len(MockRepository._data[table])