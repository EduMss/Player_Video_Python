import vlc #pip install python-vlc
import PySimpleGUI as sg #pip install PySimpleGUI
import os
from sys import platform as PLATFORM
import time

ListaVideos = []
Abrir = ""

class Procurar_Videos:
    def __init__(self):
        self.formatosAceitos = [".mp4", ".mov", ".wmv", ".avi"]
    
    def func(self,ListaVideos):
        ListaVideos.clear()
        for file in os.listdir(os.path.dirname(__file__)):
            for formato in self.formatosAceitos:
                if file.endswith(formato):
                    ListaVideos.append(file)

Procurar = Procurar_Videos()
Procurar.func(ListaVideos=ListaVideos)


class PlayerVideo:
    def __init__(self, Video):
        self.caminhoVideo = os.path.join(os.path.dirname(__file__), Video)

        layout = [
            [sg.Image('', size=(300, 170), key='-VID_OUT-')],
            [sg.Slider(range=(0, 1), enable_events=True, resolution=0.0001, disable_number_display=True,
                       background_color='#83D8F5', orientation='h', key='TimeProgresso')],#, size=(0,15))],
            [sg.Text('00:00', key='TimeNumero')],
            [sg.Button("button", key="parar")]
        ]

        self.window = sg.Window(title="Player de Video", layout=layout, element_justification='center', finalize=True, resizable=True)
        self.window['-VID_OUT-'].expand(True, True)  
        self.window['TimeProgresso'].expand(True, True)  

        self.inst = vlc.Instance()
        self.list_player = self.inst.media_list_player_new()
        self.media_list = self.inst.media_list_new([self.caminhoVideo])
        self.list_player.set_media_list(self.media_list)
        self.player = self.list_player.get_media_player()

        if PLATFORM.startswith('linux'):
            self.player.set_xwindow(self.window['-VID_OUT-'].Widget.winfo_id())
        else:
            self.player.set_hwnd(self.window['-VID_OUT-'].Widget.winfo_id()) 

        self.list_player.play()


    def AtualizandoInfo(self):
        tempoAssistido = "{:02d}:{:02d}".format(*divmod(self.player.get_time() // 1000, 60))
        tempoTotal = "{:02d}:{:02d}".format(*divmod(self.player.get_length() // 1000, 60))

        self.window['TimeProgresso'].update(self.player.get_position())
        self.window['TimeNumero'].update(f'{tempoAssistido} / {tempoTotal}')


    def funcoes(self):
        rodando = True
        iniciar = True
        while rodando:
            while iniciar:
                time.sleep(0.1)
                if self.player.is_playing:
                    self.AtualizandoInfo()
                    iniciar = False
                    break
            
            self.event, self.value = self.window.read(timeout=1000)
            

            if self.event == sg.WIN_CLOSED:
                rodando = False
                break

            elif self.event == "parar":
                print("Botão parar " + self.caminhoVideo)
                rodando = False
                break

            elif self.event == "TimeProgresso":
                self.player.set_rate(self.value['TimeProgresso'])
            
            elif self.player.is_playing:
                self.AtualizandoInfo()

                
            
class TelaInicial:
    def __init__(self):
        layout = [
            [sg.Button("button", key="parar")],
            [sg.Listbox(values=ListaVideos, size=(30, 6), key='List')],
            [sg.Button("abrir", key="abrir")]
        ]

        self.window = sg.Window("Player de Video").Layout(layout)

    def funcoes(self):
        rodando = True
        while rodando:
            self.event, self.value = self.window.read()

            if self.event == sg.WIN_CLOSED:
                rodando = False
                break

            elif self.event == "parar":
                print("Botão parar")
                rodando = False
                break

            elif self.event == "abrir":
                Video = self.window['List']
                Video = str(Video.get())
                    
                #--------------------------------------------------
                #n sei se vai preicsar quando eu pegar o texto dentro do arquivo, ou eu vou procurar o outro metodo, q so apaga o final e o inicio e eu escolho quantos espaços são apagados
                Bugs = ('[',']',"'")
                for Bug in Bugs:
                    index = Bugs.index(Bug)
                    if Bugs[index] in Video:
                        Video = Video.replace(Bugs[index], '')
                #--------------------------------------------------
                Abrir = "PlayerVideo"
                rodando = False
                break

        if Abrir == "PlayerVideo":
            self.window.close()
            PlayerVideo(Video).funcoes()


if __name__ == '__main__':
    TelaInicial().funcoes()

