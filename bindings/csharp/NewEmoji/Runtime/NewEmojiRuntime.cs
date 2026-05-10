using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using NewEmoji.Native;

namespace NewEmoji.Runtime;

public static class NewEmojiRuntime
{
    private static readonly object SyncRoot = new();
#if !NETFRAMEWORK
    private static bool s_resolverRegistered;
#endif
    private static IntPtr s_handle;
    private static string? s_loadedPath;

    public static string? LoadedPath
    {
        get
        {
            EnsureLoaded();
            return s_loadedPath;
        }
    }

    public static void EnsureLoaded()
    {
        if (s_handle != IntPtr.Zero)
        {
            return;
        }

        lock (SyncRoot)
        {
            if (s_handle != IntPtr.Zero)
            {
                return;
            }

            RegisterResolver();
            var errors = new List<string>();
            foreach (var candidate in GetCandidatePaths())
            {
                if (!File.Exists(candidate))
                {
                    continue;
                }

                try
                {
#if NETFRAMEWORK
                    var directory = Path.GetDirectoryName(candidate);
                    if (!string.IsNullOrEmpty(directory))
                    {
                        SetDllDirectoryW(directory);
                    }

                    s_handle = LoadLibraryW(candidate);
                    if (s_handle == IntPtr.Zero)
                    {
                        var error = Marshal.GetLastWin32Error();
                        errors.Add($"{candidate}: LoadLibraryW 失败，Win32Error={error}");
                        continue;
                    }
#else
                    s_handle = NativeLibrary.Load(candidate);
#endif
                    s_loadedPath = candidate;
                    return;
                }
                catch (BadImageFormatException ex)
                {
                    errors.Add($"{candidate}: DLL 位数与当前进程不一致。{ex.Message}");
                }
                catch (Exception ex) when (ex is DllNotFoundException or FileLoadException)
                {
                    errors.Add($"{candidate}: {ex.Message}");
                }
            }

            var arch = Environment.Is64BitProcess ? "x64" : "Win32";
            var detail = errors.Count == 0 ? "未找到可加载的 new_emoji.dll。" : string.Join(Environment.NewLine, errors);
            throw new DllNotFoundException($"无法加载 new_emoji.dll。当前进程需要 {arch} DLL。{Environment.NewLine}{detail}");
        }
    }

    private static void RegisterResolver()
    {
#if NETFRAMEWORK
        return;
#else
        if (s_resolverRegistered)
        {
            return;
        }

        NativeLibrary.SetDllImportResolver(
            typeof(NativeMethods).Assembly,
            (libraryName, assembly, searchPath) =>
            {
                if (!string.Equals(libraryName, NativeMethods.DllName, StringComparison.OrdinalIgnoreCase)
                    && !string.Equals(libraryName, "new_emoji", StringComparison.OrdinalIgnoreCase))
                {
                    return IntPtr.Zero;
                }

                EnsureLoaded();
                return s_handle;
            });
        s_resolverRegistered = true;
#endif
    }

    private static IEnumerable<string> GetCandidatePaths()
    {
        var archFolder = Environment.Is64BitProcess ? "win-x64" : "win-x86";
        var buildArch = Environment.Is64BitProcess ? "x64" : "Win32";
        var fileName = NativeMethods.DllName;
        var envPath = Environment.GetEnvironmentVariable("NEW_EMOJI_DLL_PATH");
        if (!string.IsNullOrWhiteSpace(envPath))
        {
            yield return Path.GetFullPath(envPath);
        }

        foreach (var baseDir in GetBaseDirectories())
        {
            yield return Path.Combine(baseDir, fileName);
            yield return Path.Combine(baseDir, "runtimes", archFolder, "native", fileName);
            yield return Path.Combine(baseDir, buildArch, fileName);
        }

        foreach (var baseDir in GetBaseDirectories())
        {
            var current = new DirectoryInfo(baseDir);
            while (current is not null)
            {
                yield return Path.Combine(current.FullName, "bin", buildArch, "Release", fileName);
                current = current.Parent;
            }
        }
    }

    private static IEnumerable<string> GetBaseDirectories()
    {
        yield return AppContext.BaseDirectory;

        var assemblyLocation = Assembly.GetExecutingAssembly().Location;
        if (!string.IsNullOrEmpty(assemblyLocation))
        {
            var assemblyDir = Path.GetDirectoryName(assemblyLocation);
            if (!string.IsNullOrEmpty(assemblyDir))
            {
                yield return assemblyDir;
            }
        }

        yield return Environment.CurrentDirectory;
    }

#if NETFRAMEWORK
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr LoadLibraryW(string lpFileName);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool SetDllDirectoryW(string lpPathName);
#endif
}
