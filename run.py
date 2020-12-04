from cdmlib import create_folders, create_file, gen_ddl_sql, \
    write_ddl_sql, write_view_sql, read_file

if __name__ == "__main__":
    print('Start generate SQLs:')
    create_folders()

    file_name = 'PhysicalModel.xlsm'
    sheets_file = read_file('test_sheets.txt')
    sheet_lines = sheets_file.readlines()

    # sheet_names = ['PARTY_REFERENCE', 'Party_relationship']
    for sheet_line in sheet_lines:
        sheet_name = sheet_line.strip()
        write_ddl_sql(file_name, sheet_name)
        write_view_sql(file_name, sheet_name)

    print('Done! All SQL generated.')
