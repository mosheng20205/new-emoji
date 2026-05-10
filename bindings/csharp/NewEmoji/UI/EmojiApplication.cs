using NewEmoji.Native;

namespace NewEmoji;

public static class EmojiApplication
{
    public static int Run()
    {
        return NativeMethods.EU_RunMessageLoop();
    }
}
