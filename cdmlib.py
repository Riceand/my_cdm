import os
import re
import xlrd
from helper import mkdirs, exist_path

TABLE_NAME = 'Table Name'
TABLE_COLUMN = 'Table Column'
KEY = 'Key'
DATA_TYPE = 'Data Type'
ROW = 'row'
COL = 'col'
FOLDER_CDM = 'CDM'
FOLDER_DDL = FOLDER_CDM + '/DDL/'
FOLDER_INSERT = FOLDER_CDM + '/INSERT/'
FOLDER_VIEW = FOLDER_CDM + '/VIEW/'

def create_folders():
    mkdirs(FOLDER_DDL)
    mkdirs(FOLDER_INSERT)
    mkdirs(FOLDER_VIEW)
    return True

def create_file(file_name):
    return open(file_name, 'w+')

def read_file(file_name):
    return open(file_name, 'r')

def write_sql(file_name, sheet_name, folder):
    the_sheet = get_sheet(file_name, sheet_name)
    table_name = get_table_name(the_sheet)
    f = create_file(folder + table_name + '.sql')
    sql = fn_gen_sql(folder)(the_sheet)
    f.write(sql)
    f.close()

def write_ddl_sql(file_name, sheet_name):
    write_sql(file_name, sheet_name, FOLDER_DDL)

def write_view_sql(file_name, sheet_name):
    write_sql(file_name, sheet_name, FOLDER_VIEW)

def remove_file(file_name):
    return os.remove(file_name)

def open_workbook(file_name):
    if exist_path(file_name):
        return xlrd.open_workbook(file_name)
    return None

def get_sheet(file_name, sheet_name):
    if exist_path(file_name):
        wb = xlrd.open_workbook(file_name)
        try:
            return wb.sheet_by_name(sheet_name)
        except Exception as e:
            print(e)
            return None
    return None

def get_row_values(the_sheet):
    the_range = list(range(the_sheet.nrows))
    return list(map(lambda i: the_sheet.row_values(i), the_range))

def get_col_values(the_sheet):
    the_range = list(range(the_sheet.ncols))
    return list(map(lambda i: the_sheet.col_values(i), the_range))

def find_index_in_list(ls, v):
    try:
        return ls.index(v)
    except ValueError as ve:
        print(ve)
        return -1

def find_first_value_y(cols, title):
    start = False # 是否开始查找，从上往下只有找到 title 后，再开始找第一个不为空的值。
    i = 0
    for l in cols:
        if start and l.strip() != '':
            return i
        if l == title:
            start = True
        i = i + 1
    return -1

def replace_space_in_name(name, repl):
    return re.sub(r'\s+', repl, name)

def find_table_name_in_cols(cols):
    i = find_first_value_y(cols, TABLE_NAME)
    if i >= 0:
        return replace_space_in_name(cols[i], '')
    return ''

def find_cell_pos(sheet, cell_value):
    rows = get_row_values(sheet)
    x = -1
    y = -1
    for row in rows:
        x = x + 1
        f = find_index_in_list(row, cell_value)
        if f >= 0:
            y = f
            return {ROW: x, COL: y}
    return {ROW: -1, COL: -1}

def convert_table_column(cell_value):
    # 替换所有非字母、数字和下划线的字符为 '_'，如："(transaction) (part code) "
    tmp1 = re.sub(r'\W', '_', cell_value)
    # 删除开头和结尾的所有下划线，如："_transaction___part_code__"
    tmp2 = re.sub(r'^_+|_+$', '', tmp1)
    # 替换中间多个下划线为一个下划线，如："transaction___part_code"
    tmp3 = re.sub(r'_+', '_', tmp2)
    # 全部转换为大写，如："TRANSACTION_PART_CODE"
    return tmp3.upper()

def convert_column_type(cell_value):
    map_types = {
        'NUMBER': 'NUMERIC',
        'DATE': 'DATE',
        'TIME': 'TIME',
        'TIMESTAMP': 'TIMESTAMP',
    }
    return map_types.get(cell_value.upper(), 'STRING')

def convert_pk(cell_value):
    if cell_value and cell_value.lower().find('pk') >= 0:
        return 'NOT NULL'
    return ''

def get_table_name(the_sheet):
    pos_table_name = find_cell_pos(the_sheet, TABLE_NAME)
    cols = get_col_values(the_sheet)
    table_names = cols[pos_table_name[COL]]
    return find_table_name_in_cols(table_names)

def get_column_all_values(the_sheet, title):
    cols = get_col_values(the_sheet)
    pos = find_cell_pos(the_sheet, title)
    return cols[pos[COL]]

def find_last_value_y(col_all_vals):
    last_index = len(col_all_vals) - 1
    last = col_all_vals[last_index]
    if last == '':
        col_all_vals.pop()
        return find_last_value_y(col_all_vals)
    else:
        # y_to need + 1, not just the index
        return last_index + 1

def get_column_values(the_sheet, title):
    col_all_vals = get_column_all_values(the_sheet, title)
    y_from = find_first_value_y(col_all_vals, title)
    y_to = find_last_value_y(col_all_vals)
    return col_all_vals[y_from:y_to]

def get_str_item(array, i):
    return array[i] if i < len(array) else ''

def gen_ddl_columns(columns, types, pks):
    results = []
    for i in range(len(columns)):
        #FIXME the i out of range
        str_pks = convert_pk(get_str_item(pks, i))
        str_types = convert_column_type(get_str_item(types, i))
        result = ' '.join([columns[i], str_types, str_pks])
        # 将多个空格替换为一个空格
        result = replace_space_in_name(result, ' ')
        results.append(result.strip())
    return results

def gen_ddl_sql(the_sheet):
    table_name = get_table_name(the_sheet)
    columns = get_column_values(the_sheet, TABLE_COLUMN)
    pks = get_column_values(the_sheet, KEY)
    types = get_column_values(the_sheet, DATA_TYPE)
    ddl_columns = gen_ddl_columns(columns, types, pks)
    str_columns = ',\n'.join(ddl_columns)

    result_sql = []
    result_sql.append('CREATE OR REPLACE TABLE {cdm_table_dataset}.' + table_name)
    result_sql.append('(')
    result_sql.append(str_columns)
    result_sql.append(');')
    return '\n'.join(result_sql)

def gen_view_sql(the_sheet):
    table_name = get_table_name(the_sheet)
    columns = get_column_values(the_sheet, TABLE_COLUMN)
    # print(columns)
    str_columns = ',\n'.join(columns)

    result_sql = []
    result_sql.append('CREATE OR REPLACE VIEW {cdm_view_dataset}.' + table_name + ' AS SELECT')
    result_sql.append(str_columns)
    result_sql.append('FROM {cdm_table_dataset}.' + table_name + ';')
    return '\n'.join(result_sql)

def fn_gen_sql(folder):
    MAP_FOLDER_GEN_FN = {
        FOLDER_DDL: gen_ddl_sql,
        FOLDER_VIEW: gen_view_sql
    }
    return MAP_FOLDER_GEN_FN[folder]