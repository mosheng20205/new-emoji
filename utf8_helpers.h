#pragma once
#include <string>
#include <windows.h>

std::wstring utf8_to_wide(const unsigned char* bytes, int len);
std::string  wide_to_utf8(const std::wstring& wstr);
