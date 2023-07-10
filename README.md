# Onomation Backend

## 環境構築

ここでは比較的簡単に環境を構築できるvenvを使った方法を紹介する．

1.  まずプロジェクトのディレクトリに移動する
2.  venvの環境を構築する．環境名は何でも良い（例： `venv` ）
    ```
    python3 -m venv [環境名]
    ```
3.  作成した環境を有効化する
    ```
    source [環境名]/bin/activate
    ```
    ターミナルの表示が以下のようになっていれば環境が有効になっている
    ```
    ([環境名])$ 
    ```
4.  必要なパッケージをインストールする． `requirements.txt` に必要なパッケージをまとめたので，そこからインストールしてほしい．
    ```
    pip install -r requirements.txt
    ```
5.  [任意] 環境を無効にしたい場合は以下のコマンドを実行すれば良い
    ```
    deactivate
    ```

一旦環境を構築した後は3.と5.のみ使用する．

参考：[venv: Python 仮想環境管理](https://qiita.com/fiftystorm36/items/b2fd47cf32c7694adc2e)

## 使用したパッケージ