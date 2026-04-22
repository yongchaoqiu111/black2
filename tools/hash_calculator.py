"""
Black2 文件哈希计算工具
根据 Black2 协议白皮书 2.7 节，计算文件的 SHA-256 哈希值

使用方法：
1. 双击运行 hash_calculator.exe
2. 选择需要计算的文件
3. 复制生成的哈希值
4. 在 Black2 平台发布商品时粘贴此哈希值
"""

import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import os


class HashCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Black2 文件哈希计算工具")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # 设置样式
        self.root.configure(bg='#f0f0f0')
        
        # 标题
        title_frame = tk.Frame(root, bg='#667eea', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🔐 Black2 文件哈希计算工具",
            font=("Microsoft YaHei", 18, "bold"),
            bg='#667eea',
            fg='white'
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            title_frame,
            text="根据 Black2 协议白皮书 2.7 节 - 支持任意大小文件",
            font=("Microsoft YaHei", 10),
            bg='#667eea',
            fg='white'
        )
        subtitle_label.pack()
        
        # 主内容区
        content_frame = tk.Frame(root, bg='#f0f0f0', padx=30, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # 文件选择区域
        file_frame = tk.LabelFrame(
            content_frame, 
            text="选择文件",
            font=("Microsoft YaHei", 11, "bold"),
            bg='#f0f0f0',
            padx=15,
            pady=15
        )
        file_frame.pack(fill='x', pady=(0, 15))
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(
            file_frame,
            textvariable=self.file_path_var,
            font=("Microsoft YaHei", 10),
            state='readonly',
            width=50
        )
        file_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        select_btn = tk.Button(
            file_frame,
            text="浏览文件",
            command=self.select_file,
            font=("Microsoft YaHei", 10),
            bg='#667eea',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        select_btn.pack(side='right')
        
        # 文件信息
        info_frame = tk.Frame(content_frame, bg='#e8f4f8', padx=15, pady=10)
        info_frame.pack(fill='x', pady=(0, 15))
        
        self.file_name_label = tk.Label(
            info_frame,
            text="文件名：未选择",
            font=("Microsoft YaHei", 9),
            bg='#e8f4f8',
            anchor='w'
        )
        self.file_name_label.pack(anchor='w')
        
        self.file_size_label = tk.Label(
            info_frame,
            text="文件大小：-",
            font=("Microsoft YaHei", 9),
            bg='#e8f4f8',
            anchor='w'
        )
        self.file_size_label.pack(anchor='w')
        
        # 计算按钮
        calc_btn = tk.Button(
            content_frame,
            text="计算 SHA-256 哈希",
            command=self.calculate_hash,
            font=("Microsoft YaHei", 12, "bold"),
            bg='#764ba2',
            fg='white',
            padx=30,
            pady=12,
            cursor='hand2'
        )
        calc_btn.pack(pady=10)
        
        # 进度条
        progress_frame = tk.Frame(content_frame, bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=10)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="",
            font=("Microsoft YaHei", 9),
            bg='#f0f0f0'
        )
        self.progress_label.pack()
        
        # 结果显示区域
        result_frame = tk.LabelFrame(
            content_frame,
            text="计算结果",
            font=("Microsoft YaHei", 11, "bold"),
            bg='#f0f0f0',
            padx=15,
            pady=15
        )
        result_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.hash_text = tk.Text(
            result_frame,
            font=("Consolas", 11),
            height=3,
            wrap='word',
            bg='#d4edda',
            fg='#155724',
            relief='flat',
            padx=10,
            pady=10,
            state='disabled'
        )
        self.hash_text.pack(fill='both', expand=True)
        
        # 复制按钮
        copy_btn = tk.Button(
            result_frame,
            text="复制哈希值",
            command=self.copy_hash,
            font=("Microsoft YaHei", 10),
            bg='#28a745',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        copy_btn.pack(pady=10)
        
        # 说明文本
        help_text = tk.Label(
            content_frame,
            text="💡 提示：计算完成后，复制哈希值并在 Black2 平台发布商品时粘贴",
            font=("Microsoft YaHei", 9),
            bg='#f0f0f0',
            fg='#666'
        )
        help_text.pack(pady=(10, 0))
        
        self.selected_file = None
    
    def select_file(self):
        """选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择要计算哈希的文件",
            filetypes=[("所有文件", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_path_var.set(file_path)
            
            # 显示文件信息
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            self.file_name_label.config(text=f"文件名：{file_name}")
            self.file_size_label.config(text=f"文件大小：{self.format_size(file_size)}")
    
    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def calculate_hash(self):
        """计算文件SHA-256哈希"""
        if not self.selected_file:
            messagebox.showwarning("警告", "请先选择文件！")
            return
        
        if not os.path.exists(self.selected_file):
            messagebox.showerror("错误", "文件不存在！")
            return
        
        try:
            self.progress_label.config(text="正在计算哈希...")
            self.root.update()
            
            # 使用流式读取，支持大文件
            sha256_hash = hashlib.sha256()
            file_size = os.path.getsize(self.selected_file)
            bytes_read = 0
            chunk_size = 1024 * 1024  # 1MB
            
            with open(self.selected_file, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    sha256_hash.update(chunk)
                    bytes_read += len(chunk)
                    
                    # 更新进度
                    if file_size > 0:
                        progress = (bytes_read / file_size) * 100
                        self.progress_label.config(
                            text=f"计算中... {progress:.1f}% ({self.format_size(bytes_read)} / {self.format_size(file_size)})"
                        )
                        self.root.update()
            
            hash_hex = sha256_hash.hexdigest()
            
            # 显示结果
            self.hash_text.config(state='normal')
            self.hash_text.delete('1.0', tk.END)
            self.hash_text.insert('1.0', hash_hex)
            self.hash_text.config(state='disabled')
            
            self.progress_label.config(text="✅ 计算完成！")
            
            messagebox.showinfo("成功", "哈希计算完成！点击\"复制哈希值\"按钮复制结果。")
            
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")
            self.progress_label.config(text="❌ 计算失败")
    
    def copy_hash(self):
        """复制哈希值到剪贴板"""
        hash_value = self.hash_text.get('1.0', tk.END).strip()
        
        if not hash_value:
            messagebox.showwarning("警告", "没有可复制的哈希值！")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(hash_value)
        self.root.update()
        
        messagebox.showinfo("成功", "哈希值已复制到剪贴板！")


def main():
    root = tk.Tk()
    app = HashCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
