#include "utf8_helpers.h"

std::wstring utf8_to_wide(const unsigned char* bytes, int len) {
    if (!bytes || len <= 0) return L"";
    int wide_len = MultiByteToWideChar(CP_UTF8, 0, reinterpret_cast<LPCCH>(bytes), len, nullptr, 0);
    if (wide_len <= 0) return L"";
    std::wstring result(wide_len, L'\0');
    MultiByteToWideChar(CP_UTF8, 0, reinterpret_cast<LPCCH>(bytes), len, &result[0], wide_len);
    return result;
}

std::string wide_to_utf8(const std::wstring& wstr) {
    if (wstr.empty()) return "";
    int len = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), static_cast<int>(wstr.size()),
                                  nullptr, 0, nullptr, nullptr);
    if (len <= 0) return "";
    std::string result(len, '\0');
    WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), static_cast<int>(wstr.size()),
                        &result[0], len, nullptr, nullptr);
    return result;
}
