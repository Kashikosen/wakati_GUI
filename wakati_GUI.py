#wakati_GUI.py      GUI実装テスト
#NEologd    /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd
#文節分かち書き　参考：https://qiita.com/shimajiroxyz/items/e44058af8b036f5354aa

#coding: utf-8
import PySimpleGUI as sg
import threading
import MeCab



class Context:

    def __init__(self):
        self.wakati_txt = ''
        self.hinshi_result = ''
        self.tango_wakati_result = ''
        self.bunsetu_wakati_result = ''

    ###文字入力GUI###
    def create_text_gui(self):

        #レイアウト
        layout = [
            [sg.Text('分かち書きシステム', font=('小塚ゴシック Pro B', 24), text_color='#ffffff')],
            [sg.Text('入力欄')],
            [sg.Multiline(default_text='', size=(120,10),
                          border_width=2, key='text1',
                          text_color='#000000', background_color='#ffffff')],
            [sg.Text(' ')],
            [sg.Text(' ')],
            [sg.Text('品詞分析結果')],
            [sg.Multiline(default_text='', size=(120,10), key = 'hinshi_result',
                          text_color='#000000', background_color='#aacccc',
                          disabled=True, auto_refresh=True)],
            [sg.Text(' ')],
            [sg.Text('単語　分かち書き')],
            [sg.Multiline(default_text='', size=(120,10), key = 'tango_wakati_result',
                          text_color='#000000', background_color='#aacccc',
                          disabled=True, auto_refresh=True)],
            [sg.Text('文節　分かち書き')],
            [sg.Multiline(default_text='', size=(120,10), key = 'bunsetu_wakati_result',
                          text_color='#000000', background_color='#aacccc',
                          disabled=True, auto_refresh=True)],
            [sg.Button('Read(⌘r)', key='bt_read'), sg.Button('Clear(⌘l)', key='bt_clear'), sg.Button('Quit(⌘q)', key='bt_quit')]
            ]

        #ウィンドウ作成
        window = sg.Window('wakati_GUI.py', layout, return_keyboard_events=True)


        #イベントループ
        while True:
            event, values = window.read()       #イベントの読み取り（イベント待ち）
            #print('イベント：', event, ',  値：', values)       #確認表示

            #Return表記整える
            if event is not None and event.startswith('Return'):
               event = 'Return'
               print(event)

            #各種ボタン
            if event == None or event == 'bt_quit' or event == 'q' and ('Meta_L' or 'Meta_R'):
                print('quit')
                break

            elif event == 'bt_read' or event == 'r' and ('Meta_L' or 'Meta_R') or event.startswith('Return'):
                #print(values['text1'])
                self.wakati_txt = values['text1']
                print(self.wakati_txt)
                #別スレッドで実行
                threading.Thread(target=self.hinshi, args=(window,), daemon=True).start()
                threading.Thread(target=self.tango_wakati, args=(window,), daemon=True).start()
                threading.Thread(target=self.bunsetu_wakati, args=(window,), daemon=True).start()

            elif event == 'bt_clear' or event == 'l' and ('Meta_L' or 'Meta_R'):
                print('clear')
                window['text1'].update('')
                self.tango_wakati_result = ''
                #GUIに反映
                window['tango_wakati_result'].update(self.tango_wakati_result)

        #終了表示
        window.close()
    ###



    ###品詞表示###
    def hinshi(self, window):
        if self.wakati_txt.strip():
            tagger = MeCab.Tagger("-d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
            self.hinshi_result = str(tagger.parse(self.wakati_txt))
            print(self.hinshi_result)
            #GUIに反映
            window['hinshi_result'].update(self.hinshi_result)
        
        else:
            self.hinshi_result = '※対象が存在しません'
            print(self.hinshi_result)
            #GUIに反映
            window['hinshi_result'].update(self.hinshi_result)



    ###単語分かち書き###
    def tango_wakati(self, window):
        if self.wakati_txt.strip():
            tagger = MeCab.Tagger("-Owakati -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
            #tagger = MeCab.Tagger()
            tango_wakati_result = tagger.parse(self.wakati_txt)
            self.tango_wakati_result = ' / '.join(tango_wakati_result.split())
            print(self.tango_wakati_result)
            #GUIに反映
            window['tango_wakati_result'].update(self.tango_wakati_result)

        else:
            self.tango_wakati_result = '※対象が存在しません'
            print(self.tango_wakati_result)
            #GUIに反映
            window['tango_wakati_result'].update(self.tango_wakati_result)
    ###



    ###文節分かち書き###
    def bunsetu_wakati(self, window):
        if self.wakati_txt.strip():
            tagger = MeCab.Tagger("-d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
            bunsetu_hinshi_result = tagger.parse(self.wakati_txt).splitlines()
            bunsetu_hinshi_result = bunsetu_hinshi_result[:-1]            # 最後の1行は不要なので取り除く
            break_pos = ['名詞','動詞','接頭詞','副詞','感動詞','形容詞','形容動詞','連体詞']       # 文節の切れ目検出
            bunsetu_wakati_result = ['']       # 分かち書きリスト
            afterPrepos = False         # 接頭詞の直後かどうかのフラグ
            afterSahenNoun = False      # サ変接続名詞の直後かどうかのフラグ

            # 文節区切り
            for v in bunsetu_hinshi_result:
                if '\t' not in v: continue
                surface = v.split('\t')[0]          #表層系
                pos = v.split('\t')[1].split(',')   #品詞など
                pos_detail = ','.join(pos[1:4])     #品詞細分類（各要素の内部がさらに'/'で区切られていることがあるので、','でjoinして、inで判定する)

                #単語が文節の切れ目とならないかどうかの判定
                noBreak = pos[0] not in break_pos
                noBreak = noBreak or '接尾' in pos_detail
                noBreak = noBreak or (pos[0]=='動詞' and 'サ変接続' in pos_detail)
                noBreak = noBreak or '非自立' in pos_detail     #非自立な名詞、動詞を文節の切れ目としたい場合はこの行をコメントアウトする
                noBreak = noBreak or afterPrepos
                noBreak = noBreak or (afterSahenNoun and pos[0]=='動詞' and pos[4]=='サ変・スル')
                if noBreak == False:
                    bunsetu_wakati_result.append("")
                bunsetu_wakati_result[-1] += surface
                afterPrepos = pos[0]=='接頭詞'
                afterSahenNoun = 'サ変接続' in pos_detail
            if bunsetu_wakati_result[0] == '': bunsetu_wakati_result = bunsetu_wakati_result[1:]        #最初が空文字のとき削除する
            # 文字列に変換
            self.bunsetu_wakati_result = ' / '.join(bunsetu_wakati_result)
            print(self.bunsetu_wakati_result)
            # GUIに反映
            window['bunsetu_wakati_result'].update(self.bunsetu_wakati_result)
        
        else:
            self.bunsetu_wakati_result = '※対象が存在しません'
            print(self.bunsetu_wakati_result)
            #GUIに反映
            window['bunsetu_wakati_result'].update(self.bunsetu_wakati_result)
    ###
            




context = Context()
context.create_text_gui()