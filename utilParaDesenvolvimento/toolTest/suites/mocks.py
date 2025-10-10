# suites/mocks.py
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


class MockRepository:
    _data = {}
    _lock = threading.Lock()

    @staticmethod
    def write_dataframe_to_table(df, table):
        with MockRepository._lock:
            if table not in MockRepository._data:
                MockRepository._data[table] = pd.DataFrame()
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
            if table not in MockRepository._data: return 0
            df = MockRepository._data[table]
            if df.empty: return 0
            idx = pd.Series([True] * len(df), index=df.index)
            for k, v in where_conditions.items():
                idx &= (df[k] == v)
            if not any(idx): return 0
            for k, v in updates.items():
                df.loc[idx, k] = v
            return len(df[idx])

    # --- FUNÇÃO CORRIGIDA E ROBUSTA ---
    @staticmethod
    def delete_from_table(table, where_conditions):
        """
        Exclui linhas de um DataFrame de forma segura para concorrência,
        resetando o índice para manter a integridade dos dados.
        """
        with MockRepository._lock:
            if table not in MockRepository._data:
                return 0
            df = MockRepository._data[table]
            if df.empty:
                return 0

            initial_len = len(df)
            keep_mask = pd.Series([True] * len(df), index=df.index)

            for k, v in where_conditions.items():
                keep_mask &= (df[k] != v)

            new_df = df[keep_mask]

            # Linha crucial: Reseta o índice para [0, 1, 2, ...],
            # prevenindo erros em operações concorrentes futuras.
            MockRepository._data[table] = new_df.reset_index(drop=True)

            return initial_len - len(MockRepository._data[table])