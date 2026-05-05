#pragma once
#include <string>

class Table;

bool export_table_to_xlsx(const Table& table, const std::wstring& path, int flags);
bool import_table_from_xlsx(Table& table, const std::wstring& path, int flags);
