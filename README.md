# BANANA GLOBE — Banana × Stocks × AI

[English](#english) | [日本語](#日本語)

---

## English

An art piece that **re-frames capitalism through the banana**: banana × stocks × AI.
It pairs a cinematic **3D photoreal globe** (the attract / seduction layer) with an objective **D3 statistics dashboard** (the evidence layer). The core tension the piece stages: on the metrics the investment is *meaningless*, yet the return is ~10×.

### Run
```sh
cd ~/dev/banana-globe
python3 -m http.server 8200
# → http://localhost:8200/            (attract: 3D globe)
# → http://localhost:8200/trade.html      (trade-flow view: south → north)
# → http://localhost:8200/evidence.html   (evidence: D3 dashboard)
```

### Structure
- `index.html` — attract layer: the 3D photoreal Earth.
- `trade.html` — trade-flow view: banana trade flows (FAO/UN Comtrade, ~2023 approx.) as glowing pulses over a realistic 16K Earth. 98% of the volume flows south → north.
- `evidence.html` — evidence layer: the D3 objective-statistics dashboard.
- `evidence.json` — the underlying data.
- `build_evidence.py` — generates `evidence.json`.
- `banana_globe.hip` — Houdini scene for the rendered globe assets.
- `tex/` — textures. `render/` — rendered outputs (git-ignored).

### Texture credits
- Day (16K, `tex/color_16k.jpg`): NASA Blue Marble Next Generation (2004-07, topo + bathymetry), downscaled from the 21600×10800 original ([NASA Visible Earth](https://visibleearth.nasa.gov/), public domain). The original is kept out of the repo; regenerate with a Lanczos resize to 16384×8192.
- Night / stars (8K): [Solar System Scope](https://www.solarsystemscope.com/textures/) (CC BY 4.0).

### Concept
The two layers are deliberately opposed: the globe seduces, the dashboard testifies. The piece lives in the contradiction between the emotional pull of the image and what the numbers actually say.

---

## 日本語

**バナナを通して資本主義を捉え直す**作品。バナナ×株×AI。
映画的な**3D 実写地球**（アトラクト＝誘惑の層）と、客観的な **D3 統計ダッシュボード**（証拠の層）を対にする。
作品が立てる核心の矛盾：指標上その投資は*無意味*なのに、リターンは約 10 倍。

### 起動
```sh
cd ~/dev/banana-globe
python3 -m http.server 8200
# → http://localhost:8200/            （アトラクト：3D 地球）
# → http://localhost:8200/trade.html      （貿易フロー：南から北へ）
# → http://localhost:8200/evidence.html   （証拠：D3 ダッシュボード）
```

### 構成
- `index.html` — アトラクト層：3D 実写地球。
- `trade.html` — 貿易フロー・ビュー：バナナ貿易（FAO/UN Comtrade 2023年前後の概数）を 16K リアル地球上の光のパルスで描く。輸送量の98%が南→北へ流れる。
- `evidence.html` — 証拠層：D3 客観統計ダッシュボード。
- `evidence.json` — 元データ。
- `build_evidence.py` — `evidence.json` を生成。
- `banana_globe.hip` — 地球アセットの Houdini シーン。
- `tex/` — テクスチャ。`render/` — レンダー出力（git 管理外）。

### テクスチャのクレジット
- 昼（16K, `tex/color_16k.jpg`）: NASA Blue Marble Next Generation（2004-07, 地形＋海底地形入り）。21600×10800 原板（[NASA Visible Earth](https://visibleearth.nasa.gov/)、パブリックドメイン）を 16384×8192 に Lanczos 縮小。原板はリポジトリ外。
- 夜・星空（8K）: [Solar System Scope](https://www.solarsystemscope.com/textures/)（CC BY 4.0）。

### コンセプト
2つの層は意図的に対立する：地球は誘惑し、ダッシュボードは証言する。
イメージの情動的な引力と、数字が実際に語ることの矛盾に作品は宿る。
