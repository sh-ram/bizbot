from typing import Dict, List, NamedTuple

import sqlite3

class UpdateValue(NamedTuple):
    column: str
    value: str

conn = sqlite3.connect('currency.db', check_same_thread=False)#
cursor = conn.cursor()

def fetchall(table: str, 
             columns: List[str],
             where_clause: str=None) -> List[dict]:
    """ 
        Return all values from target db table.
        Additional get rows by where clause.
    """
    if not where_clause: where_clause = ''
    columns_joined = '`, `'.join(columns)
    # tables_joined = '`, `'.join(tables)
    cursor.execute(f'SELECT `{columns_joined}` FROM `{table}`' \
                   f'{where_clause}')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    conn.commit()
    return result

def insert(table: str,
           columns_values: Dict,
           constraint: List=None):
    """Commit db insert query. Used constraint values to update exist row."""
    columns = '`, `'.join( columns_values.keys() )
    values = [ tuple(columns_values.values()) ]
    placeholders = ', '.join( "?" * len(columns_values.keys()) ) 
    upsert = _get_upsert(columns_values, constraint)
    cursor.executemany(
        f'INSERT INTO `{table}` (`{columns}`)'
        f'VALUES ({placeholders}) {upsert}',
        values)
    conn.commit()

def _get_upsert(columns_values: Dict,
                constraint: List) -> str:
    """ 
        Get additional part of database insert query.
        Returned string is actually update target existing
            db row by out of constraint values.
    """
    columns = columns_values.keys()
    upsert_columns = [ column for column in columns if column not in constraint ]
    if not constraint and not upsert_columns:
        return ''
    constraint = '`, `'.join(constraint)
    values = []
    for column in upsert_columns:
        values.append(f"`{column}` = '{columns_values[column]}'")
    values = ', '.join(values)
    upsert = f'ON CONFLICT (`{constraint}`)'\
             f'DO UPDATE SET {values}'
    return upsert

def update(table: str, 
           update_value: UpdateValue, 
           where_clause: str=''):
    update_column, update_value = update_value
    cursor.execute(
        f'UPDATE `{table}` '
        f'SET `{update_column}` = "{update_value}" '
        f'{where_clause}'
    )
    conn.commit()

def get_cursor() -> sqlite3.Cursor:
    return cursor

# def delete(table: str, delete_value: DeleteValue) -> None:
#     """ Delete from target db table by values dict. """
#     column, value = delete_value
#     cursor.execute(
#         f'DELETE FROM `{table}` '
#         f'WHERE `{column}` = "{value}"'
#     )
#     conn.commit()
