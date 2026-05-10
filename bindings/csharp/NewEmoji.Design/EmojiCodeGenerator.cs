using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace NewEmoji.Design;

public sealed class EmojiCodeGenerator
{
    public string GenerateProgram(EmojiLayoutDocument document)
    {
        var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var handlers = new SortedSet<string>(StringComparer.Ordinal);
        var code = new StringBuilder();
        code.AppendLine("using System;");
        code.AppendLine("using System.Windows.Forms;");
        code.AppendLine("using NewEmoji;");
        code.AppendLine();
        code.AppendLine("namespace NewEmojiGeneratedApp");
        code.AppendLine("{");
        code.AppendLine("    internal static class Program");
        code.AppendLine("    {");
        code.AppendLine("        [STAThread]");
        code.AppendLine("        private static void Main()");
        code.AppendLine("        {");
        code.AppendLine("            Application.EnableVisualStyles();");
        code.AppendLine("            Application.SetCompatibleTextRenderingDefault(false);");
        code.AppendLine($"            var win = EmojiWindow.Create(\"{Escape(document.Window.Title)}\", {document.Window.Width}, {document.Window.Height}, titlebarColor: {ColorLiteral(document.Window.TitlebarColor)});");
        code.AppendLine("            win.Closing += (_, _) => Application.ExitThread();");
        GenerateElementCreation(code, document.Root, "win", null, names, handlers, 3);
        code.AppendLine("            win.Show();");
        code.AppendLine("            Application.Run();");
        code.AppendLine("        }");
        code.AppendLine();
        foreach (var handler in handlers)
        {
            code.AppendLine($"        private static void {handler}(object sender, EventArgs e)");
            code.AppendLine("        {");
            code.AppendLine("            // TODO: 在这里编写事件逻辑。");
            code.AppendLine("        }");
            code.AppendLine();
        }
        code.AppendLine("    }");
        code.AppendLine("}");
        return code.ToString();
    }

    public void ExportNet48Project(EmojiLayoutDocument document, string outputDirectory, string newEmojiProjectPath, string nativeDllPath)
    {
        Directory.CreateDirectory(outputDirectory);
        File.WriteAllText(Path.Combine(outputDirectory, "Program.cs"), GenerateProgram(document), Encoding.UTF8);
        File.WriteAllText(Path.Combine(outputDirectory, "GeneratedNewEmojiApp.csproj"), GenerateProject(outputDirectory, newEmojiProjectPath, nativeDllPath), Encoding.UTF8);
        EmojiLayoutSerializer.Save(Path.Combine(outputDirectory, "layout.json"), document);
    }

    private static string GenerateProject(string outputDirectory, string newEmojiProjectPath, string nativeDllPath)
    {
        var projectReference = MakeRelativePath(outputDirectory, newEmojiProjectPath);
        var nativeReference = MakeRelativePath(outputDirectory, nativeDllPath);
        return $@"<Project Sdk=""Microsoft.NET.Sdk"">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net48</TargetFramework>
    <UseWindowsForms>true</UseWindowsForms>
    <PlatformTarget>x64</PlatformTarget>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include=""{XmlEscape(projectReference)}"" />
    <None Include=""{XmlEscape(nativeReference)}"" Link=""new_emoji.dll"" CopyToOutputDirectory=""PreserveNewest"" />
  </ItemGroup>
</Project>
";
    }

    private static void GenerateElementCreation(
        StringBuilder code,
        EmojiElementDesign element,
        string windowVariable,
        string? parentVariable,
        HashSet<string> names,
        ISet<string> handlers,
        int indent)
    {
        var variable = UniqueIdentifier(element.Name, names);
        var prefix = new string(' ', indent * 4);
        var b = element.Bounds;

        if (parentVariable is null)
        {
            code.AppendLine($"{prefix}var {variable} = {windowVariable}.CreateContainer({b.X}, {b.Y}, {b.Width}, {b.Height});");
        }
        else if (string.Equals(element.Type, "Dialog", StringComparison.OrdinalIgnoreCase))
        {
            code.AppendLine($"{prefix}var {variable} = {windowVariable}.CreateDialog(\"{Escape(GetProperty(element, "title", element.Text))}\", \"{Escape(GetProperty(element, "body", "弹窗内容 ✅"))}\");");
        }
        else if (string.Equals(element.Type, "Drawer", StringComparison.OrdinalIgnoreCase))
        {
            code.AppendLine($"{prefix}var {variable} = {windowVariable}.CreateDrawer(\"{Escape(GetProperty(element, "title", element.Text))}\", \"{Escape(GetProperty(element, "body", "抽屉内容 ⚙️"))}\");");
        }
        else
        {
            code.AppendLine($"{prefix}var {variable} = {CreateExpression(parentVariable, element)};");
        }

        if (!element.Visible)
        {
            code.AppendLine($"{prefix}{variable}.Visible = false;");
        }

        if (!element.Enabled)
        {
            code.AppendLine($"{prefix}{variable}.Enabled = false;");
        }

        if (element.Events.TryGetValue("Clicked", out var handler) && IsIdentifier(handler))
        {
            handlers.Add(handler);
            code.AppendLine($"{prefix}{variable}.Clicked += {handler};");
        }

        foreach (var child in element.Children)
        {
            GenerateElementCreation(code, child, windowVariable, variable, names, handlers, indent);
        }
    }

    private static string CreateExpression(string parent, EmojiElementDesign element)
    {
        var b = element.Bounds;
        return element.Type switch
        {
            "Container" => $"{parent}.AddContainer({b.X}, {b.Y}, {b.Width}, {b.Height})",
            "Panel" => $"{parent}.AddPanel({b.X}, {b.Y}, {b.Width}, {b.Height})",
            "Text" => $"{parent}.AddText(\"{Escape(element.Text)}\", {b.X}, {b.Y}, {b.Width}, {b.Height})",
            "Button" => $"{parent}.AddButton(\"{Escape(element.Emoji)}\", \"{Escape(element.Text)}\", {b.X}, {b.Y}, {b.Width}, {b.Height})",
            "Input" => $"{parent}.AddInput(\"{Escape(element.Text)}\", \"{Escape(GetProperty(element, "placeholder"))}\", {b.X}, {b.Y}, {b.Width}, {b.Height})",
            "EditBox" => $"{parent}.AddEditBox({b.X}, {b.Y}, {b.Width}, {b.Height}, \"{Escape(element.Text)}\")",
            "Table" => $"{parent}.AddTable(\"{Escape(GetProperty(element, "columns", "名称,状态"))}\", \"{Escape(GetProperty(element, "rows", "示例,正常"))}\", {b.X}, {b.Y}, {b.Width}, {b.Height})",
            "Card" => $"{parent}.AddCard(\"{Escape(GetProperty(element, "title", element.Text))}\", \"{Escape(GetProperty(element, "body", "卡片内容 ✅"))}\", true, {b.X}, {b.Y}, {b.Width}, {b.Height})",
            "Tabs" => $"{parent}.AddTabs(\"{Escape(GetProperty(element, "items", "首页 🏠\\n设置 ⚙️"))}\", 0, 0, {b.X}, {b.Y}, {b.Width}, {b.Height})",
            "Notification" => $"{parent}.AddNotification(\"{Escape(GetProperty(element, "title", element.Text))}\", \"{Escape(GetProperty(element, "body", "通知内容 🔔"))}\", EmojiMessageType.Info, true, {b.X}, {b.Y}, {b.Width}, {b.Height})",
            _ => $"{parent}.AddPanel({b.X}, {b.Y}, {b.Width}, {b.Height})",
        };
    }

    private static string GetProperty(EmojiElementDesign element, string key, string fallback = "")
    {
        return element.Properties.TryGetValue(key, out var value) ? value : fallback;
    }

    private static string UniqueIdentifier(string value, HashSet<string> names)
    {
        var baseName = ToIdentifier(value);
        var name = baseName;
        var suffix = 2;
        while (!names.Add(name))
        {
            name = baseName + suffix++;
        }

        return name;
    }

    private static string ToIdentifier(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return "element";
        }

        var builder = new StringBuilder();
        foreach (var ch in value)
        {
            builder.Append(char.IsLetterOrDigit(ch) || ch == '_' ? ch : '_');
        }

        var result = builder.ToString().Trim('_');
        if (string.IsNullOrEmpty(result))
        {
            result = "element";
        }

        if (char.IsDigit(result[0]))
        {
            result = "_" + result;
        }

        return result;
    }

    private static bool IsIdentifier(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return false;
        }

        return value.All(ch => char.IsLetterOrDigit(ch) || ch == '_') && !char.IsDigit(value[0]);
    }

    private static string Escape(string value)
    {
        return (value ?? string.Empty).Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "\\r").Replace("\n", "\\n");
    }

    private static string ColorLiteral(string color)
    {
        if (string.IsNullOrWhiteSpace(color))
        {
            return "0xFF2D7DFF";
        }

        var trimmed = color.Trim().TrimStart('#');
        return "0x" + trimmed;
    }

    private static string MakeRelativePath(string fromDirectory, string toPath)
    {
        var fromUri = new Uri(AppendDirectorySeparator(Path.GetFullPath(fromDirectory)));
        var toUri = new Uri(Path.GetFullPath(toPath));
        return Uri.UnescapeDataString(fromUri.MakeRelativeUri(toUri).ToString()).Replace('/', Path.DirectorySeparatorChar);
    }

    private static string AppendDirectorySeparator(string path)
    {
        return path.EndsWith(Path.DirectorySeparatorChar.ToString(), StringComparison.Ordinal) ? path : path + Path.DirectorySeparatorChar;
    }

    private static string XmlEscape(string value)
    {
        return value.Replace("&", "&amp;").Replace("\"", "&quot;").Replace("<", "&lt;").Replace(">", "&gt;");
    }
}
