using System.IO;
using System.Runtime.Serialization.Json;
using System.Text;

namespace NewEmoji.Design;

public static class EmojiLayoutSerializer
{
    public static EmojiLayoutDocument Load(string path)
    {
        using var stream = File.OpenRead(path);
        var serializer = CreateSerializer();
        return (EmojiLayoutDocument?)serializer.ReadObject(stream) ?? EmojiLayoutDocument.CreateDefault();
    }

    public static void Save(string path, EmojiLayoutDocument document)
    {
        var directory = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        File.WriteAllText(path, ToJson(document), Encoding.UTF8);
    }

    public static string ToJson(EmojiLayoutDocument document)
    {
        using var stream = new MemoryStream();
        var serializer = CreateSerializer();
        serializer.WriteObject(stream, document);
        return Encoding.UTF8.GetString(stream.ToArray());
    }

    public static EmojiLayoutDocument FromJson(string json)
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(json ?? ""));
        var serializer = CreateSerializer();
        return (EmojiLayoutDocument?)serializer.ReadObject(stream) ?? EmojiLayoutDocument.CreateDefault();
    }

    private static DataContractJsonSerializer CreateSerializer()
    {
        return new DataContractJsonSerializer(
            typeof(EmojiLayoutDocument),
            new DataContractJsonSerializerSettings { UseSimpleDictionaryFormat = true });
    }
}
