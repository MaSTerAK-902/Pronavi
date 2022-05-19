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

config_ini = configparser.ConfigParser()
config_ini.read('./config/html_config.ini',encoding = 'utf-8')

HTML_Text_File = open('./config/htmltemplate.txt','r',encoding='UTF-8', newline='').read()
#未検証 : Repalceが機能していない可能性有り
HTML_TXT_File = HTML_Text_File.replace("\n", "")

Read_Columns = config_ini.getint('DEFAULT','Columns')
#変更予定 : テキスト側のプレースホルダーの数から確認に変更
Read_Header_Name = config_ini.get('DEFAULT','Header')

#追加予定 : 変数名の見直し 処理方法の見直し 要改善箇所
Pandas_Read_Noheader = pd.read_csv('input_file.csv', header = None)
Pandas_Read_Dataframe = pd.read_csv('input_file.csv')
Df_Rows_Count = len(Pandas_Read_Dataframe)
Pandas_Count = 0

for r in range(Df_Rows_Count):
    Read_Tempo_List = []

    for c in range(Read_Columns):
        Read_Tempo_List.append(Pandas_Read_Noheader[c][r + 1])

    HTML_Add_Data = Repalce_Word(Read_Tempo_List)
    Pandas_Read_Dataframe = Pandas_Read_Dataframe.replace(Pandas_Count , {Read_Header_Name : HTML_Add_Data})
    Pandas_Count += 1

Pandas_Read_Dataframe.to_csv('otuput_I_file.csv')
    
################################## メインの処理 ##################################
Setting_Tree_Root = ET.parse('./config/InitialSetting.xml').getroot()
#追加予定 : 取込みファイルを検査(エラーはコマンドと.logに出力すること)

Serch_Auction_Navi = pd.read_csv('./config/Auction_Navi_Template.csv')
Auction_Navi = pd.read_csv('./config/Auction_Navi_Template.csv', header = None)
AuctionNavi_Columns_Count = len(Auction_Navi.columns)
#追加予定 : 取込みファイルを検査(エラーはコマンドと.logに出力すること)

Input_File_NoHeader = pd.read_csv('otuput_I_file.csv',header = None)
Input_File = pd.read_csv('otuput_I_file.csv')
InputFile_Rows_Count = len(Input_File)
#追加予定 : 取込みファイルを検査(エラーはコマンドと.logに出力すること)

Output_Csv_Add_Dataframe = []

for i in range(InputFile_Rows_Count):
    Add_Tempo_Dataframe = []
    
    for n in range(AuctionNavi_Columns_Count) :
        
        Auction_Navi_Word_List = list(Input_File.get(Auction_Navi[n][0], ['None']))
        
        if Auction_Navi_Word_List != ['None'] and isinstance(Auction_Navi_Word_List[i], float) != True:
            Add_Tempo_Dataframe.insert(n, Auction_Navi_Word_List[i])    
        else :
            Set_Branch_Flag = False
            
            for Set_Tree in Setting_Tree_Root:
                
                if Set_Tree.findtext("Set_Name") == Auction_Navi[n][0]:
                    Add_Tempo_Dataframe.insert(n, Set_Tree.findtext("Set_Data"))
                    Set_Branch_Flag = True
                    break
                    
            if Set_Branch_Flag == False:
                Add_Tempo_Dataframe.insert(n, '')
                
    Output_Csv_Add_Dataframe.append(Add_Tempo_Dataframe)

df = pd.DataFrame(Output_Csv_Add_Dataframe, columns = pd.read_csv('./config/Auction_Navi_Template.csv').columns.tolist())
#変更予定 : エンコーディングは利用者側で指定できるように変数を設定
df.to_csv('output.csv',index = False , encoding='shift-jis')
Time_Now = datetime.datetime.now()
Output_Filename = './output/output_' + Time_Now.strftime('%Y%m%d') + '.zip'

#追加予定 : 指定した画像を全てzipファイルに保存
with zipfile.ZipFile(Output_Filename,'w') as zf:
    zf.write('output.csv')

os.remove('otuput_I_file.csv')
os.remove('output.csv')