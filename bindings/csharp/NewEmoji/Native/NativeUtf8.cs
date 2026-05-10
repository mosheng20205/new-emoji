using System;
using System.Runtime.InteropServices;
using System.Text;

namespace NewEmoji.Native;

public static class NativeUtf8
{
    public static byte[] GetBytes(string? text)
    {
        return string.IsNullOrEmpty(text) ? Array.Empty<byte>() : Encoding.UTF8.GetBytes(text);
    }

    public static string FromPointer(IntPtr utf8, int len)
    {
        if (utf8 == IntPtr.Zero || len <= 0)
        {
            return string.Empty;
        }

        var bytes = new byte[len];
        Marshal.Copy(utf8, bytes, 0, len);
        return Encoding.UTF8.GetString(bytes);
    }

    public static string FromBuffer(Func<byte[], int, int> read, int initialSize = 256)
    {
        var size = Math.Max(1, initialSize);
        for (var attempt = 0; attempt < 6; attempt++)
        {
            var buffer = new byte[size];
            var written = read(buffer, buffer.Length);
            if (written <= 0)
            {
                return string.Empty;
            }

            if (written < buffer.Length)
            {
                return Encoding.UTF8.GetString(buffer, 0, written);
            }

            size = written + 1;
        }

        return string.Empty;
    }
}
