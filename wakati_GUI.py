#coding: utf-8
import PySimpleGUI as sg
import threading
import MeCab



class Context:

    def __init__(self):
        self.wakachi_txt = ''
        self.wakachi_result = ''

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
            [sg.Text('分かち書き結果')],
            [sg.Multiline(default_text='', size=(120,10), key = 'wakachi_result',
                          text_color='#000000', background_color='#aacccc',
                          disabled=True, auto_refresh=True)],
            [sg.Button('read', key='bt_read'), sg.Button('clear', key='bt_clear'), sg.Button('Quit', key='bt_quit')]
            ]

        #ウィンドウ作成
        window = sg.Window('wakati_GUI.py', layout, return_keyboard_events=True)

        #イベントループ
        while True:
            event, values = window.read()       #イベントの読み取り（イベント待ち）
            print('イベント：', event, ',  値：', values)       #確認表示

            #Return表記整える
            if event.startswith('Return'):
               event = 'Return'
               print(event)

            #各種ボタン
            if event == None or event == 'bt_quit' or event == 'q' and ('Meta_L' or 'Meta_R'):
                print('quit')
                break

            elif event == 'bt_read' or event == 'r' and ('Meta_L' or 'Meta_R') or event.startswith('Return'):
                #print(values['text1'])
                self.wakachi_txt =  values['text1']
                print(self.wakachi_txt)
                #分かち書きを別スレッドで実行
                threading.Thread(target=self.wakachi, args=(window,), daemon=True).start()

            elif event == 'bt_clear' or event == 'c' and ('Meta_L' or 'Meta_R'):
                print('clear')
                window['text1'].update('')
                self.wakachi_result = ''
                #GUIに反映
                window['wakachi_result'].update(self.wakachi_result)

        #終了表示
        window.close()
    ###



    ###分かち書き###
    def wakachi(self,window):
        if self.wakachi_txt.strip():
            tagger = MeCab.Tagger("-Owakati")
            self.wakachi_result = str(tagger.parse(self.wakachi_txt))
            print(self.wakachi_result)
            #GUIに反映
            window['wakachi_result'].update(self.wakachi_result)

        else:
            self.wakachi_result = '※対象が存在しません'
            print(self.wakachi_result)
            #GUIに反映
            window['wakachi_result'].update(self.wakachi_result)
    ###


context = Context()
context.create_text_gui()