# note → X 日次投稿 運用手順（RUNBOOK）

毎朝の予約タスクがこの手順に従って、その日の投稿をBufferに**下書き**として登録する。
投稿の承認（Add to Queue）は massa が Buffer アプリで行う。**Claude は絶対にキュー登録・即時投稿をしない。**

## 固定情報

- note：https://note.com/telos_eros_ethos （RSS：https://note.com/telos_eros_ethos/rss）
- Buffer 組織「My organization」：`6b07675f5098443dec0a2c3d`
- Buffer チャンネル（X / @masitango）：`6b07682d8541f09ecba525a7`
- 投稿時刻：毎日 12:15 JST（Buffer のキュー設定。承認された下書きがこの枠で出る）
- 画像置き場：このリポジトリ `masitango-star/note-x-cards` の `cards/`
- 投稿履歴：このリポジトリの `history.csv`
- 日付は常に JST で扱う

## 手順

1. **重複防止**：Buffer の `list_posts`（status: draft, scheduled）と `history.csv` を見て、今日の日付の投稿が既にあれば何もせず終了する。
2. **形式を決める（A/Bテスト）**：`(今日 − 2026-11-26)` の日数が偶数なら `link`、奇数なら `thread`。
3. **記事を選ぶ**：RSS を取得し、次の優先順で1本選ぶ。
   - まだ一度も紹介していない記事（新着を最優先）
   - 次に、紹介回数が少なく、最後に紹介した日が古い記事
   - 直近14日に紹介した記事は避ける（記事が足りないときだけ緩める）
   - 固定記事「自己紹介 vol.1」は対象外
4. **本文を読む**：記事URLを取得して本文を読む。引用は必ず本文から**原文のまま**取る。
   - 1〜2文、全角で25〜60字程度。文の途中で切らない（文単位で短くするのは可）
   - `history.csv` で同じ記事に使った引用は使わない
   - 記事の主張が伝わる一文を選ぶ（前置きや接続の文は避ける）
5. **投稿文を作る**（ハッシュタグ・絵文字・煽り文句は使わない。体言止めや問いで締める massa の論考の文体に合わせる）
   - `link` 形式（1投稿）：
     ```
     <記事の一節（原文のまま）>

     <記事が投げかける問い・要点を1〜2文>

     ▼note「<記事タイトル>」
     <記事URL>
     ```
     URL込みで X の上限（日本語140字相当、URLは23字換算）に収める。
   - `thread` 形式（2投稿）：
     - 1投稿目：記事の問題提起を2〜3文で（引用カードの文と同じ文は使わない）＋引用カード画像
     - 2投稿目：`続きはnoteで▼` ＋ 改行 ＋ `「<記事タイトル>」` ＋ 改行 ＋ `<記事URL>`
6. **引用カード（thread の日のみ）**：
   - `python3 scripts/make_card.py "<引用>" "<記事タイトル>" cards/YYYY-MM-DD.png`
   - 出来上がった画像を Read で目視確認。単語の途中で改行されて不自然なら、引用に `\n`（実際の改行）を入れて再生成する。**文字そのものは変えない。**
   - commit して push。画像URLはキャッシュ回避のため**コミットIDで固定した** raw URL を使う：
     `https://raw.githubusercontent.com/masitango-star/note-x-cards/<commit SHA>/cards/YYYY-MM-DD.png`
   - `curl` で 200 が返ることを確認してから Buffer に渡す。
   - 代替テキスト（altText）：`引用：<引用>（note「<記事タイトル>」並木将仁）`
7. **Buffer に下書き登録**：`create_post` を `saveToDraft: true`、`schedulingType: automatic` で呼ぶ。
   - thread 形式は `text` に1投稿目、`metadata.twitter.thread` に2投稿すべて（1投稿目に画像）を入れる。
   - `mode`・`dueAt` は指定しない。**キュー登録・即時投稿は絶対にしない。**
8. **履歴を記録**：`history.csv` に1行追記（date, format, article_url, article_title, quote, buffer_post_id, note）して commit・push。
9. **終了報告**：最後のメッセージを短く。形式、記事名、引用（または冒頭文）、そして「Bufferで確認して Add to Queue で12:15に投稿されます」。

## 失敗時

- 画像の生成・push・URL確認のどれかに失敗した → その日は `link` 形式で下書きを作り、`history.csv` の note 欄に理由を書く。報告でも一言伝える。
- Buffer の呼び出しが失敗した → 1回だけ再試行。それでも駄目なら、作った投稿文を報告に載せて終了（massa が手で入れられるように）。
- RSS や記事本文が取れない → 1回再試行。駄目なら履歴にある過去の記事と引用を使い回さず、報告で状況を伝えて終了。

## A/Bテストの評価（2026-12-10 以降）

- 2026-12-10 以降の実行では、下書き作成に加えて、2026-11-26 以降に送信済みの投稿の数字を `list_posts`（includeMetrics: true）で取り、`link` と `thread` の平均（表示回数、エンゲージメント、リンククリックなど取れる指標）を比べて報告の末尾に短く添える。
- 形式の切り替えは massa が決める。決まるまでは日替わりを続ける。
