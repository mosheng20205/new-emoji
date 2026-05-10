using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Windows.Forms;
using NewEmoji.Design;

namespace NewEmoji.Designer.WinForms48
{
    internal sealed class MainForm : Form
    {
        private readonly DesignerCanvas _canvas = new();
        private readonly ListBox _toolbox = new();
        private readonly TreeView _tree = new();
        private readonly PropertyGrid _propertyGrid = new();
        private readonly TextBox _log = new();
        private EmojiLayoutDocument _document = EmojiLayoutDocument.CreateDefault();
        private string? _currentJsonPath;
        private string? _lastExportDirectory;
        private bool _syncingTree;

        public MainForm()
        {
            Text = "✅ new_emoji 可视化设计器 (.NET 4.8)";
            Width = 1180;
            Height = 760;
            StartPosition = FormStartPosition.CenterScreen;
            BuildUi();
            BindDocument(_document);
        }

        private void BuildUi()
        {
            var menu = new MenuStrip();
            var file = new ToolStripMenuItem("文件");
            file.DropDownItems.Add("新建布局 ✅", null, (_, _) => NewLayout());
            file.DropDownItems.Add("打开 JSON 📂", null, (_, _) => OpenJson());
            file.DropDownItems.Add("保存 JSON 💾", null, (_, _) => SaveJson());
            file.DropDownItems.Add(new ToolStripSeparator());
            file.DropDownItems.Add("导出 C# .NET 4.8 项目 🚀", null, (_, _) => ExportProject());
            file.DropDownItems.Add("构建导出项目 🔧", null, (_, _) => BuildExportedProject());
            file.DropDownItems.Add("运行导出项目 ▶", null, (_, _) => RunExportedProject());
            menu.Items.Add(file);

            var edit = new ToolStripMenuItem("编辑");
            edit.DropDownItems.Add("撤销 ↶", null, (_, _) => _canvas.Undo());
            edit.DropDownItems.Add("重做 ↷", null, (_, _) => _canvas.Redo());
            edit.DropDownItems.Add(new ToolStripSeparator());
            edit.DropDownItems.Add("全选组件", null, (_, _) => _canvas.SelectAll());
            edit.DropDownItems.Add("复制组件 📋", null, (_, _) => _canvas.CopySelected());
            edit.DropDownItems.Add("粘贴组件 📌", null, (_, _) => _canvas.PasteClipboard());
            edit.DropDownItems.Add("复制一份组件 ✨", null, (_, _) => _canvas.DuplicateSelected());
            edit.DropDownItems.Add("删除组件 🗑", null, (_, _) => _canvas.DeleteSelected());
            menu.Items.Add(edit);

            var align = new ToolStripMenuItem("对齐");
            align.DropDownItems.Add("左对齐", null, (_, _) => _canvas.AlignSelected(DesignerAlignCommand.Left));
            align.DropDownItems.Add("右对齐", null, (_, _) => _canvas.AlignSelected(DesignerAlignCommand.Right));
            align.DropDownItems.Add("顶端对齐", null, (_, _) => _canvas.AlignSelected(DesignerAlignCommand.Top));
            align.DropDownItems.Add("底端对齐", null, (_, _) => _canvas.AlignSelected(DesignerAlignCommand.Bottom));
            align.DropDownItems.Add("水平居中", null, (_, _) => _canvas.AlignSelected(DesignerAlignCommand.HorizontalCenter));
            align.DropDownItems.Add("垂直居中", null, (_, _) => _canvas.AlignSelected(DesignerAlignCommand.VerticalCenter));
            align.DropDownItems.Add(new ToolStripSeparator());
            align.DropDownItems.Add("等宽", null, (_, _) => _canvas.AlignSelected(DesignerAlignCommand.SameWidth));
            align.DropDownItems.Add("等高", null, (_, _) => _canvas.AlignSelected(DesignerAlignCommand.SameHeight));
            menu.Items.Add(align);

            MainMenuStrip = menu;
            Controls.Add(menu);

            var split = new SplitContainer
            {
                Dock = DockStyle.Fill,
                Orientation = Orientation.Vertical,
                SplitterDistance = 230,
            };
            Controls.Add(split);
            split.BringToFront();

            var leftSplit = new SplitContainer
            {
                Dock = DockStyle.Fill,
                Orientation = Orientation.Horizontal,
                SplitterDistance = 310,
            };
            split.Panel1.Controls.Add(leftSplit);

            var toolboxGroup = new GroupBox
            {
                Dock = DockStyle.Fill,
                Text = "组件库 🧩",
                Font = new Font("Microsoft YaHei UI", 9f),
            };
            _toolbox.Dock = DockStyle.Fill;
            _toolbox.Font = new Font("Microsoft YaHei UI", 10f);
            _toolbox.Items.AddRange(new object[]
            {
                new DesignerComponentItem("Panel", "面板 Panel", 220, 140),
                new DesignerComponentItem("Text", "文本 Text ✅", 260, 36),
                new DesignerComponentItem("Button", "按钮 Button ✅", 160, 42),
                new DesignerComponentItem("Input", "输入框 Input 😊", 260, 42),
                new DesignerComponentItem("EditBox", "编辑框 EditBox", 260, 42),
                new DesignerComponentItem("Table", "表格 Table 📊", 360, 180),
                new DesignerComponentItem("Card", "卡片 Card 📌", 260, 140),
                new DesignerComponentItem("Tabs", "标签页 Tabs", 360, 160),
                new DesignerComponentItem("Dialog", "弹窗 Dialog", 240, 120),
                new DesignerComponentItem("Drawer", "抽屉 Drawer ⚙️", 280, 180),
                new DesignerComponentItem("Notification", "通知 Notification 🔔", 320, 110),
            });
            _toolbox.MouseDown += (_, _) =>
            {
                if (_toolbox.SelectedItem is DesignerComponentItem item)
                {
                    _toolbox.DoDragDrop(item, DragDropEffects.Copy);
                }
            };
            _toolbox.DoubleClick += (_, _) =>
            {
                if (_toolbox.SelectedItem is DesignerComponentItem item)
                {
                    _canvas.AddElement(item.Type, new Point(48, 48));
                }
            };
            toolboxGroup.Controls.Add(_toolbox);
            leftSplit.Panel1.Controls.Add(toolboxGroup);

            var treeGroup = new GroupBox
            {
                Dock = DockStyle.Fill,
                Text = "组件树 🌳",
                Font = new Font("Microsoft YaHei UI", 9f),
            };
            _tree.Dock = DockStyle.Fill;
            _tree.HideSelection = false;
            _tree.AfterSelect += (_, e) =>
            {
                if (_syncingTree)
                {
                    return;
                }

                _canvas.SelectElement(e.Node?.Tag as EmojiElementDesign);
            };
            treeGroup.Controls.Add(_tree);
            leftSplit.Panel2.Controls.Add(treeGroup);

            var rightSplit = new SplitContainer
            {
                Dock = DockStyle.Fill,
                Orientation = Orientation.Vertical,
                SplitterDistance = 690,
            };
            split.Panel2.Controls.Add(rightSplit);

            _canvas.Dock = DockStyle.Fill;
            _canvas.SelectedElementChanged += (_, _) =>
            {
                _propertyGrid.SelectedObject = _canvas.SelectedElement is null ? null : new EmojiElementEditor(_canvas.SelectedElement);
                SelectTreeNode(_canvas.SelectedElement);
            };
            _canvas.ElementsChanged += (_, _) =>
            {
                _document = _canvas.Document;
                RefreshTree();
            };
            rightSplit.Panel1.Controls.Add(_canvas);

            var propertySplit = new SplitContainer
            {
                Dock = DockStyle.Fill,
                Orientation = Orientation.Horizontal,
                SplitterDistance = 420,
            };
            rightSplit.Panel2.Controls.Add(propertySplit);

            _propertyGrid.Dock = DockStyle.Fill;
            _propertyGrid.PropertyValueChanged += (_, _) =>
            {
                _canvas.RecordDocumentChange();
                _canvas.Invalidate();
                RefreshTree();
            };
            propertySplit.Panel1.Controls.Add(_propertyGrid);

            _log.Dock = DockStyle.Fill;
            _log.Multiline = true;
            _log.ReadOnly = true;
            _log.ScrollBars = ScrollBars.Vertical;
            _log.Font = new Font("Consolas", 9f);
            propertySplit.Panel2.Controls.Add(_log);
        }

        private void BindDocument(EmojiLayoutDocument document)
        {
            _document = document;
            _canvas.Document = _document;
            _propertyGrid.SelectedObject = null;
            RefreshTree();
            Log("布局已加载。");
        }

        private void RefreshTree()
        {
            var selected = _canvas.SelectedElement;
            _syncingTree = true;
            try
            {
                _tree.BeginUpdate();
                _tree.Nodes.Clear();
                var root = new TreeNode($"窗口：{_document.Window.Title} 🪟");
                foreach (var child in _document.Root.Children)
                {
                    root.Nodes.Add(CreateElementNode(child));
                }

                _tree.Nodes.Add(root);
                root.Expand();
            }
            finally
            {
                _tree.EndUpdate();
                _syncingTree = false;
            }

            SelectTreeNode(selected);
        }

        private static TreeNode CreateElementNode(EmojiElementDesign element)
        {
            var emoji = string.IsNullOrWhiteSpace(element.Emoji) ? "" : element.Emoji + " ";
            var text = string.IsNullOrWhiteSpace(element.Text) ? "" : " - " + element.Text;
            var node = new TreeNode($"{emoji}{element.Name} [{element.Type}]{text}") { Tag = element };
            foreach (var child in element.Children)
            {
                node.Nodes.Add(CreateElementNode(child));
            }

            return node;
        }

        private void SelectTreeNode(EmojiElementDesign? element)
        {
            _syncingTree = true;
            try
            {
                _tree.SelectedNode = element is null ? null : FindNode(_tree.Nodes, element);
            }
            finally
            {
                _syncingTree = false;
            }
        }

        private static TreeNode? FindNode(TreeNodeCollection nodes, EmojiElementDesign element)
        {
            foreach (TreeNode node in nodes)
            {
                if (ReferenceEquals(node.Tag, element))
                {
                    return node;
                }

                var child = FindNode(node.Nodes, element);
                if (child is not null)
                {
                    return child;
                }
            }

            return null;
        }

        private void NewLayout()
        {
            _currentJsonPath = null;
            BindDocument(EmojiLayoutDocument.CreateDefault());
        }

        private void OpenJson()
        {
            using var dialog = new OpenFileDialog
            {
                Title = "打开 new_emoji 布局 JSON",
                Filter = "new_emoji 布局 (*.json)|*.json|所有文件 (*.*)|*.*",
            };
            if (dialog.ShowDialog(this) != DialogResult.OK)
            {
                return;
            }

            _currentJsonPath = dialog.FileName;
            BindDocument(EmojiLayoutSerializer.Load(dialog.FileName));
        }

        private void SaveJson()
        {
            if (string.IsNullOrEmpty(_currentJsonPath))
            {
                using var dialog = new SaveFileDialog
                {
                    Title = "保存 new_emoji 布局 JSON",
                    Filter = "new_emoji 布局 (*.json)|*.json|所有文件 (*.*)|*.*",
                    FileName = "new_emoji_layout.json",
                };
                if (dialog.ShowDialog(this) != DialogResult.OK)
                {
                    return;
                }

                _currentJsonPath = dialog.FileName;
            }

            var path = _currentJsonPath ?? throw new InvalidOperationException("保存路径为空。");
            EmojiLayoutSerializer.Save(path, _document);
            Log($"已保存 JSON：{_currentJsonPath}");
        }

        private void ExportProject()
        {
            var errors = new EmojiLayoutValidator().Validate(_document);
            if (errors.Count > 0)
            {
                MessageBox.Show(this, string.Join(Environment.NewLine, errors), "布局校验未通过", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            using var dialog = new FolderBrowserDialog
            {
                Description = "选择导出 C# .NET 4.8 项目的目录",
            };
            if (dialog.ShowDialog(this) != DialogResult.OK)
            {
                return;
            }

            var root = FindRepositoryRoot();
            var newEmojiProject = Path.Combine(root, "bindings", "csharp", "NewEmoji", "NewEmoji.csproj");
            var nativeDll = Path.Combine(root, "bin", "x64", "Release", "new_emoji.dll");
            new EmojiCodeGenerator().ExportNet48Project(_document, dialog.SelectedPath, newEmojiProject, nativeDll);
            _lastExportDirectory = dialog.SelectedPath;
            Log($"已导出项目：{dialog.SelectedPath}");
        }

        private void BuildExportedProject()
        {
            var project = GetLastExportedProject();
            if (project is null)
            {
                return;
            }

            RunProcess("dotnet", $"build \"{project}\"", Path.GetDirectoryName(project)!);
        }

        private void RunExportedProject()
        {
            var project = GetLastExportedProject();
            if (project is null)
            {
                return;
            }

            RunProcess("dotnet", $"run --project \"{project}\"", Path.GetDirectoryName(project)!);
        }

        private string? GetLastExportedProject()
        {
            if (string.IsNullOrEmpty(_lastExportDirectory))
            {
                MessageBox.Show(this, "请先导出 C# .NET 4.8 项目。", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return null;
            }

            var project = Path.Combine(_lastExportDirectory, "GeneratedNewEmojiApp.csproj");
            if (!File.Exists(project))
            {
                MessageBox.Show(this, "未找到导出的项目文件。", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return null;
            }

            return project;
        }

        private void RunProcess(string fileName, string arguments, string workingDirectory)
        {
            var info = new ProcessStartInfo(fileName, arguments)
            {
                WorkingDirectory = workingDirectory,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
            };

            using var process = Process.Start(info);
            if (process is null)
            {
                Log("启动进程失败。");
                return;
            }

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();
            Log(output);
            if (!string.IsNullOrWhiteSpace(error))
            {
                Log(error);
            }
        }

        private static string FindRepositoryRoot()
        {
            var current = new DirectoryInfo(AppDomain.CurrentDomain.BaseDirectory);
            while (current is not null)
            {
                if (File.Exists(Path.Combine(current.FullName, "bindings", "csharp", "NewEmoji", "NewEmoji.csproj")))
                {
                    return current.FullName;
                }

                current = current.Parent;
            }

            return AppDomain.CurrentDomain.BaseDirectory;
        }

        private void Log(string message)
        {
            if (string.IsNullOrWhiteSpace(message))
            {
                return;
            }

            _log.AppendText(message.TrimEnd() + Environment.NewLine);
        }
    }
}
