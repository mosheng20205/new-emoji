using System.ComponentModel;
using NewEmoji.Design;

namespace NewEmoji.Designer.WinForms48
{
    internal sealed class EmojiElementEditor
    {
        public EmojiElementEditor(EmojiElementDesign element)
        {
            Element = element;
        }

        [Browsable(false)]
        public EmojiElementDesign Element { get; }

        [Category("基础")]
        [ReadOnly(true)]
        public string Type => Element.Type;

        [Category("基础")]
        [DisplayName("名称")]
        public string Name
        {
            get => Element.Name;
            set => Element.Name = value ?? "";
        }

        [Category("内容")]
        [DisplayName("文本")]
        public string Text
        {
            get => Element.Text;
            set => Element.Text = value ?? "";
        }

        [Category("内容")]
        [DisplayName("Emoji")]
        public string Emoji
        {
            get => Element.Emoji;
            set => Element.Emoji = value ?? "";
        }

        [Category("布局")]
        public int X
        {
            get => Element.Bounds.X;
            set => Element.Bounds.X = value;
        }

        [Category("布局")]
        public int Y
        {
            get => Element.Bounds.Y;
            set => Element.Bounds.Y = value;
        }

        [Category("布局")]
        [DisplayName("宽度")]
        public int Width
        {
            get => Element.Bounds.Width;
            set => Element.Bounds.Width = value;
        }

        [Category("布局")]
        [DisplayName("高度")]
        public int Height
        {
            get => Element.Bounds.Height;
            set => Element.Bounds.Height = value;
        }

        [Category("状态")]
        [DisplayName("可见")]
        public bool Visible
        {
            get => Element.Visible;
            set => Element.Visible = value;
        }

        [Category("状态")]
        [DisplayName("启用")]
        public bool Enabled
        {
            get => Element.Enabled;
            set => Element.Enabled = value;
        }

        [Category("组件属性")]
        [DisplayName("占位文本")]
        public string Placeholder
        {
            get => GetProperty("placeholder");
            set => SetProperty("placeholder", value);
        }

        [Category("组件属性")]
        [DisplayName("表格列")]
        public string Columns
        {
            get => GetProperty("columns");
            set => SetProperty("columns", value);
        }

        [Category("组件属性")]
        [DisplayName("表格行")]
        public string Rows
        {
            get => GetProperty("rows");
            set => SetProperty("rows", value);
        }

        [Category("组件属性")]
        [DisplayName("标签项")]
        public string Items
        {
            get => GetProperty("items");
            set => SetProperty("items", value);
        }

        [Category("组件属性")]
        [DisplayName("标题")]
        public string Title
        {
            get => GetProperty("title");
            set => SetProperty("title", value);
        }

        [Category("组件属性")]
        [DisplayName("正文")]
        public string Body
        {
            get => GetProperty("body");
            set => SetProperty("body", value);
        }

        [Category("事件")]
        [DisplayName("Clicked")]
        public string Clicked
        {
            get => Element.Events.TryGetValue("Clicked", out var value) ? value : "";
            set
            {
                if (string.IsNullOrWhiteSpace(value))
                {
                    Element.Events.Remove("Clicked");
                }
                else
                {
                    Element.Events["Clicked"] = value;
                }
            }
        }

        private string GetProperty(string key)
        {
            return Element.Properties.TryGetValue(key, out var value) ? value : "";
        }

        private void SetProperty(string key, string? value)
        {
            if (string.IsNullOrEmpty(value))
            {
                Element.Properties.Remove(key);
            }
            else
            {
                Element.Properties[key] = value ?? "";
            }
        }
    }
}
