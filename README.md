# #動態名言佳句管理系統

# 專案描述

這是一個基於 Python Tkinter 開發的桌面應用程式，用於管理名言佳句。本專案整合了 Selenium 爬蟲 獲取初始資料，並對接 FastAPI 後端，實現了完整的 CRUD（新增、讀取、更新、刪除）功能，確保資料能同步反映在資料庫與介面中。

# 執行前條件

確保電腦已安裝 Python 3.10+。

# 執行步驟:

第一步:安裝套件：pip install -r requirements.txt

第二步:執行爬蟲：python pacho.py (此時應產生 quotes.db 並有 50 筆資料
)
第三步:啟動 API：uvicorn api:app --reload (注意：GUI 執行時，API 必須保持開啟狀態)

第四步:執行 GUI：python gui.py (測試新增、刪除、修改功能是否同步影響 API 與資料庫，且操作時畫面流暢)

# 成果展示:

<img width="1339" height="680" alt="Image" src="https://github.com/user-attachments/assets/e89a1284-ff54-4cd9-bd0a-dd64fb50d94d" />
<img width="1418" height="727" alt="Image" src="https://github.com/user-attachments/assets/b84f0e54-8649-4623-b942-63147b06a682" />
<img width="1338" height="599" alt="Image" src="https://github.com/user-attachments/assets/37b93df3-3ad3-48ea-adb2-6a5b076a7c1a" />
<img width="1329" height="617" alt="Image" src="https://github.com/user-attachments/assets/b8bc360d-6324-4db2-b709-c0af0369a24b" />
<img width="1352" height="606" alt="Image" src="https://github.com/user-attachments/assets/727397fd-8a7e-4263-84b5-dc1861f60f9d" />
<img width="1333" height="594" alt="Image" src="https://github.com/user-attachments/assets/2f157e35-3403-43fa-a1b8-69a16e615f05" />