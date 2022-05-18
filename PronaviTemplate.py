#競りナビ出品リストの自動作成機能
import csv
import pandas as pd
import configparser
import zipfile
import datetime
import os
import xml.etree.ElementTree as ET

################################## HTMLデータをCSVに追加する ##################################
def Repalce_Word(data):
    result = HTML_TXT_File.format(*data)
    return result

#HTML_Config.ini の読み込み
config_ini = configparser.ConfigParser()
config_ini.read('./config/html_config.ini',encoding = 'utf-8')

#Memo : HTML用データフレームの作成
HTML_TXT_File = open('./config/htmltemplate.txt','r',encoding='UTF-8', newline='').read()
Read_Columns = config_ini.getint('DEFAULT','Columns')
Read_Header_Name = config_ini.get('DEFAULT','Header')

#TBV : 変数名の見直し 処理方法の見直し
Pandas_Read_Noheader = pd.read_csv('input_file.csv', header = None)
Pandas_Read_Dataframe = pd.read_csv('input_file.csv')
Df_Rows_Count = len(Pandas_Read_Dataframe)
Pandas_Count = 0

for r in range(Df_Rows_Count):
    Read_Tempo_List = []
    for c in range(Read_Columns):
        Read_Tempo_List.append(Pandas_Read_Noheader[c][r + 1])
    #Memo : HTMLからデータを読み取る Replace_Wordモジュールを使う
    HTML_Add_Data = Repalce_Word(Read_Tempo_List)
    Pandas_Read_Dataframe = Pandas_Read_Dataframe.replace(Pandas_Count , {Read_Header_Name : HTML_Add_Data})
    Pandas_Count += 1

Pandas_Read_Dataframe.to_csv('otuput_I_file.csv')
    
################################## メインの処理 ##################################
#XML設定ファイルの読み込み
Setting_Tree_Root = ET.parse('./config/InitialSetting.xml').getroot()
#Memo : 取込みファイルを検査(エラーはコマンドと.logに出力すること)

#競りナビテンプレートの情報を取得
Serch_Auction_Navi = pd.read_csv('./config/Auction_Navi_Template.csv')
Auction_Navi = pd.read_csv('./config/Auction_Navi_Template.csv', header = None)
AuctionNavi_Columns_Count = len(Auction_Navi.columns)
#Memo : 取込みファイルを検査(エラーはコマンドと.logに出力すること)

#インプットファイルの情報を取得
Input_File_NoHeader = pd.read_csv('otuput_I_file.csv',header = None)
Input_File = pd.read_csv('otuput_I_file.csv')
InputFile_Rows_Count = len(Input_File)
#Memo : 取込みファイルを検査(エラーはコマンドと.logに出力すること)

#競りナビテンプレートデータから出力用のデータフレームの作成
Output_Csv_Add_Dataframe = []

#メイン処理の記述
for i in range(InputFile_Rows_Count):
    #Memo ： 一時保存用のデータフレームの作成と初期化
    Add_Tempo_Dataframe = []
    
    for n in range(AuctionNavi_Columns_Count) :
        #Memo : 競りナビリストに順次追加していく
        #Memo : Getメソッドを使ってInput_File.csvからAuction_Naviのヘッダーと一致した列のみを抽出する。
        
        Auction_Navi_Word_List = list(Input_File.get(Auction_Navi[n][0], ['None']))
        
        if Auction_Navi_Word_List != ['None'] and isinstance(Auction_Navi_Word_List[i], float) != True:
            #Memo : Add_Tempo_Dataframeにデータを格納する。
            Add_Tempo_Dataframe.insert(n, Auction_Navi_Word_List[i])    
        else :
            Set_Branch_Flag = False
            #Memo : SettingTreeを解析して、指定列のデータを全て置き換えする。
            
            for Set_Tree in Setting_Tree_Root:
                
                if Set_Tree.findtext("Set_Name") == Auction_Navi[n][0]:
                    Add_Tempo_Dataframe.insert(n, Set_Tree.findtext("Set_Data"))
                    Set_Branch_Flag = True
                    break
                    
            #Memo : 空データをAdd_Tempo_Dataframeに追加する。
            if Set_Branch_Flag == False:
                Add_Tempo_Dataframe.insert(n, '')
                
    #Memo : Output_Csv_Add_Dataframe にAutction_Navi_Word_List[n]を追加する。 
    Output_Csv_Add_Dataframe.append(Add_Tempo_Dataframe)

#Memo : DataFrameを出力する処理（csvに出力 -> .zipにパッケージ -> csvを削除
df = pd.DataFrame(Output_Csv_Add_Dataframe, columns = pd.read_csv('./config/Auction_Navi_Template.csv').columns.tolist())
df.to_csv('output.csv',index = False , encoding='shift-jis')
Time_Now = datetime.datetime.now()
Output_Filename = './output/output_' + Time_Now.strftime('%Y%m%d') + '.zip'

#zipファイルに圧縮する（名称は作成時の日付を利用する）
with zipfile.ZipFile(Output_Filename,'w') as zf:
    zf.write('output.csv')
    
#Memo : ZIPファイルの削除
os.remove('otuput_I_file.csv')
os.remove('output.csv')