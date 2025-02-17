# 天下一 Game Battle Contest 2022

- [公式サイト](https://tenka1.klab.jp/2022/)
- [YouTube配信](https://www.youtube.com/watch?v=JNwDmtjbu0A)

## 問題概要

- [問題概要およびAPI仕様](problem.md)
- [チュートリアル](tutorial.md)
- [Runnerの使い方](runner.md)
- [ビジュアライザの使い方](visualizer.md)

## ポータルサイト

コンテストの参加に必要なAPIトークンの発行、運営への質問、ランキング、お知らせの確認ができます。

ユーザ登録は、ユーザIDとパスワードの設定のみで完了します。

[天下一 Game Battle Contest 2022 ポータルサイト](https://2022contest.gbc.tenka1.klab.jp/portal/index.html)

- [ポータルサイトの使い方](portal.md)

## サンプルコード

- [Go](go)
- [Python](py)
- [C#](cs)
- [Rust](rust)
- [C++(libcurl)](cpp) 通信にライブラリを使用
- [C++(Python)](cpp_and_python) 通信にPythonを使用


動作確認環境はいずれも Ubuntu 20.04 LTS

## ルール

- コンテスト期間
  - 2022年9月23日(金・祝)
    - 予選リーグ: 14:00～18:00
    - 決勝リーグ: 18:00～18:20
    - ※予選リーグ終了後、上位8名による決勝リーグを開催
- 参加資格
  - 学生、社会人問わず、どなたでも参加可能です。他人と協力せず、個人で取り組んでください。
- 使用可能言語
  - 言語の制限はありません。ただしHTTPSによる通信ができる必要があります。
- SNS等の利用について
  - 本コンテスト開催中にSNS等にコンテスト問題について言及して頂いて構いませんが、ソースコードを公開するなどの直接的なネタバレ行為はお控えください。
ハッシュタグ: #klabtenka1

## その他

- [ギフトカード抽選プログラム](lottery/lottery.py) (key.txtは当選者決定後に公開します)
  - 抽選対象は join API で開始したゲームに一度以上 move API を実行した参加者です
