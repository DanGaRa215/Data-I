import streamlit as st
from PIL import Image
import numpy as np
from scipy.spatial import distance # ユークリッド距離計算に使用

#  色彩抽出関数↓
def ext_mean_rgb(filepath_or_bytes):

    #画像ファイルまたはBytesIOオブジェクトから平均RGB値を抽出
    if isinstance(filepath_or_bytes, str):
        image = Image.open(filepath_or_bytes).convert('RGB')
    else: # StreamlitのFileUploaderからの入力の場合
        image = Image.open(filepath_or_bytes).convert('RGB')
    
    image_np = np.array(image).reshape(-1, 3)
    return np.array([np.mean(image_np[:, 0]), np.mean(image_np[:, 1]),
                     np.mean(image_np[:, 2])], dtype=np.float32)

# 色ベクトル生成関数 ↓
def gen_color_vec(rgbvec):
    
    #平均RGB値から,10色のパレットに対する類似度を表すベクトルを生成
    palette = np.array(
        [
            [255, 0, 0],  # 赤
            [255, 102, 0],  # 橙
            [255, 255, 0],  # 黄
            [0, 128, 0],  # 緑
            [0, 0, 255],  # 青
            [128, 0, 128],  # 紫
            [255, 0, 255],  # ピンク
            [255, 255, 255],  # 白
            [128, 128, 128],  # グレー
            [0, 0, 0]  # 黒
        ], dtype=np.float32)

    # rgbvecもfloat32であることを確認
    rgbvec = rgbvec.astype(np.float32)

    colorvec = np.array([])
    for col in palette:
        colorvec = np.append(colorvec, distance.euclidean(col, rgbvec))
    
    # 距離を類似度（0-1）に変換
    # 距離の最大値で割ることで正規化
    max_dist = np.max(colorvec)
    if max_dist == 0: # 全ての距離が0の場合（完全に一致）
        colorvec = np.ones_like(colorvec)
    else:
        colorvec = 1 - colorvec / max_dist 
        
    return colorvec.reshape(-1, 1)

# 印象変換行列 A↓
# 行：元気，友情，注意，安らぎ，明るい，暗い，冷静
# 列：赤，橙，黄，緑，青，紫，ピンク，白，グレー，黒
A = np.array([
    [0.5, 1, 1, 1, 0, 0, 1, 1, 0, -1],  # 明るい
    [0, -1, -1, 0, 0.5, 0, -1, -1, 0.5, 1],  # 暗い
    [0, 0.5, 0.5, 0, 0, 0, 1, 0, 0, 0],  # かわいい
    [0, -1, -1, 0, 1, 0, -1, 0, 1, 1],  # 悲しい
    [1, 1, 0.5, -1, -1, 0.5, 0, 0, 0, 0],  # 情熱
    [-1, -1, -1, 0.5, 1, 0, 0, 0.5, 0.5, 0.5], # 冷静
    [0, 0.5, 0.5, 1, 0, 0, 0, 0, 0, 0]   # 自然
], dtype=np.float32)


# 印象語のリスト（行列Aの行））
impression_words = ["明るい", "暗い", "かわいい", "悲しい", "情熱", "冷静", "自然"]


# Streamlit アプリのメイン処理↓
st.title("画像の色彩印象分析アプリ")
st.write("画像データを入れれば，その画像の色彩に基づく印象を表す語を出力します")
st.write("このアプリは，**画像の色を表すベクトル**と，**色と印象の関係を表す行列**の積によって，印象のスコアを算出している")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption='アップロードされた画像', use_column_width=True)

    if st.button("印象を分析"):
        
        # 画像の平均RGBを抽出
        mean_rgb = ext_mean_rgb(uploaded_file)
        st.write(f"画像の平均RGB値: R={mean_rgb[0]:.2f}, G={mean_rgb[1]:.2f}, B={mean_rgb[2]:.2f}")

        # 色ベクトルを生成
        x = gen_color_vec(mean_rgb)
        # st.write("生成された色ベクトル（パレット色との類似度）:")
        # st.write(x.T) # 横長のベクトルとして表示

        # 印象スコアを計算 (行列とベクトルの積)
        # y = A・x
        impression_scores = np.dot(A, x)
        
        st.subheader("分析結果：色彩に基づく印象スコア")
        
        # 結果をDataFrameに変換して表示
        import pandas as pd 
        scores_df = pd.DataFrame(impression_scores, index=impression_words, columns=['スコア'])
        st.dataframe(scores_df)

        # 最もスコアが高い印象を特定
        max_score_idx = np.argmax(impression_scores)
        most_impression_word = impression_words[max_score_idx]
        most_impression_score = impression_scores[max_score_idx][0]

        st.success(f"この画像から最も強く想起される印象は「**{most_impression_word}**」です (スコア: {most_impression_score:.2f})")
