# suites/mocks.py
import pandas as pd
import time
import threading


# Mocks centralizados para simular o backend
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


class MockRepository:
    _data = {}
    _lock = threading.Lock()  # Adiciona um lock para segurança em concorrência

    @staticmethod
    def write_dataframe_to_table(df, table):
        with MockRepository._lock:
            if table not in MockRepository._data:
                MockRepository._data[table] = pd.DataFrame()
            # ignore_index=True é crucial para evitar problemas de índice
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

        q = ' & '.join([f'`{k}` == "{v}"' for k, v in where_conditions.items()])
        try:
            return df_copy.query(q)
        except:
            return pd.DataFrame()

    @staticmethod
    def update_table(table, updates, where_conditions):
        with MockRepository._lock:
            if table not in MockRepository._data:
                return 0

            df = MockRepository._data[table]
            if df.empty:
                return 0

            idx = pd.Series([True] * len(df), index=df.index)
            for k, v in where_conditions.items():
                idx &= (df[k] == v)

            if not any(idx):
                return 0

            for k, v in updates.items():
                df.loc[idx, k] = v

            return len(df[idx])

    #  FUNÇÃO CORRIGIDA 
    @staticmethod
    def delete_from_table(table, where_conditions):
        with MockRepository._lock:
            if table not in MockRepository._data:
                return 0

            df = MockRepository._data[table]
            if df.empty:
                return 0

            initial_len = len(df)

            # Cria uma máscara que começa com tudo 'True' (manter todas as linhas)
            # É crucial usar o índice do DataFrame para evitar o erro de alinhamento
            keep_mask = pd.Series([True] * len(df), index=df.index)

            # Aplica todas as condições 'where'. Uma linha só será removida se
            # corresponder a TODAS as condições (lógica AND).
            for k, v in where_conditions.items():
                # A condição para MANTER a linha é ela ser DIFERENTE do `where`
                keep_mask &= (df[k] != v)

            # Filtra o DataFrame para manter apenas as linhas desejadas
            new_df = df[keep_mask]

            # A linha mais importante: reseta o índice para [0, 1, 2, ...]
            # Isso previne erros de índice nas próximas operações concorrentes.
            MockRepository._data[table] = new_df.reset_index(drop=True)

            return initial_len - len(MockRepository._data[table])