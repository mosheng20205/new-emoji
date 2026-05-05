#include "xlsx_table_io.h"
#include "element_table.h"
#include "utf8_helpers.h"

#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <filesystem>
#include <map>
#include <utility>
#include <sstream>
#include <string>
#include <vector>

namespace {

struct ZipEntry {
    std::string name;
    std::vector<unsigned char> data;
    uint32_t crc = 0;
    uint32_t local_offset = 0;
};

static uint32_t crc32_bytes(const std::vector<unsigned char>& data) {
    static uint32_t table[256]{};
    static bool ready = false;
    if (!ready) {
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t c = i;
            for (int j = 0; j < 8; ++j) c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
            table[i] = c;
        }
        ready = true;
    }
    uint32_t c = 0xFFFFFFFFu;
    for (unsigned char b : data) c = table[(c ^ b) & 0xFF] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}

static void put16(std::vector<unsigned char>& out, uint16_t v) {
    out.push_back((unsigned char)(v & 0xFF));
    out.push_back((unsigned char)((v >> 8) & 0xFF));
}

static void put32(std::vector<unsigned char>& out, uint32_t v) {
    put16(out, (uint16_t)(v & 0xFFFF));
    put16(out, (uint16_t)((v >> 16) & 0xFFFF));
}

static uint16_t get16(const std::vector<unsigned char>& data, size_t pos) {
    if (pos + 2 > data.size()) return 0;
    return (uint16_t)data[pos] | ((uint16_t)data[pos + 1] << 8);
}

static uint32_t get32(const std::vector<unsigned char>& data, size_t pos) {
    return (uint32_t)get16(data, pos) | ((uint32_t)get16(data, pos + 2) << 16);
}

static std::vector<unsigned char> bytes(const std::string& s) {
    return std::vector<unsigned char>(s.begin(), s.end());
}

static bool write_zip(const std::wstring& path, std::vector<ZipEntry> entries) {
    std::vector<unsigned char> out;
    for (auto& e : entries) {
        e.crc = crc32_bytes(e.data);
        e.local_offset = (uint32_t)out.size();
        put32(out, 0x04034B50);
        put16(out, 20);
        put16(out, 0x0800); // UTF-8 filenames
        put16(out, 0);      // stored
        put16(out, 0);
        put16(out, 0);
        put32(out, e.crc);
        put32(out, (uint32_t)e.data.size());
        put32(out, (uint32_t)e.data.size());
        put16(out, (uint16_t)e.name.size());
        put16(out, 0);
        out.insert(out.end(), e.name.begin(), e.name.end());
        out.insert(out.end(), e.data.begin(), e.data.end());
    }

    uint32_t central_offset = (uint32_t)out.size();
    for (const auto& e : entries) {
        put32(out, 0x02014B50);
        put16(out, 20);
        put16(out, 20);
        put16(out, 0x0800);
        put16(out, 0);
        put16(out, 0);
        put16(out, 0);
        put32(out, e.crc);
        put32(out, (uint32_t)e.data.size());
        put32(out, (uint32_t)e.data.size());
        put16(out, (uint16_t)e.name.size());
        put16(out, 0);
        put16(out, 0);
        put16(out, 0);
        put16(out, 0);
        put32(out, 0);
        put32(out, e.local_offset);
        out.insert(out.end(), e.name.begin(), e.name.end());
    }
    uint32_t central_size = (uint32_t)out.size() - central_offset;
    put32(out, 0x06054B50);
    put16(out, 0);
    put16(out, 0);
    put16(out, (uint16_t)entries.size());
    put16(out, (uint16_t)entries.size());
    put32(out, central_size);
    put32(out, central_offset);
    put16(out, 0);

    std::ofstream file(std::filesystem::path(path), std::ios::binary);
    if (!file) return false;
    file.write((const char*)out.data(), (std::streamsize)out.size());
    return file.good();
}

static bool read_file(const std::wstring& path, std::vector<unsigned char>& out) {
    std::ifstream file(std::filesystem::path(path), std::ios::binary);
    if (!file) return false;
    file.seekg(0, std::ios::end);
    std::streamoff size = file.tellg();
    if (size <= 0) return false;
    file.seekg(0, std::ios::beg);
    out.resize((size_t)size);
    file.read((char*)out.data(), size);
    return file.good();
}

static bool read_zip_stored_entry(const std::wstring& path, const std::string& name, std::string& out) {
    std::vector<unsigned char> data;
    if (!read_file(path, data)) return false;
    size_t eocd = std::string::npos;
    size_t start = data.size() > 22 ? data.size() - 22 : 0;
    for (size_t pos = start + 1; pos > 0; --pos) {
        size_t i = pos - 1;
        if (get32(data, i) == 0x06054B50) { eocd = i; break; }
    }
    if (eocd == std::string::npos) return false;
    uint16_t count = get16(data, eocd + 10);
    uint32_t central = get32(data, eocd + 16);
    size_t pos = central;
    for (int i = 0; i < count && pos + 46 <= data.size(); ++i) {
        if (get32(data, pos) != 0x02014B50) return false;
        uint16_t method = get16(data, pos + 10);
        uint32_t comp_size = get32(data, pos + 20);
        uint16_t name_len = get16(data, pos + 28);
        uint16_t extra_len = get16(data, pos + 30);
        uint16_t comment_len = get16(data, pos + 32);
        uint32_t local = get32(data, pos + 42);
        std::string entry_name((const char*)data.data() + pos + 46, name_len);
        if (entry_name == name) {
            if (method != 0) return false;
            if (local + 30 > data.size() || get32(data, local) != 0x04034B50) return false;
            uint16_t lf_name = get16(data, local + 26);
            uint16_t lf_extra = get16(data, local + 28);
            size_t start = local + 30 + lf_name + lf_extra;
            if (start + comp_size > data.size()) return false;
            out.assign((const char*)data.data() + start, (size_t)comp_size);
            return true;
        }
        pos += 46 + name_len + extra_len + comment_len;
    }
    return false;
}

static std::string xml_escape_utf8(const std::wstring& w) {
    std::string s = wide_to_utf8(w);
    std::string out;
    out.reserve(s.size());
    for (char ch : s) {
        if (ch == '&') out += "&amp;";
        else if (ch == '<') out += "&lt;";
        else if (ch == '>') out += "&gt;";
        else if (ch == '"') out += "&quot;";
        else out.push_back(ch);
    }
    return out;
}

static std::wstring xml_unescape_wide(std::string s) {
    auto repl = [&](const std::string& a, const std::string& b) {
        size_t pos = 0;
        while ((pos = s.find(a, pos)) != std::string::npos) {
            s.replace(pos, a.size(), b);
            pos += b.size();
        }
    };
    repl("&quot;", "\"");
    repl("&apos;", "'");
    repl("&lt;", "<");
    repl("&gt;", ">");
    repl("&amp;", "&");
    return utf8_to_wide((const unsigned char*)s.data(), (int)s.size());
}

static std::wstring cell_display_value(const TableCell& cell) {
    if ((cell.kind == TableCellKind::Combo || cell.kind == TableCellKind::Select ||
         cell.kind == TableCellKind::Buttons) && !cell.parts.empty()) {
        if (cell.kind == TableCellKind::Buttons) {
            std::wstring out;
            for (size_t i = 0; i < cell.parts.size(); ++i) {
                if (i) out += L" / ";
                out += cell.parts[i];
            }
            return out;
        }
        return cell.value.empty() ? cell.parts.front() : cell.value;
    }
    if (cell.kind == TableCellKind::Switch || cell.kind == TableCellKind::Selection) {
        return cell.checked ? L"1" : (cell.value.empty() ? L"0" : cell.value);
    }
    return cell.value;
}

static std::string col_name(int index) {
    std::string out;
    int n = index + 1;
    while (n > 0) {
        int rem = (n - 1) % 26;
        out.insert(out.begin(), (char)('A' + rem));
        n = (n - 1) / 26;
    }
    return out;
}

static int col_index_from_ref(const std::string& ref) {
    int col = 0;
    bool any = false;
    for (char ch : ref) {
        if (ch >= 'a' && ch <= 'z') ch = (char)(ch - 'a' + 'A');
        if (ch < 'A' || ch > 'Z') break;
        any = true;
        col = col * 26 + (ch - 'A' + 1);
    }
    return any ? col - 1 : -1;
}

static std::string inline_cell(int row, int col, const std::wstring& value) {
    std::ostringstream ss;
    ss << "<c r=\"" << col_name(col) << row << "\" t=\"inlineStr\"><is><t xml:space=\"preserve\">"
       << xml_escape_utf8(value) << "</t></is></c>";
    return ss.str();
}

static std::string escape_protocol(const std::wstring& w) {
    std::wstring out;
    for (wchar_t ch : w) {
        if (ch == L'\\' || ch == L'\t' || ch == L'\n' || ch == L'=' || ch == L'|') out.push_back(L'\\');
        if (ch == L'\t') out += L't';
        else if (ch == L'\n') out += L'n';
        else out.push_back(ch);
    }
    return wide_to_utf8(out);
}

static std::string attr(const std::string& tag, const std::string& name) {
    std::string key = name + "=\"";
    size_t start = tag.find(key);
    if (start == std::string::npos) return "";
    start += key.size();
    size_t end = tag.find('"', start);
    if (end == std::string::npos) return "";
    return tag.substr(start, end - start);
}

static std::vector<std::wstring> parse_shared_strings(const std::wstring& path) {
    std::string xml;
    std::vector<std::wstring> out;
    if (!read_zip_stored_entry(path, "xl/sharedStrings.xml", xml)) return out;
    size_t pos = 0;
    while ((pos = xml.find("<si", pos)) != std::string::npos) {
        size_t end = xml.find("</si>", pos);
        if (end == std::string::npos) break;
        std::string chunk = xml.substr(pos, end - pos);
        std::string text;
        size_t tp = 0;
        while ((tp = chunk.find("<t", tp)) != std::string::npos) {
            size_t close = chunk.find('>', tp);
            size_t te = chunk.find("</t>", close);
            if (close == std::string::npos || te == std::string::npos) break;
            text += chunk.substr(close + 1, te - close - 1);
            tp = te + 4;
        }
        out.push_back(xml_unescape_wide(text));
        pos = end + 5;
    }
    return out;
}

static std::wstring parse_cell_text(const std::string& cell, const std::vector<std::wstring>& shared) {
    std::string type = attr(cell.substr(0, cell.find('>') + 1), "t");
    if (type == "inlineStr") {
        size_t ts = cell.find("<t");
        if (ts == std::string::npos) return L"";
        size_t close = cell.find('>', ts);
        size_t te = cell.find("</t>", close);
        if (close == std::string::npos || te == std::string::npos) return L"";
        return xml_unescape_wide(cell.substr(close + 1, te - close - 1));
    }
    size_t vs = cell.find("<v>");
    size_t ve = cell.find("</v>", vs);
    if (vs == std::string::npos || ve == std::string::npos) return L"";
    std::string raw = cell.substr(vs + 3, ve - vs - 3);
    if (type == "s") {
        int idx = atoi(raw.c_str());
        if (idx >= 0 && idx < (int)shared.size()) return shared[idx];
        return L"";
    }
    return xml_unescape_wide(raw);
}

static bool parse_sheet_rows(const std::wstring& path, std::vector<std::vector<std::wstring>>& rows,
                             std::vector<std::pair<int, int>>& first_row_merges) {
    std::string xml;
    if (!read_zip_stored_entry(path, "xl/worksheets/sheet1.xml", xml)) return false;
    auto shared = parse_shared_strings(path);
    size_t pos = 0;
    while ((pos = xml.find("<row", pos)) != std::string::npos) {
        size_t row_end = xml.find("</row>", pos);
        if (row_end == std::string::npos) break;
        std::string row_xml = xml.substr(pos, row_end - pos);
        std::vector<std::wstring> row;
        size_t cp = 0;
        while ((cp = row_xml.find("<c", cp)) != std::string::npos) {
            size_t tag_end = row_xml.find('>', cp);
            size_t ce = row_xml.find("</c>", cp);
            if (tag_end == std::string::npos || ce == std::string::npos) break;
            std::string tag = row_xml.substr(cp, tag_end - cp + 1);
            std::string cell_xml = row_xml.substr(cp, ce - cp + 4);
            int col = col_index_from_ref(attr(tag, "r"));
            if (col < 0) col = (int)row.size();
            if ((int)row.size() <= col) row.resize(col + 1);
            row[col] = parse_cell_text(cell_xml, shared);
            cp = ce + 4;
        }
        rows.push_back(row);
        pos = row_end + 6;
    }
    size_t mp = 0;
    while ((mp = xml.find("<mergeCell", mp)) != std::string::npos) {
        size_t tag_end = xml.find("/>", mp);
        if (tag_end == std::string::npos) break;
        std::string tag = xml.substr(mp, tag_end - mp + 2);
        std::string ref = attr(tag, "ref");
        size_t colon = ref.find(':');
        if (colon != std::string::npos && ref.find('1') != std::string::npos) {
            int a = col_index_from_ref(ref.substr(0, colon));
            int b = col_index_from_ref(ref.substr(colon + 1));
            if (a >= 0 && b >= a) first_row_merges.push_back({ a, b });
        }
        mp = tag_end + 2;
    }
    return !rows.empty();
}

} // namespace

bool export_table_to_xlsx(const Table& table, const std::wstring& path, int) {
    if (table.adv_columns.empty()) return false;
    bool grouped = false;
    for (const auto& col : table.adv_columns) if (!col.parent_title.empty()) grouped = true;
    int header_rows = grouped ? 2 : 1;
    int rows_count = table.row_count();
    int cols_count = (int)table.adv_columns.size();
    std::vector<std::string> merges;

    std::ostringstream sheet;
    sheet << "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
          << "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
          << "<dimension ref=\"A1:" << col_name((std::max)(0, cols_count - 1)) << (header_rows + rows_count) << "\"/>"
          << "<sheetViews><sheetView workbookViewId=\"0\"/></sheetViews><sheetFormatPr defaultRowHeight=\"18\"/>"
          << "<cols>";
    for (int c = 0; c < cols_count; ++c) {
        int width = table.adv_columns[c].width > 0 ? table.adv_columns[c].width : table.adv_columns[c].min_width;
        sheet << "<col min=\"" << (c + 1) << "\" max=\"" << (c + 1) << "\" width=\""
              << (std::max)(8, width / 7) << "\" customWidth=\"1\"/>";
    }
    sheet << "</cols><sheetData>";
    if (grouped) {
        sheet << "<row r=\"1\">";
        int c = 0;
        while (c < cols_count) {
            std::wstring parent = table.adv_columns[c].parent_title;
            int start = c;
            int end = c + 1;
            if (!parent.empty()) {
                while (end < cols_count && table.adv_columns[end].parent_title == parent) ++end;
            }
            sheet << inline_cell(1, start, parent);
            if (!parent.empty() && end - start > 1) {
                merges.push_back(col_name(start) + "1:" + col_name(end - 1) + "1");
            }
            c = end;
        }
        sheet << "</row><row r=\"2\">";
        for (int i = 0; i < cols_count; ++i) sheet << inline_cell(2, i, table.adv_columns[i].title);
        sheet << "</row>";
    } else {
        sheet << "<row r=\"1\">";
        for (int i = 0; i < cols_count; ++i) sheet << inline_cell(1, i, table.adv_columns[i].title);
        sheet << "</row>";
    }

    for (int r = 0; r < rows_count; ++r) {
        const TableRow* row = table.row_ptr(r);
        if (!row) continue;
        int excel_row = header_rows + r + 1;
        sheet << "<row r=\"" << excel_row << "\">";
        for (int c = 0; c < cols_count; ++c) {
            std::wstring value;
            if (c < (int)row->cells.size()) value = cell_display_value(row->cells[c]);
            sheet << inline_cell(excel_row, c, value);
        }
        sheet << "</row>";
    }
    sheet << "</sheetData>";
    if (!merges.empty()) {
        sheet << "<mergeCells count=\"" << merges.size() << "\">";
        for (const auto& m : merges) sheet << "<mergeCell ref=\"" << m << "\"/>";
        sheet << "</mergeCells>";
    }
    sheet << "<pageMargins left=\"0.7\" right=\"0.7\" top=\"0.75\" bottom=\"0.75\" header=\"0.3\" footer=\"0.3\"/>"
          << "</worksheet>";

    std::vector<ZipEntry> entries = {
        { "[Content_Types].xml", bytes("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/><Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/><Override PartName=\"/docProps/core.xml\" ContentType=\"application/vnd.openxmlformats-package.core-properties+xml\"/><Override PartName=\"/docProps/app.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.extended-properties+xml\"/></Types>") },
        { "_rels/.rels", bytes("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/><Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties\" Target=\"docProps/core.xml\"/><Relationship Id=\"rId3\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties\" Target=\"docProps/app.xml\"/></Relationships>") },
        { "docProps/app.xml", bytes("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Properties xmlns=\"http://schemas.openxmlformats.org/officeDocument/2006/extended-properties\" xmlns:vt=\"http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes\"><Application>new_emoji</Application></Properties>") },
        { "docProps/core.xml", bytes("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><cp:coreProperties xmlns:cp=\"http://schemas.openxmlformats.org/package/2006/metadata/core-properties\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\"><dc:creator>new_emoji</dc:creator></cp:coreProperties>") },
        { "xl/workbook.xml", bytes("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"Table\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>") },
        { "xl/_rels/workbook.xml.rels", bytes("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/></Relationships>") },
        { "xl/worksheets/sheet1.xml", bytes(sheet.str()) }
    };
    return write_zip(path, entries);
}

bool import_table_from_xlsx(Table& table, const std::wstring& path, int) {
    std::vector<std::vector<std::wstring>> rows;
    std::vector<std::pair<int, int>> merges;
    if (!parse_sheet_rows(path, rows, merges)) return false;
    bool grouped = rows.size() >= 2 && (!merges.empty());
    int header_row = grouped ? 1 : 0;
    if (header_row >= (int)rows.size()) return false;
    int cols = 0;
    for (const auto& row : rows) cols = (std::max)(cols, (int)row.size());
    if (cols <= 0) return false;

    std::vector<std::wstring> parents((size_t)cols);
    if (grouped) {
        for (int c = 0; c < cols && c < (int)rows[0].size(); ++c) parents[c] = rows[0][c];
        for (auto [a, b] : merges) {
            std::wstring p = (a < (int)rows[0].size()) ? rows[0][a] : L"";
            for (int c = a; c <= b && c < cols; ++c) parents[c] = p;
        }
    }

    std::string col_spec;
    for (int c = 0; c < cols; ++c) {
        std::wstring title = (c < (int)rows[header_row].size() && !rows[header_row][c].empty())
            ? rows[header_row][c] : (L"列" + std::to_wstring(c + 1));
        if (!col_spec.empty()) col_spec.push_back('\n');
        col_spec += "title=" + escape_protocol(title) + "\tkey=c" + std::to_string(c) + "\twidth=120";
        if (grouped && !parents[c].empty()) col_spec += "\tparent=" + escape_protocol(parents[c]);
    }

    std::string row_spec;
    for (int r = header_row + 1; r < (int)rows.size(); ++r) {
        if (!row_spec.empty()) row_spec.push_back('\n');
        row_spec += "key=x" + std::to_string(r - header_row - 1);
        for (int c = 0; c < cols; ++c) {
            std::wstring value = c < (int)rows[r].size() ? rows[r][c] : L"";
            row_spec += "\tc" + std::to_string(c) + "=" + escape_protocol(value);
        }
    }
    table.set_columns_ex(utf8_to_wide((const unsigned char*)col_spec.data(), (int)col_spec.size()));
    table.set_rows_ex(utf8_to_wide((const unsigned char*)row_spec.data(), (int)row_spec.size()));
    table.clamp_scroll();
    table.invalidate();
    return true;
}
