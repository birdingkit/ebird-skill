**繁體中文** | [English](README.md)

# ebird-skill

一個 [Claude Code](https://claude.com/claude-code) 技能，用於查詢 [eBird API 2.0](https://documenter.getpostman.com/view/664302/S1ENwy59)。可以詢問鳥類觀察紀錄、熱點、稀有鳥種、物種清單及地區統計資料，Claude 會自動處理 API 呼叫。

## 安裝

將此技能加入 Claude Code：

```bash
claude skill add /path/to/ebird-skill
```

## API Key

需要免費的 eBird API key，可至 https://ebird.org/api/keygen 註冊取得。

使用技能時，如果尚未提供 API key，Claude 會主動詢問。

## 你可以這樣問

**查詢鳥況**
- 「台北最近有什麼鳥？」
- 「布袋的黑面琵鷺紀錄」
- 「我附近有什麼稀有鳥種？」
- 「宜蘭最好的賞鳥熱點？」
- 「今天台灣 eBird 排行榜前 100 名？」
- "Where can I see a Black-faced Spoonbill?"（也支援英文）

**資料分析與匯出**
- 「把查詢結果輸出成 CSV」
- 「比較台北和台南近一個月的鳥種數量」
- 「畫出七股黑面琵鷺近兩週的數量趨勢圖」
- 「用 R 分析嘉義沿海濕地的鳥種多樣性」
- 「把台灣各縣市的 eBird 熱點數量畫成地圖」

## 支援的指令

| 指令 | 說明 |
|------|------|
| `recent` | 某地區的近期觀察紀錄 |
| `nearby` | 座標附近的近期觀察紀錄 |
| `notable` | 某地區的稀有鳥種紀錄 |
| `nearby-notable` | 座標附近的稀有鳥種紀錄 |
| `species` | 特定物種在某地區的近期紀錄 |
| `nearby-species` | 座標附近的特定物種紀錄 |
| `hotspots` | 某地區的賞鳥熱點 |
| `nearby-hotspots` | 座標附近的賞鳥熱點 |
| `taxonomy` | 以名稱搜尋物種（含本地快取） |
| `hotspot-info` | 特定熱點的詳細資訊 |
| `historic` | 特定日期的觀察紀錄 |
| `top100` | 特定日期的前 100 名貢獻者 |
| `stats` | 特定日期的地區統計 |
| `sub-regions` | 列出某地區的子區域 |

## 搭配 R 或其他語言使用

此技能透過 Python 腳本取得資料，但回傳的 JSON 可以用任何語言分析和視覺化。例如，你可以請 Claude 用 R（ggplot2）繪製物種觀察圖表，或進行統計分析——Claude 會先用此技能取得資料，再撰寫 R 程式碼處理。

需求：Python（執行技能腳本）加上你偏好的分析環境（R、Julia 等）。

## 直接使用

也可以直接執行腳本：

```bash
python ebird_api.py recent --key YOUR_API_KEY --region TW --back 7 --locale zh
python ebird_api.py taxonomy --key YOUR_API_KEY --species "黑面琵鷺" --locale zh
python ebird_api.py notable --key YOUR_API_KEY --region TW-TPE --back 14
```

執行 `python ebird_api.py --help` 查看所有選項。

## 授權

MIT
