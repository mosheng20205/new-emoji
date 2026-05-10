namespace NewEmoji.Designer.WinForms48
{
    internal sealed class DesignerComponentItem
    {
        public DesignerComponentItem(string type, string label, int width, int height)
        {
            Type = type;
            Label = label;
            Width = width;
            Height = height;
        }

        public string Type { get; }
        public string Label { get; }
        public int Width { get; }
        public int Height { get; }

        public override string ToString()
        {
            return Label;
        }
    }
}
