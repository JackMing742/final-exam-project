import tkinter as tk
from tkinter import messagebox, ttk
import requests
import threading

api_url = "http://127.0.0.1:8000/quotes"

"""呼叫子執行緒處理函式
widget.after(delay_ms, callback)
delay_ms → 延遲多少毫秒執行
callback → 延遲後要執行的函式
"""


# 清空 Treeview 內容
def clean_data(data) -> None:
    for item in tree.get_children():
        tree.delete(item)


# 恢復按鈕狀態
def restore_button() -> None:
    """恢復按鈕的正常狀態（在主執行緒中呼叫）。"""
    btn_load.config(
        state=tk.NORMAL, text="載入名言"
    )  # state=tk.NORMAL 恢復按鈕可點擊狀態


# 清空編輯區內容並恢復狀態列
def clear_edit_fields():
    """清空編輯區內容並恢復狀態列"""
    text_content.delete("1.0", tk.END)  # 清空文字區域
    entry_author.delete(0, tk.END)  # 清空作者輸入框
    entry_tags.delete(0, tk.END)  # 清空標籤輸入框
    status_label.config(text="準備就緒", fg="black")


# API 工作執行緒
def api_worker_thread():
    """[子執行緒] 負責跑網路，絕對不能操作 GUI"""
    try:
        # 執行耗時的 API 呼叫
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            raise Exception(f"API 錯誤，狀態碼：{response.status_code}")
        data = response.json()
        form.after(0, lambda: update_ui_success(data))  # 回到主執行緒更新 UI

    except Exception as e:
        form.after(0, lambda: update_ui_error(str(e)))


# 更新 UI 為錯誤狀態
def update_ui_error(error_msg: str) -> None:
    """
    更新 UI 為錯誤狀態（在主執行緒中呼叫）。

    參數：
        error_msg: 錯誤訊息
    """
    messagebox.showerror("錯誤", error_msg)  # 彈出錯誤對話框
    status_label.config(text=f"錯誤: {error_msg}", fg="red")  # 更新狀態列文字
    restore_button()


# 更新 UI 為成功狀態
def update_ui_success(data):
    """[主執行緒] 負責更新畫面 (Treeview/Label)"""
    clean_data(data)
    # 將資料加入 Treeview
    for item in data:
        tags_str = ", ".join(item.get("tags", []))  # 將標籤列表轉成字串

        tree.insert(
            "",  # 父節點為空代表最上層沒有階層關係所有資料都是在最上層
            tk.END,
            values=(item.get("id"), item.get("author"), item.get("text"), tags_str),
        )
    restore_button()
    status_label.config(text="資料載入成功", fg="green")  # 更新狀態列文字
    restore_button()


# 按下按鈕事件
def on_button_click():
    """[主執行緒] 按下按鈕"""
    if btn_load["state"] == tk.DISABLED:
        return  # 正在載入中，忽略重複點擊
    # 按鈕狀態改為不可點擊並且狀態列顯示載入中
    btn_load.config(state=tk.DISABLED, text="連線中...")
    status_label.config(text="正在從伺服器抓取資料...", fg="blue")
    thread: threading.Thread = threading.Thread(
        target=api_worker_thread, daemon=True
    )  #  建立執行緒
    thread.start()  # 啟動執行緒


# Treeview 選取事件
def on_tree_select(event):
    """當選取 Treeview 項目時，更新編輯區的內容"""
    selected = (
        tree.selection()
    )  # 取得節點的 ID不是自己設定的id是Tkinter 自動產生的並且我的資料都是平行的所以列表中只有一項為0
    if not selected:
        return
    # 取得選中行的資料：values 格式為 (ID, 作者, 內容, 標籤)
    values = tree.item(selected[0])["values"]

    # 更新狀態文字
    status_label.config(text=f"目前編輯 ID: {values[0]}", fg="black")

    # 更新作者 Entry
    entry_author.delete(0, tk.END)
    entry_author.insert(0, values[1])

    # 更新內容 Text
    text_content.delete("1.0", tk.END)
    text_content.insert("1.0", values[2])

    # 更新標籤 Entry
    entry_tags.delete(0, tk.END)
    entry_tags.insert(0, values[3])


# 新增名言
def add_quote():
    """新增名言"""
    text = text_content.get("1.0", tk.END).strip()
    author = entry_author.get().strip()
    tags_raw = entry_tags.get().strip()

    if not text:
        messagebox.showwarning("警告", "名言內容不可為空")
        return
    # 組合請求資料
    payload = {
        "text": text,
        "author": author,
        "tags": [tag.strip() for tag in tags_raw.split(",")] if tags_raw else [],
    }

    # 鎖定 UI
    status_label.config(text="正在新增名言...", fg="blue")
    bth_add.config(state=tk.DISABLED)

    def worker():
        try:
            # 2. 發送 API 請求
            response = requests.post(api_url, json=payload, timeout=10)
            if response.status_code == 200:
                # 3. 成功後回到主執行緒更新 UI
                form.after(
                    0,
                    lambda: [
                        messagebox.showinfo("成功", "名言新增成功"),
                        clear_edit_fields(),
                        on_button_click(),  # 自動重新整理列表
                    ],
                )
            else:
                form.after(
                    0,
                    lambda: messagebox.showerror(
                        "錯誤：無法連線至後端 API。請確認 API 是否已啟動，代碼：{response.status_code}"
                    ),
                )
        except Exception as e:
            form.after(0, lambda: messagebox.showerror("404", f"操作失敗：{str(e)}"))
        finally:
            # 4. 解鎖按鈕
            form.after(0, lambda: bth_add.config(state=tk.NORMAL))

    threading.Thread(target=worker, daemon=True).start()


# 更新名言資料
def update_quote():
    """更新名言"""
    selected = tree.selection()  # 取得選取項目的資料
    if not selected:
        messagebox.showwarning("警告", "請先選擇一則名言進行更新")
        return

    quote_id = tree.item(selected[0])["values"][0]
    text = text_content.get("1.0", tk.END).strip()
    author = entry_author.get().strip()
    tags_raw = entry_tags.get().strip()

    if not text:
        messagebox.showwarning("警告", "名言內容不可為空")
        return

    payload = {
        "text": text,
        "author": author,
        "tags": [tag.strip() for tag in tags_raw.split(",")] if tags_raw else [],
    }

    # 鎖定 UI
    status_label.config(text="正在更新名言...", fg="blue")
    bth_update.config(state=tk.DISABLED)

    def worker():
        try:
            # 2. 發送 API 請求
            response = requests.put(f"{api_url}/{quote_id}", json=payload, timeout=10)
            if response.status_code == 200:
                # 3. 成功後回到主執行緒更新 UI
                form.after(
                    0,
                    lambda: [
                        messagebox.showinfo("成功", "名言更新成功"),
                        clear_edit_fields(),
                        on_button_click(),  # 自動重新整理列表
                    ],
                )
            else:
                form.after(
                    0,
                    lambda: messagebox.showerror(
                        "錯誤：無法連線至後端 API。請確認 API 是否已啟動，代碼：{response.status_code}"
                    ),
                )
        except Exception as e:
            form.after(0, lambda: messagebox.showerror("404", f"操作失敗：{str(e)}"))
        finally:
            # 4. 解鎖按鈕
            form.after(0, lambda: bth_update.config(state=tk.NORMAL))

    threading.Thread(target=worker, daemon=True).start()


# 刪除名言
def delete_quote():
    """刪除名言"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("警告", "請先選擇一則名言進行刪除")
        return

    quote_id = tree.item(selected[0])["values"][0]

    if not messagebox.askyesno("確認刪除", "確定要刪除這則名言嗎？"):
        return

    # 鎖定 UI
    status_label.config(text="正在刪除名言...", fg="blue")
    bth_delete.config(state=tk.DISABLED)

    def worker():
        try:
            # 2. 發送 API 請求
            response = requests.delete(f"{api_url}/{quote_id}", timeout=10)
            if response.status_code == 200:
                # 3. 成功後回到主執行緒更新 UI
                form.after(
                    0,
                    lambda: [
                        messagebox.showinfo("成功", "名言刪除成功"),
                        clear_edit_fields(),
                        on_button_click(),  # 自動重新整理列表
                    ],
                )
            else:
                form.after(
                    0,
                    lambda: messagebox.showerror(
                        "錯誤：無法連線至後端 API。請確認 API 是否已啟動，代碼：{response.status_code}"
                    ),
                )
        except Exception as e:
            form.after(0, lambda: messagebox.showerror("404", f"操作失敗：{str(e)}"))
        finally:
            # 4. 解鎖按鈕
            form.after(0, lambda: bth_delete.config(state=tk.NORMAL))

    threading.Thread(target=worker, daemon=True).start()


# 主程式
def main() -> None:
    global tree, form, btn_load, status_label, text_content, entry_author, entry_tags
    global bth_add, bth_update, bth_delete
    # 建立主視窗
    form = tk.Tk()
    form.title("名言佳句管理系統")
    form.geometry("800x600")
    columns = ("ID", "author", "text", "tags")  # 建立 Treeview 列表

    # 建立列表框架
    list_frame = tk.Frame(form)
    list_frame.pack(pady=10, padx=10, fill="both", expand=True)
    tree = ttk.Treeview(list_frame, columns=columns, show="headings")
    tree.heading("ID", text="ID")
    tree.column("ID", width=50, anchor="center")
    tree.heading("author", text="作者")
    tree.column("author", width=150)
    tree.heading("text", text="內容")
    tree.column("text", width=400)
    tree.heading("tags", text="標籤")
    tree.column("tags", width=150)

    # 建立滾動條
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", on_tree_select)  # 綁定選取事件

    # 建立編輯區
    edit_frame = tk.LabelFrame(form, text="編輯/新增區")
    edit_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(edit_frame, text="名言內容").grid(row=0, column=0, sticky="w", padx=5)
    text_content = tk.Text(edit_frame, height=5, width=105)
    text_content.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
    tk.Label(edit_frame, text="作者").grid(row=2, column=0, sticky="w", padx=5)
    entry_author = tk.Entry(edit_frame, width=50)
    entry_author.grid(row=3, column=0, padx=10, pady=5, sticky="w")
    tk.Label(edit_frame, text="標籤").grid(row=2, column=1, sticky="w", padx=5)
    entry_tags = tk.Entry(edit_frame, width=50)
    entry_tags.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    # 建立按鈕區
    btn_frame = tk.LabelFrame(form, text="操作選項")
    btn_frame.pack(fill="x", padx=10, pady=5)
    # 載入按鈕
    btn_load = tk.Button(
        btn_frame,
        text="重新整理 (Refresh)",
        command=on_button_click,
        bg="#dddddd",
        width=25,
    )
    btn_load.pack(side="left", padx=10, pady=5)
    # 新增按鈕
    bth_add = tk.Button(
        btn_frame, text="新增名言 (Add)", bg="#dddddd", width=25, command=add_quote
    )
    bth_add.pack(side="left", padx=10, pady=5)
    # 更新按鈕
    bth_update = tk.Button(
        btn_frame,
        text="更新名言 (Update)",
        bg="#dddddd",
        width=25,
        command=update_quote,
    )
    bth_update.pack(side="left", padx=10, pady=5)
    # 刪除按鈕
    bth_delete = tk.Button(
        btn_frame,
        text="刪除名言 (Delete)",
        bg="#dddddd",
        width=25,
        command=delete_quote,
    )
    bth_delete.pack(side="left", padx=10)
    # 狀態列
    id_frame = tk.LabelFrame(form)  # id框架
    id_frame.pack(fill="x", padx=10, pady=5, side=tk.BOTTOM)  # id框架位置
    status_label = tk.Label(id_frame, text="準備就緒")  # 狀態列標籤
    status_label.pack(side="left", padx=5)

    form.mainloop()


if __name__ == "__main__":
    main()
