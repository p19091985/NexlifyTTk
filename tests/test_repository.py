import pandas as pd
import pytest
from sqlalchemy import select, insert, update, event
from sqlalchemy.exc import IntegrityError
from persistencia.repository import GenericRepository as Repository
from persistencia import auth
from persistencia.schema import usuarios, tipos_vegetais, vegetais, log_alteracoes
from persistencia.data_service import DataService
PASSWORD = 'Teste seguro do template 2026!'


def test_crud_and_audit(administrator):
    previous_events = len(Repository.read_table_to_dataframe('log_alteracoes'))
    Repository.write_dataframe_to_table(pd.DataFrame([{'nome':'Folhas'}]), 'tipos_vegetais')
    row = Repository.read_table_to_dataframe('tipos_vegetais').iloc[0]
    Repository.update_table('tipos_vegetais', {'nome':'Frutos'}, {'id':int(row.id)})
    assert Repository.read_table_to_dataframe('tipos_vegetais').iloc[0]['nome'] == 'Frutos'
    Repository.delete_from_table('tipos_vegetais', {'id':int(row.id)})
    assert Repository.read_table_to_dataframe('tipos_vegetais').empty
    assert len(Repository.read_table_to_dataframe('log_alteracoes')) == previous_events + 3


def test_no_unbounded_write_or_identifier_injection(administrator):
    with pytest.raises(ValueError):
        Repository.delete_from_table('usuarios', {})
    with pytest.raises(ValueError):
        Repository.read_table_to_dataframe('usuarios; DROP TABLE usuarios')
    with pytest.raises(ValueError):
        Repository.read_table_to_dataframe('usuarios', ['senha_criptografada'])
    with pytest.raises(ValueError):
        Repository.update_table('usuarios', {'nome_completo = 1 --':'x'}, {'login_usuario':'admin'})
    with pytest.raises(ValueError):
        Repository.execute_query_to_dataframe('DELETE FROM usuarios')


def test_unauthenticated_and_auditor_cannot_write(administrator):
    auth.clear_session()
    with pytest.raises(PermissionError):
        Repository.read_table_to_dataframe('vegetais')
    with administrator.begin() as connection:
        connection.execute(insert(usuarios).values(login_usuario='auditor', senha_criptografada=auth.hash_password(PASSWORD),
                           nome_completo='Auditor', tipo_acesso='Auditor Externo'))
    auth.verify_user_credentials('auditor', PASSWORD)
    with pytest.raises(PermissionError):
        Repository.write_dataframe_to_table(pd.DataFrame([{'nome':'Falha'}]), 'tipos_vegetais')
    with pytest.raises(PermissionError):
        Repository.read_table_to_dataframe('usuarios')
    with pytest.raises(PermissionError):
        DataService.rename_especie_gato_e_logar('a','b','admin')


def test_last_admin_protected(administrator):
    with pytest.raises(ValueError, match='último'):
        Repository.delete_from_table('usuarios', {'login_usuario':'admin'})
    with pytest.raises(ValueError, match='último'):
        Repository.update_table('usuarios', {'tipo_acesso':'Auditor Externo'}, {'login_usuario':'admin'})


def test_business_transaction_rolls_back_if_audit_fails(administrator):
    with administrator.begin() as connection:
        connection.execute(insert(tipos_vegetais), [{'nome':'A'},{'nome':'B'}])
        connection.execute(insert(vegetais).values(nome='Vegetal', id_tipo=1))
    def fail_audit(conn, cursor, statement, params, context, executemany):
        if 'INSERT INTO log_alteracoes' in statement:
            raise IntegrityError('audit blocked', {}, Exception('test failure'))
    event.listen(administrator, 'before_cursor_execute', fail_audit)
    try:
        success, _ = DataService.reclassificar_vegetal_e_logar('Vegetal','B','admin')
        assert not success
    finally:
        event.remove(administrator, 'before_cursor_execute', fail_audit)
    with administrator.connect() as connection:
        assert connection.execute(select(vegetais.c.id_tipo)).scalar_one() == 1
