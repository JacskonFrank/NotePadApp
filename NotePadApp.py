import tkinter as tk
from tkinter import messagebox, filedialog, ttk


class TabbedNotepad:
    def __init__(self, root):
        # 初始化主窗口
        self.window = root
        # 创建 Notebook 小部件
        self.notebook = ttk.Notebook(root)
        # 设置窗口尺寸
        self.window.geometry('800x600')
        # 布局 Notebook 小部件以填充整个窗口
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建菜单栏
        self.menu_bar = tk.Menu(self.window)
        # 创建文件菜单
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        # 添加新建命令
        self.file_menu.add_command(label='新建', command=self.new_file)
        # 添加打开命令
        self.file_menu.add_command(label='打开', command=self.open_file)
        # 添加关闭命令
        self.file_menu.add_command(label='关闭', command=self.close_tab)
        # 查找命令
        self.file_menu.add_command(label='查找', command=self.do_find)
        # 添加保存命令
        self.file_menu.add_command(label='保存', command=self.save_file)
        # 添加另存为命令
        self.file_menu.add_command(label='另存为...', command=self.save_as)
        # 添加分割线
        self.file_menu.add_separator()
        # 添加退出命令
        self.file_menu.add_command(label='退出', command=self.window.quit)
        # 将文件菜单添加到菜单栏
        self.menu_bar.add_cascade(label='文件', menu=self.file_menu)
        # 配置主窗口使用此菜单栏
        self.window.config(menu=self.menu_bar)

        # 存储所有打开的标签页及其相关信息
        self.tabs = {}

    def new_file(self):
        # 创建新的标签页
        tab = ttk.Frame(self.notebook)
        # 创建 Text 小部件，并启用撤销功能
        text = tk.Text(tab, undo=True)
        # 布局 Text 小部件以填充整个标签页
        text.pack(fill=tk.BOTH, expand=True)
        # 绑定事件处理器，当文本发生变化时调用 on_changed
        text.bind('<KeyRelease>', self.on_changed)
        # 添加标签页到 Notebook
        self.notebook.add(tab, text='未命名')
        # 将标签页及其相关信息存储到 self.tabs 字典中
        self.tabs[tab] = {'text': text, 'path': None}
        # 选择当前添加的标签页
        self.notebook.select(tab)

    def open_file(self):
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename()
        if file_path:
            # 创建新的标签页
            tab = ttk.Frame(self.notebook)
            # 创建 Text 小部件，并启用撤销功能
            text = tk.Text(tab, undo=True)
            # 布局 Text 小部件以填充整个标签页
            text.pack(fill=tk.BOTH, expand=True)
            # 绑定事件处理器，当文本发生变化时调用 on_changed
            text.bind('<KeyRelease>', self.on_changed)
            # 添加标签页到 Notebook
            self.notebook.add(tab, text=file_path.split('/')[-1])
            # 将标签页及其相关信息存储到 self.tabs 字典中
            self.tabs[tab] = {'text': text, 'path': file_path}
            try:
                # 读取文件内容并插入到 Text 小部件中
                with open(file_path, 'r') as f:
                    text.insert(1.0, f.read())
            except Exception as e:
                # 显示错误消息
                messagebox.showerror('打开文件失败', f'错误: {e}')
            # 选择当前添加的标签页
            self.notebook.select(tab)

    def close_tab(self):
        # 获取当前选中的标签页
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab in self.tabs:
            # 检查是否有未保存的更改
            if self.tabs[current_tab]['text'].edit_modified():
                # 提示用户是否保存更改
                if messagebox.askyesno('保存', '你想要保存当前文件吗？'):
                    # 调用保存文件方法
                    self.save_file()
            # 移除当前标签页
            self.notebook.forget(current_tab)
            # 从 self.tabs 字典中移除当前标签页的信息
            del self.tabs[current_tab]

    def do_find(self):
        # 获取当前选中的标签页
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab not in self.tabs:
            return
        text = self.tabs[current_tab]['text']
        if current_tab in self.tabs:
            find_window = tk.Toplevel(self.window)
            find_window.title('查找')
            find_window.geometry('210x25')
            find_label = tk.Label(find_window, text='查找:')
            find_label.grid(row=0, column=0)
            find_entry = tk.Entry(find_window)
            find_entry.grid(row=0, column=1)
            find_button = tk.Button(find_window, text='查找', command=lambda: self.find_text(text, find_entry.get(),current_tab))
            find_button.grid(row=0, column=2)
            # 绑定事件处理器，当按键释放时调用 find_text
            find_entry.bind('<KeyRelease>', lambda event: self.find_text(text, find_entry.get(), current_tab))
            # 绑定事件处理器，当按按下回车键时调用 find_text
            find_entry.bind('<Return>', lambda event: self.find_text(text, find_entry.get(), current_tab))
            # 聚焦到 Entry 小部件
            find_entry.focus_set()
            # 绑定事件处理器，当按按下 Escape 键时调用 find_window.destroy
            find_entry.bind('<Escape>', lambda event: find_window.destroy())

    def find_text(self, text, word, tab):
        """
        查找文本
        :param text: Text 小部件
        :param word: 要查找的字符串
        :param tab: 当前标签页
        :return:
        """
        self.tabs[tab]['text'].tag_remove('found', '1.0', tk.END)
        if not word or not tab or not text:
            return
        try:
            index = '1.0'
            while True:
                # 在文本中查找 find_word
                # search 方法返回找到的字符串的索引位置，格式：'1.0+2c'，表示从第1行第0列开始，向后移动2个字符
                # search(text, startindex, stopindex, nocase)
                # stopindex=tk.END 表示搜索到文本末尾，nocase=0 表示不区分大小写，
                index = text.search(word, index, stopindex=tk.END, nocase=0)
                # 如果没有找到，则退出循环
                if not index:
                    break
                # last 作用为将索引位置向后移动 find_word 的长度
                last = f'{index}+{len(word)}c'
                # 将找到的字符串添加到 'found' 标签中
                text.tag_add('found', index, last)
                # 将下一次开始的索引index位置设置为 last
                index = last
            # 设置 'found' 标签的样式，字体为红色， 背景为黄色
            text.tag_config('found', foreground='red', background='yellow')
        except tk.TclError:
            pass

    def save_file(self):
        # 获取当前选中的标签页
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab in self.tabs:
            # 获取当前标签页的 Text 小部件和路径
            text = self.tabs[current_tab]['text']
            path = self.tabs[current_tab]['path']
            if path:
                try:
                    # 将文本内容写入文件
                    with open(path, 'w') as f:
                        f.write(text.get(1.0, tk.END))
                except Exception as e:
                    # 显示保存失败的错误消息
                    messagebox.showerror('保存失败', f'错误: {e}')
            else:
                # 如果没有路径，则提示用户选择保存位置
                path = filedialog.asksaveasfilename()
                if path:
                    try:
                        # 将文本内容写入文件
                        with open(path, 'w') as f:
                            f.write(text.get(1.0, tk.END))
                        # 更新当前标签页的路径
                        self.tabs[current_tab]['path'] = path
                        # 更新标签页的标题
                        self.notebook.tab(current_tab, text=path.split('/')[-1])
                    except Exception as e:
                        # 显示保存失败的错误消息
                        messagebox.showerror('保存失败', f'错误: {e}')

    def save_as(self):
        # 获取当前选中的标签页
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab in self.tabs:
            # 提示用户选择保存位置
            save_file_name = filedialog.asksaveasfilename()
            if save_file_name:
                try:
                    # 将文本内容写入文件
                    with open(save_file_name, 'w') as f:
                        f.write(self.tabs[current_tab]['text'].get(1.0, tk.END))
                    # 更新当前标签页的路径
                    self.tabs[current_tab]['path'] = save_file_name
                    # 更新标签页的标题
                    self.notebook.tab(current_tab, text=save_file_name.split('/')[-1])
                except Exception as e:
                    # 显示另存为失败的错误消息
                    messagebox.showerror('另存为失败', f'错误：{e}')

    def on_changed(self, event):
        # 当文本发生变化时，标记为已修改
        current_tab = self.notebook.nametowidget(self.notebook.select())
        self.tabs[current_tab]['text'].edit_modified(True)

    def undo(self):
        # 获取当前选中的标签页
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab in self.tabs:
            self.tabs[current_tab]['text'].edit_undo()

    def redo(self):
        # 获取当前选中的标签页
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if current_tab in self.tabs:
            self.tabs[current_tab]['text'].edit_redo()


if __name__ == "__main__":
    # 创建主窗口
    window = tk.Tk()
    # 设置窗口标题
    window.title('记事本')
    # 创建 TabbedNotepad 实例
    app = TabbedNotepad(window)
    # 运行主循环
    window.mainloop()