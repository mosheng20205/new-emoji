using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using NewEmoji.Design;

namespace NewEmoji.Designer.WinForms48
{
    internal enum DesignerAlignCommand
    {
        Left,
        Right,
        Top,
        Bottom,
        HorizontalCenter,
        VerticalCenter,
        SameWidth,
        SameHeight,
    }

    internal sealed class DesignerCanvas : Panel
    {
        private readonly List<EmojiElementDesign> _selection = new();
        private readonly List<EmojiElementDesign> _localClipboard = new();
        private readonly Stack<string> _undo = new();
        private readonly Stack<string> _redo = new();
        private EmojiLayoutDocument _document = EmojiLayoutDocument.CreateDefault();
        private EmojiElementDesign? _selected;
        private string _checkpoint = "";
        private Point _lastPoint;
        private bool _dragging;
        private bool _resizing;
        private bool _interactionChanged;

        public DesignerCanvas()
        {
            DoubleBuffered = true;
            BackColor = Color.FromArgb(245, 247, 250);
            AllowDrop = true;
            TabStop = true;
            ResetHistory();
        }

        public EmojiLayoutDocument Document
        {
            get => _document;
            set
            {
                _document = value ?? EmojiLayoutDocument.CreateDefault();
                ClearSelection();
                ResetHistory();
                ElementsChanged?.Invoke(this, EventArgs.Empty);
                Invalidate();
            }
        }

        public EmojiElementDesign? SelectedElement => _selected;

        public IReadOnlyList<EmojiElementDesign> SelectedElements => _selection.AsReadOnly();

        public bool CanUndo => _undo.Count > 0;

        public bool CanRedo => _redo.Count > 0;

        public event EventHandler? SelectedElementChanged;

        public event EventHandler? ElementsChanged;

        public void SelectElement(EmojiElementDesign? element)
        {
            _selection.Clear();
            if (element is not null && _document.Root.Children.Contains(element))
            {
                _selection.Add(element);
            }

            _selected = _selection.LastOrDefault();
            SelectedElementChanged?.Invoke(this, EventArgs.Empty);
            Invalidate();
        }

        public void SelectAll()
        {
            _selection.Clear();
            _selection.AddRange(_document.Root.Children);
            _selected = _selection.LastOrDefault();
            SelectedElementChanged?.Invoke(this, EventArgs.Empty);
            Invalidate();
        }

        public void AddElement(string type, Point location)
        {
            var item = DefaultsFor(type);
            item.Name = UniqueName(item.Name);
            item.Bounds.X = Math.Max(0, location.X);
            item.Bounds.Y = Math.Max(0, location.Y);
            _document.Root.Children.Add(item);
            SelectElement(item);
            RecordDocumentChange();
        }

        public void DeleteSelected()
        {
            if (_selection.Count == 0)
            {
                return;
            }

            foreach (var element in _selection.ToArray())
            {
                _document.Root.Children.Remove(element);
            }

            ClearSelection();
            RecordDocumentChange();
        }

        public void CopySelected()
        {
            if (_selection.Count == 0)
            {
                return;
            }

            _localClipboard.Clear();
            _localClipboard.AddRange(OrderedSelection().Select(CloneElement));

            var clipDocument = new EmojiLayoutDocument
            {
                Window = _document.Window,
                Root = EmojiElementDesign.CreateRoot(),
            };
            foreach (var element in _localClipboard)
            {
                clipDocument.Root.Children.Add(CloneElement(element));
            }

            try
            {
                Clipboard.SetText(EmojiLayoutSerializer.ToJson(clipDocument));
            }
            catch
            {
                // 剪贴板可能被其他程序占用，本地副本仍可用于同一设计器内粘贴。
            }
        }

        public void PasteClipboard()
        {
            var items = TryReadClipboardElements();
            if (items.Count == 0)
            {
                items.AddRange(_localClipboard.Select(CloneElement));
            }

            InsertClones(items, 20);
        }

        public void DuplicateSelected()
        {
            if (_selection.Count == 0)
            {
                return;
            }

            InsertClones(OrderedSelection().Select(CloneElement).ToList(), 18);
        }

        public void MoveSelected(int dx, int dy)
        {
            if (_selection.Count == 0)
            {
                return;
            }

            MoveSelectionBy(dx, dy);
            RecordDocumentChange();
            SelectedElementChanged?.Invoke(this, EventArgs.Empty);
            Invalidate();
        }

        public void AlignSelected(DesignerAlignCommand command)
        {
            if (_selection.Count < 2 || _selected is null)
            {
                return;
            }

            var anchor = _selected.Bounds;
            foreach (var element in _selection)
            {
                if (ReferenceEquals(element, _selected))
                {
                    continue;
                }

                switch (command)
                {
                    case DesignerAlignCommand.Left:
                        element.Bounds.X = anchor.X;
                        break;
                    case DesignerAlignCommand.Right:
                        element.Bounds.X = anchor.X + anchor.Width - element.Bounds.Width;
                        break;
                    case DesignerAlignCommand.Top:
                        element.Bounds.Y = anchor.Y;
                        break;
                    case DesignerAlignCommand.Bottom:
                        element.Bounds.Y = anchor.Y + anchor.Height - element.Bounds.Height;
                        break;
                    case DesignerAlignCommand.HorizontalCenter:
                        element.Bounds.X = anchor.X + (anchor.Width - element.Bounds.Width) / 2;
                        break;
                    case DesignerAlignCommand.VerticalCenter:
                        element.Bounds.Y = anchor.Y + (anchor.Height - element.Bounds.Height) / 2;
                        break;
                    case DesignerAlignCommand.SameWidth:
                        element.Bounds.Width = anchor.Width;
                        break;
                    case DesignerAlignCommand.SameHeight:
                        element.Bounds.Height = anchor.Height;
                        break;
                }
            }

            RecordDocumentChange();
            SelectedElementChanged?.Invoke(this, EventArgs.Empty);
            Invalidate();
        }

        public void Undo()
        {
            if (_undo.Count == 0)
            {
                return;
            }

            var current = SerializeDocument();
            var previous = _undo.Pop();
            _redo.Push(current);
            RestoreDocument(previous);
            _checkpoint = previous;
        }

        public void Redo()
        {
            if (_redo.Count == 0)
            {
                return;
            }

            var current = SerializeDocument();
            var next = _redo.Pop();
            _undo.Push(current);
            RestoreDocument(next);
            _checkpoint = next;
        }

        public void RecordDocumentChange()
        {
            var current = SerializeDocument();
            if (string.Equals(current, _checkpoint, StringComparison.Ordinal))
            {
                return;
            }

            _undo.Push(_checkpoint);
            _redo.Clear();
            _checkpoint = current;
            ElementsChanged?.Invoke(this, EventArgs.Empty);
        }

        protected override void OnDragEnter(DragEventArgs drgevent)
        {
            if (drgevent.Data?.GetDataPresent(typeof(DesignerComponentItem)) == true)
            {
                drgevent.Effect = DragDropEffects.Copy;
            }
            base.OnDragEnter(drgevent);
        }

        protected override void OnDragDrop(DragEventArgs drgevent)
        {
            if (drgevent.Data?.GetData(typeof(DesignerComponentItem)) is DesignerComponentItem item)
            {
                var point = PointToClient(new Point(drgevent.X, drgevent.Y));
                AddElement(item.Type, point);
            }
            base.OnDragDrop(drgevent);
        }

        protected override void OnMouseDown(MouseEventArgs e)
        {
            Focus();
            var hit = HitTest(e.Location);
            var multi = (ModifierKeys & (Keys.Control | Keys.Shift)) != 0;
            if (hit is not null && multi)
            {
                ToggleSelection(hit);
                _dragging = false;
                _resizing = false;
                base.OnMouseDown(e);
                return;
            }

            if (hit is null)
            {
                if (!multi)
                {
                    ClearSelection();
                }
            }
            else if (!_selection.Contains(hit))
            {
                SelectElement(hit);
            }
            else
            {
                _selected = hit;
                SelectedElementChanged?.Invoke(this, EventArgs.Empty);
            }

            _lastPoint = e.Location;
            _dragging = hit is not null;
            _resizing = hit is not null && ReferenceEquals(hit, _selected) && IsResizeHandle(hit, e.Location);
            _interactionChanged = false;
            base.OnMouseDown(e);
        }

        protected override void OnMouseMove(MouseEventArgs e)
        {
            Cursor = SelectedElement is not null && IsResizeHandle(SelectedElement, e.Location) ? Cursors.SizeNWSE : Cursors.Default;
            if (_selected is not null && _dragging && e.Button == MouseButtons.Left)
            {
                var dx = e.X - _lastPoint.X;
                var dy = e.Y - _lastPoint.Y;
                if (dx == 0 && dy == 0)
                {
                    base.OnMouseMove(e);
                    return;
                }

                if (_resizing)
                {
                    _selected.Bounds.Width = Math.Max(24, _selected.Bounds.Width + dx);
                    _selected.Bounds.Height = Math.Max(20, _selected.Bounds.Height + dy);
                }
                else
                {
                    MoveSelectionBy(dx, dy);
                }

                _interactionChanged = true;
                _lastPoint = e.Location;
                SelectedElementChanged?.Invoke(this, EventArgs.Empty);
                Invalidate();
            }
            base.OnMouseMove(e);
        }

        protected override void OnMouseUp(MouseEventArgs e)
        {
            if (_interactionChanged)
            {
                RecordDocumentChange();
            }

            _dragging = false;
            _resizing = false;
            _interactionChanged = false;
            base.OnMouseUp(e);
        }

        protected override bool ProcessCmdKey(ref Message msg, Keys keyData)
        {
            var keyCode = keyData & Keys.KeyCode;
            var control = (keyData & Keys.Control) == Keys.Control;
            var shift = (keyData & Keys.Shift) == Keys.Shift;
            var step = shift ? 10 : 1;

            if (control && keyCode == Keys.Z)
            {
                if (shift)
                {
                    Redo();
                }
                else
                {
                    Undo();
                }
                return true;
            }

            if (control && keyCode == Keys.Y)
            {
                Redo();
                return true;
            }

            if (control && keyCode == Keys.A)
            {
                SelectAll();
                return true;
            }

            if (control && keyCode == Keys.C)
            {
                CopySelected();
                return true;
            }

            if (control && keyCode == Keys.V)
            {
                PasteClipboard();
                return true;
            }

            if (control && keyCode == Keys.D)
            {
                DuplicateSelected();
                return true;
            }

            if (keyCode == Keys.Delete)
            {
                DeleteSelected();
                return true;
            }

            if (keyCode == Keys.Left)
            {
                MoveSelected(-step, 0);
                return true;
            }

            if (keyCode == Keys.Right)
            {
                MoveSelected(step, 0);
                return true;
            }

            if (keyCode == Keys.Up)
            {
                MoveSelected(0, -step);
                return true;
            }

            if (keyCode == Keys.Down)
            {
                MoveSelected(0, step);
                return true;
            }

            return base.ProcessCmdKey(ref msg, keyData);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            e.Graphics.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;
            DrawRoot(e.Graphics);
            foreach (var child in _document.Root.Children)
            {
                DrawElement(e.Graphics, child);
            }
        }

        private void ToggleSelection(EmojiElementDesign element)
        {
            if (_selection.Contains(element))
            {
                _selection.Remove(element);
                _selected = _selection.LastOrDefault();
            }
            else
            {
                _selection.Add(element);
                _selected = element;
            }

            SelectedElementChanged?.Invoke(this, EventArgs.Empty);
            Invalidate();
        }

        private void ClearSelection()
        {
            _selection.Clear();
            _selected = null;
            SelectedElementChanged?.Invoke(this, EventArgs.Empty);
            Invalidate();
        }

        private void MoveSelectionBy(int dx, int dy)
        {
            foreach (var element in _selection)
            {
                element.Bounds.X = Math.Max(0, element.Bounds.X + dx);
                element.Bounds.Y = Math.Max(0, element.Bounds.Y + dy);
            }
        }

        private void InsertClones(IList<EmojiElementDesign> items, int offset)
        {
            if (items.Count == 0)
            {
                return;
            }

            var inserted = new List<EmojiElementDesign>();
            foreach (var item in items)
            {
                item.Name = UniqueName(item.Name);
                item.Bounds.X = Math.Max(0, item.Bounds.X + offset);
                item.Bounds.Y = Math.Max(0, item.Bounds.Y + offset);
                _document.Root.Children.Add(item);
                inserted.Add(item);
            }

            _selection.Clear();
            _selection.AddRange(inserted);
            _selected = inserted.LastOrDefault();
            SelectedElementChanged?.Invoke(this, EventArgs.Empty);
            RecordDocumentChange();
            Invalidate();
        }

        private List<EmojiElementDesign> TryReadClipboardElements()
        {
            try
            {
                if (!Clipboard.ContainsText())
                {
                    return new List<EmojiElementDesign>();
                }

                var document = EmojiLayoutSerializer.FromJson(Clipboard.GetText());
                return document.Root.Children.Select(CloneElement).ToList();
            }
            catch
            {
                return new List<EmojiElementDesign>();
            }
        }

        private IEnumerable<EmojiElementDesign> OrderedSelection()
        {
            return _document.Root.Children.Where(child => _selection.Contains(child));
        }

        private string UniqueName(string baseName)
        {
            var seed = string.IsNullOrWhiteSpace(baseName) ? "element" : baseName.Trim();
            var names = new HashSet<string>(_document.Root.Children.Select(child => child.Name), StringComparer.OrdinalIgnoreCase);
            if (!names.Contains(seed))
            {
                return seed;
            }

            var suffix = 2;
            while (names.Contains(seed + suffix))
            {
                suffix++;
            }

            return seed + suffix;
        }

        private void ResetHistory()
        {
            _undo.Clear();
            _redo.Clear();
            _checkpoint = SerializeDocument();
        }

        private string SerializeDocument()
        {
            return EmojiLayoutSerializer.ToJson(_document);
        }

        private void RestoreDocument(string json)
        {
            _document = EmojiLayoutSerializer.FromJson(json);
            ClearSelection();
            ElementsChanged?.Invoke(this, EventArgs.Empty);
            Invalidate();
        }

        private static EmojiElementDesign CloneElement(EmojiElementDesign source)
        {
            var clone = new EmojiElementDesign
            {
                Type = source.Type,
                Name = source.Name,
                Text = source.Text,
                Emoji = source.Emoji,
                Visible = source.Visible,
                Enabled = source.Enabled,
                Bounds = new EmojiBounds(source.Bounds.X, source.Bounds.Y, source.Bounds.Width, source.Bounds.Height),
                Properties = new Dictionary<string, string>(source.Properties),
                Events = new Dictionary<string, string>(source.Events),
                Children = new List<EmojiElementDesign>(),
            };

            foreach (var child in source.Children)
            {
                clone.Children.Add(CloneElement(child));
            }

            return clone;
        }

        private void DrawRoot(Graphics g)
        {
            var b = _document.Root.Bounds;
            using var brush = new SolidBrush(Color.White);
            using var pen = new Pen(Color.FromArgb(210, 216, 225));
            g.FillRectangle(brush, b.X, b.Y, b.Width, b.Height);
            g.DrawRectangle(pen, b.X, b.Y, b.Width, b.Height);
        }

        private void DrawElement(Graphics g, EmojiElementDesign element)
        {
            var selected = _selection.Contains(element);
            var primary = ReferenceEquals(element, _selected);
            var r = new Rectangle(element.Bounds.X, element.Bounds.Y, element.Bounds.Width, element.Bounds.Height);
            var fill = FillFor(element.Type);
            using var brush = new SolidBrush(fill);
            using var border = new Pen(primary ? Color.FromArgb(45, 125, 255) : selected ? Color.FromArgb(16, 185, 129) : Color.FromArgb(145, 156, 170), selected ? 2 : 1);
            g.FillRectangle(brush, r);
            g.DrawRectangle(border, r);

            var label = LabelFor(element);
            TextRenderer.DrawText(g, label, Font, r, Color.FromArgb(31, 41, 55), TextFormatFlags.Left | TextFormatFlags.VerticalCenter | TextFormatFlags.EndEllipsis);
            if (primary)
            {
                using var handle = new SolidBrush(Color.FromArgb(45, 125, 255));
                g.FillRectangle(handle, r.Right - 7, r.Bottom - 7, 7, 7);
            }
        }

        private EmojiElementDesign? HitTest(Point point)
        {
            return _document.Root.Children.LastOrDefault(child =>
                point.X >= child.Bounds.X && point.X <= child.Bounds.X + child.Bounds.Width
                && point.Y >= child.Bounds.Y && point.Y <= child.Bounds.Y + child.Bounds.Height);
        }

        private static bool IsResizeHandle(EmojiElementDesign element, Point point)
        {
            return Math.Abs(point.X - (element.Bounds.X + element.Bounds.Width)) <= 10
                && Math.Abs(point.Y - (element.Bounds.Y + element.Bounds.Height)) <= 10;
        }

        private static Color FillFor(string type)
        {
            return type switch
            {
                "Button" => Color.FromArgb(225, 238, 255),
                "Input" => Color.FromArgb(255, 255, 255),
                "EditBox" => Color.FromArgb(255, 255, 255),
                "Text" => Color.FromArgb(255, 252, 232),
                "Panel" => Color.FromArgb(248, 250, 252),
                "Table" => Color.FromArgb(241, 245, 249),
                "Card" => Color.FromArgb(250, 245, 255),
                "Tabs" => Color.FromArgb(236, 253, 245),
                "Dialog" => Color.FromArgb(254, 242, 242),
                "Drawer" => Color.FromArgb(239, 246, 255),
                "Notification" => Color.FromArgb(255, 247, 237),
                _ => Color.FromArgb(255, 255, 255),
            };
        }

        private static string LabelFor(EmojiElementDesign element)
        {
            var text = string.IsNullOrWhiteSpace(element.Text) ? element.Type : element.Text;
            return string.IsNullOrWhiteSpace(element.Emoji) ? $" {text}" : $" {element.Emoji} {text}";
        }

        private static EmojiElementDesign DefaultsFor(string type)
        {
            var element = new EmojiElementDesign
            {
                Type = type,
                Name = char.ToLowerInvariant(type[0]) + type.Substring(1),
                Bounds = new EmojiBounds(32, 32, 160, 42),
            };

            switch (type)
            {
                case "Text":
                    element.Text = "说明文本 ✅";
                    element.Bounds.Width = 260;
                    element.Bounds.Height = 36;
                    break;
                case "Button":
                    element.Text = "确认操作";
                    element.Emoji = "✅";
                    element.Events["Clicked"] = "OnButtonClicked";
                    break;
                case "Input":
                    element.Properties["placeholder"] = "请输入内容 😊";
                    element.Bounds.Width = 260;
                    break;
                case "EditBox":
                    element.Text = "可编辑文本";
                    element.Bounds.Width = 260;
                    break;
                case "Table":
                    element.Properties["columns"] = "名称,状态";
                    element.Properties["rows"] = "任务A,正常\n任务B,处理中";
                    element.Bounds.Width = 360;
                    element.Bounds.Height = 180;
                    break;
                case "Card":
                    element.Text = "数据卡片";
                    element.Properties["title"] = "数据卡片 📊";
                    element.Properties["body"] = "这里展示核心指标。";
                    element.Bounds.Width = 260;
                    element.Bounds.Height = 140;
                    break;
                case "Tabs":
                    element.Properties["items"] = "首页 🏠\n设置 ⚙️";
                    element.Bounds.Width = 360;
                    element.Bounds.Height = 160;
                    break;
                case "Dialog":
                    element.Text = "弹窗";
                    element.Properties["title"] = "提示窗口 ✅";
                    element.Properties["body"] = "这里是弹窗内容。";
                    element.Bounds.Width = 240;
                    element.Bounds.Height = 120;
                    break;
                case "Drawer":
                    element.Text = "抽屉";
                    element.Properties["title"] = "设置抽屉 ⚙️";
                    element.Properties["body"] = "这里是抽屉内容。";
                    element.Bounds.Width = 280;
                    element.Bounds.Height = 180;
                    break;
                case "Notification":
                    element.Text = "通知提醒";
                    element.Properties["title"] = "任务提醒 🔔";
                    element.Properties["body"] = "新任务已经同步完成。";
                    element.Bounds.Width = 320;
                    element.Bounds.Height = 110;
                    break;
            }

            return element;
        }
    }
}
