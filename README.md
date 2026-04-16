# mac-etax-package

このリポジトリは、有料note記事「Macで法人税を自力でe-Tax申告する方法」の購入者向けに提供するファイル一式です。

> **note記事からアクセスされた方へ**
> 以下のファイル構成と使い方は、記事の有料パートに詳しく記載されています。
> まずは `templates/申告マスター.md` を開いてください。

---

## ファイル構成

```
mac-etax-package/
├── README.md
├── LICENSE
├── etax_builder.py         # XTX生成コアエンジン
├── KNOWHOW.md              # AIに読ませるエラー回避・落とし穴集
└── templates/
    ├── OVERVIEW.md         # AIが最初に読む索引（購入者はまず申告マスター.mdへ）
    ├── 申告マスター.md     # 【起点】会社情報の入力 & XTX生成プロンプト
    ├── 別表一.md
    ├── 別表一（次葉）.md
    ├── 別表二.md
    ├── 別表四.md
    ├── 別表五（一）.md
    ├── 別表五（二）.md
    ├── 別表六（一）.md
    ├── 別表七（一）.md
    ├── 別表十五.md
    ├── 法人事業概況説明書.md
    └── 中間申告.md
```

---

## ライセンス

[CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/)  
本パッケージの無断転載・改変・再配布を禁じます。
