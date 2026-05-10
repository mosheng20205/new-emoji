using NewEmoji.Runtime;

namespace NewEmoji.Native;

public static partial class NativeMethods
{
    static NativeMethods()
    {
        NewEmojiRuntime.EnsureLoaded();
    }
}
