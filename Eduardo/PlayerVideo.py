import vlc #pip install python-vlc
import PySimpleGUI as sg #pip install PySimpleGUI
import os
from sys import platform as PLATFORM

# sg.theme_previewer()# visualizar todos os temas disponiveis

class Procurar_Assets:
    def __init__(self):
        self.caminho = os.path.join(os.path.dirname(__file__), "Assets")
        self.AssetsListaDic = {'pause':os.path.join(self.caminho,"pause_off.png"),
                                'arquivo':os.path.join(self.caminho,"arquivo-de-video-min.png"),
                                'pasta':os.path.join(self.caminho,"pasta-aberta-min.png"),
                                'icone':os.path.join(self.caminho,"video.ico"),
                                'play':os.path.join(self.caminho,"play_off.png"),
                                'playon':os.path.join(self.caminho,"start.png"),
                                'mute':os.path.join(self.caminho,"sound_off.png"),
                                'som':os.path.join(self.caminho,"sound_on.png"),
                                'stop':os.path.join(self.caminho,"stop.png")
                                }
    
    def getAssetsListaDic(self):
        return self.AssetsListaDic

AssetsListaDic = Procurar_Assets().getAssetsListaDic()

class PlayerVideo:
    def __init__(self, size, Video, tema):
        self.caminhoVideo = Video
        self.tema = tema #para ficar disponivel me toda a classe PlayerVideo
        self.player_size = [x*.85 for x in size]  # The size of the media output window
        self.cor_background = sg.LOOK_AND_FEEL_TABLE[self.tema]['BACKGROUND']

        layout = [
            [sg.Image('', size=self.player_size, pad=(0, 5), key='-VID_OUT-')],
            [sg.Slider(range=(0, 1), enable_events=True, resolution=0.0001, disable_number_display=True,
                       background_color='#83D8F5', orientation='h', key='TimeProgresso', relief='flat', border_width= 1)],

            [sg.Text('00:00', key='TimeNumero'),
             sg.Button(key="Pausar",image_filename=AssetsListaDic['pause'], border_width=0, pad=(0, 0), button_color=('white', self.cor_background)),
            sg.Button(key="Parar",image_filename=AssetsListaDic['stop'], border_width=0, pad=(0, 0), button_color=('white', self.cor_background)),
            sg.Button(key="Mutar",image_filename=AssetsListaDic['som'], border_width=0, pad=(0, 0), button_color=('white', self.cor_background)), 
            sg.Slider(range=(0, 100),default_value=80 , enable_events=True, resolution=1, disable_number_display=True,background_color='#83D8F5', orientation='h', key='Volume'),
            sg.Text('80%', key='PorcentagemVolume')]
        ]

        self.window = sg.Window(title="Player de Video", layout=layout, element_justification='center', finalize=True, resizable=True)
        self.window['-VID_OUT-'].expand(True, True)
        self.window['TimeProgresso'].expand(True, False)
        self.window.Maximize()

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


    def AtualizandoVideoInfo(self):
        if self.player.is_playing():
            Tempo = divmod(self.player.get_time() // 1000, 60)
            if Tempo[0] > 59:
                tempoHora = int(Tempo[0] / 60)
                Tempo = (Tempo[0] - (tempoHora*60), Tempo[1])
                tempoAssistido = "{:02d}:{:02d}:{:02d}".format(tempoHora,*Tempo)
            else:
                tempoAssistido = "{:02d}:{:02d}".format(*Tempo)
            
            Tempo = divmod(self.player.get_length() // 1000, 60)
            if Tempo[0] > 59:
                tempoHora = int(Tempo[0] / 60)
                Tempo = (Tempo[0] - (tempoHora*60), Tempo[1])
                tempoTotal = "{:02d}:{:02d}:{:02d}".format(tempoHora,*Tempo)
            else:
                tempoTotal = "{:02d}:{:02d}".format(*Tempo)

            self.window['TimeProgresso'].update(self.player.get_position())
            self.window['TimeNumero'].update(f'{tempoAssistido} / {tempoTotal}')

    def AtualizandoVolumeInfo(self, volume):
        volumePorcentagem = f'{volume}%'
        self.window['PorcentagemVolume'].update(value = volumePorcentagem)

    def VolumeInicial(self):
        self.event, self.value = self.window.read(timeout=1000)
        volume = self.value["Volume"]
        self.player.audio_set_volume(int(volume))

        
        if self.player.audio_get_mute():
            self.player.audio_set_mute(True)
            self.window['Mutar'].update(image_filename=AssetsListaDic['som'])


    def funcoes(self):
        rodando = True
        iniciar = True
        while rodando:
            while iniciar:
                if self.player.is_playing:
                    self.AtualizandoVideoInfo()
                    self.VolumeInicial()
                    volume = self.value["Volume"]
                    self.AtualizandoVolumeInfo(int(volume))
                    iniciar = False
                    break
            self.event, self.value = self.window.read(timeout=1000)
            self.AtualizandoVideoInfo()
            
            if self.event == sg.WIN_CLOSED:
                rodando = False
                break

            elif self.event == "parar":
                print("Botão parar " + self.caminhoVideo)
                rodando = False
                break

            elif self.event == "TimeProgresso":
                # self.player.set_rate(self.value['TimeProgresso'])
                self.player.set_position(self.value['TimeProgresso'])
                self.AtualizandoVideoInfo()

            elif self.event == "Volume":
                print(self.value["Volume"])
                volume = self.value["Volume"]
                self.player.audio_set_volume(int(volume))
                self.AtualizandoVolumeInfo(int(volume))
                
            elif self.event == "Mutar":
                self.player.audio_set_mute(not self.player.audio_get_mute())
                if self.player.audio_get_mute():
                    self.window['Mutar'].update(image_filename=AssetsListaDic['som'])
                    self.AtualizandoVolumeInfo(int(self.volume))
                    self.window['Volume'].update(self.volume)
                else:
                    self.window['Mutar'].update(image_filename=AssetsListaDic['mute'])
                    self.AtualizandoVolumeInfo(0)
                    self.volume = self.value["Volume"]
                    self.window['Volume'].update(0)

            elif self.event == "Pausar":
                self.AtualizandoVideoInfo()
                self.player.pause()
                if self.player.is_playing():
                    self.window['Pausar'].update(image_filename=AssetsListaDic['play'])
                else:
                    self.window['Pausar'].update(image_filename=AssetsListaDic['pause'])                

            elif self.event == "Parar":
                self.AtualizandoVideoInfo()
                if not self.player.is_playing():
                    self.window['Parar'].update(image_filename=AssetsListaDic['stop'])
                    self.player.play()
                else:
                    self.window['Parar'].update(image_filename=AssetsListaDic['playon'])
                    self.player.stop()
                    self.window['TimeProgresso'].update(0)
                    self.window['TimeNumero'].update(f'00:00 / 00:00')
                
                   
class TelaInicial:
    def __init__(self, tema='BrownBlue'):

        self.tema = tema #para ficar disponivel me toda a classe PlayerVideo
        sg.change_look_and_feel(self.tema)


        layout = [
            [sg.Input(disabled=True, key='-INPUT-'), 
             sg.Button(key='ArquivoVideo',image_filename=AssetsListaDic["arquivo"], image_size=(40,40)),
             sg.Button(key='NovaPasta',image_filename=AssetsListaDic["pasta"], image_size=(40,40))],
            [sg.Listbox(values=[], size=(30, 6), key='List')],
            [sg.Button("abrir", key="abrir", size=(5,2))]
        ]

        self.window = sg.Window("Player de Video", layout=layout, element_justification='center', finalize=True, resizable=True)
        self.window['List'].expand(True, True)
        self.window['abrir'].expand(True, False, False)

    def Procurar_Videos(self, pasta=None):
        self.formatosAceitos = [".mp4", ".mov", ".wmv", ".avi"]
        self.ListaVideos = []
        if pasta == None or pasta == "":
            for file in os.listdir(os.path.dirname(__file__)):
                for formato in self.formatosAceitos:
                    if file.endswith(formato):
                        self.ListaVideos.append(file)
            self.ListaCaminhoVideo = os.path.join(os.path.dirname(__file__))
            self.window['List'].update(self.ListaVideos)
        else : 
            for file in os.listdir(pasta):
                for formato in self.formatosAceitos:
                    if file.endswith(formato):
                        self.ListaVideos.append(file)
            self.ListaCaminhoVideo = os.path.join(pasta)
            self.window['List'].update(self.ListaVideos)

    def funcoes(self):
        self.Procurar_Videos()
        rodando = True
        while rodando:
            self.event, self.value = self.window.read(timeout=1000)
            if self.event == sg.WIN_CLOSED:
                rodando = False
                self.Abrir = ""
                break

            elif self.event == 'ArquivoVideo':
                file = sg.popup_get_file('', multiple_files=False, no_window=True)
                if file:
                    self.window.close()
                    self.caminhoVideo = os.path.join(self.ListaCaminhoVideo, file)
                    PlayerVideo(size=(1920,1080), Video = self.caminhoVideo, tema=self.tema).funcoes()
                else:
                    self.window['-INPUT-'].update('')

            elif self.event == 'NovaPasta':
                pasta = sg.popup_get_folder('', no_window=True)
                if pasta:
                    self.window['-INPUT-'].update(pasta)
                    self.Procurar_Videos(pasta)
                else:
                    self.window['-INPUT-'].update('')
                    self.Procurar_Videos()

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
                self.Abrir = "PlayerVideo"
                rodando = False
                break

        if self.Abrir == "PlayerVideo":
            self.window.close()
            self.caminhoVideo = os.path.join(self.ListaCaminhoVideo, Video)
            PlayerVideo(size=(1920,1080), Video = self.caminhoVideo, tema=self.tema).funcoes()


if __name__ == '__main__':
    TelaInicial().funcoes()

