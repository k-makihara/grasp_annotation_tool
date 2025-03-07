import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

def rectangle_w_angle(x, y, width, height, angle_deg):
    """
    指定された始点 (x,y) から，幅 width, 高さ height, 角度 angle_deg（度）で回転矩形の頂点を計算する。
    戻り値は 2×4 の numpy 配列で，
      第一行：各頂点の x 座標，
      第二行：各頂点の y 座標
    順番は v1=(x,y), v2, v3, v4 の順とする。
    """
    theta = np.deg2rad(angle_deg)
    # 第一頂点
    v1 = np.array([x, y])
    # v1 から幅方向 (cosθ, sinθ) に width 分進む
    v2 = v1 + np.array([width * np.cos(theta), width * np.sin(theta)])
    # 幅方向に垂直な単位ベクトルは (-sinθ, cosθ)
    perp = np.array([-np.sin(theta), np.cos(theta)])
    # v1 から高さ方向に height 分進んだ点
    v4 = v1 + height * perp
    # v2 から同じ高さ方向に進んだ点
    v3 = v2 + height * perp
    # 各頂点を 2×4 の配列として返す
    vertices = np.column_stack((v1, v2, v3, v4))
    return vertices

def annotate_image(im, ax):
    """
    画像上で３点（順に左上、幅方向の点、高さ方向の点）をクリックして回転矩形を作成する．  
    クリックした座標から幅、角度、高さを計算し、矩形の頂点を描画・返す。
    """
    # ユーザーから 3 点を取得（タイムアウトなし）
    pts = plt.ginput(3, timeout=-1)
    if len(pts) < 3:
        return None
    (x, y), (x2, y2), (x3, y3) = pts

    # 幅の計算（1点目と2点目間の距離）
    width = np.sqrt((x - x2) ** 2 + (y - y2) ** 2)
    # 角度の計算（ラジアン→度へ変換）
    angle = np.arctan2((y2 - y), (x2 - x)) * 180 / np.pi
    # 高さは 2 点目と 3 点目の距離
    height = np.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)

    # クリック位置や線分を描画（マーカーサイズは適宜調整）
    ax.plot(x, y, 'ro', markersize=5)
    ax.plot([x, x2], [y, y2], '-ro', markersize=5, linewidth=2)
    # 回転矩形の頂点を取得
    vertices = rectangle_w_angle(x, y, width, height, angle)
    # 頂点を連結して矩形を描く（最初の頂点に戻る）
    xs = list(vertices[0, :]) + [vertices[0, 0]]
    ys = list(vertices[1, :]) + [vertices[1, 0]]
    ax.plot(xs, ys, '-g', linewidth=2)
    plt.draw()
    return vertices

def main():
    print("start")
    # 画像と注釈保存用ディレクトリのパス設定
    imgDataDir = 'data/Images/'
    annoDataDir = 'data/Annotations/'
    if not os.path.exists(annoDataDir):
        os.makedirs(annoDataDir)
    # 指定ディレクトリ内の png ファイル一覧を取得
    imgFiles = glob.glob(os.path.join(imgDataDir, '*.png'))

    # 各画像について処理
    for imgPath in imgFiles:
        # 画像ファイル名（拡張子なし）を取得
        base = os.path.basename(imgPath)
        imgname, _ = os.path.splitext(base)

        # 画像を読み込み
        im = plt.imread(imgPath)

        # 注釈ファイルを新規作成（上書きモード）
        anno_filename = os.path.join(annoDataDir, imgname + '_annotations.txt')
        anno_file = open(anno_filename, 'w')

        # GUI 表示の準備
        fig, ax = plt.subplots()
        # ウィンドウタイトルの設定（任意）
        fig.canvas.manager.set_window_title(imgname)
        # 下部にボタン表示のため余白を確保
        plt.subplots_adjust(bottom=0.2)
        ax.imshow(im)
        ax.set_title('Annotate image: ' + imgname)

        # Next ボタンの作成（押すとウィンドウを閉じて次の画像へ移行）
        axnext = plt.axes([0.8, 0.05, 0.1, 0.075])
        btn_next = Button(axnext, 'Next')

        def next_callback(event):
            plt.close(fig)

        btn_next.on_clicked(next_callback)

        # ユーザーが Next ボタンを押すまで複数の矩形を注釈
        while plt.fignum_exists(fig.number):
            vertices = annotate_image(im, ax)
            if vertices is None:
                break
            # 各矩形の頂点（2×4 配列）を 4 行分（1頂点ずつ）テキストファイルに保存
            for i in range(4):
                # 書式は "x y"（Cornell dataset と同様）
                anno_file.write(f"{vertices[0, i]} {vertices[1, i]}\n")
            plt.pause(2)  # 次の矩形注釈まで 2 秒ポーズ

        anno_file.close()
        plt.close('all')

if __name__ == "__main__":
    main()
