import os
import sys
import pandas as pd
from styleframe import StyleFrame, utils, Styler
def generate_excel_table():
    df = pd.read_json(f"{os.getcwd()}{os.sep}output{os.sep}musics.json")
    df = df.rename(columns={
        'title': 'Título',
        'image_url': 'Link da Imagem',
        'author': 'Autor',
        'publication_date': 'Data da Publicação',
        'download_url': 'Link de Download'
    })
    writer = StyleFrame.ExcelWriter(f"{os.getcwd()}{os.sep}output{os.sep}cds_melody_brasil.xlsx")

    sf = StyleFrame(df)

    sf.set_column_width('Título', 55)
    sf.set_column_width('Link da Imagem', 65)
    sf.set_column_width('Autor', 40)
    sf.set_column_width('Data da Publicação', 50)
    sf.set_column_width('Link de Download', 80)

    sf.apply_column_style(cols_to_style=df.columns,
                          styler_obj=Styler(bg_color=utils.colors.white, bold=False, font=utils.fonts.arial,
                                            font_size=12), style_header=True, )
    sf.apply_column_style(cols_to_style=['Link da Imagem', 'Link de Download'],
                          styler_obj=Styler(font_color=utils.colors.blue, font_size=10))
    sf.apply_headers_style(styler_obj=Styler(font_size=14, bold=True, font=utils.fonts.arial))

    sf.to_excel(writer, sheet_name='Sheet1')
    writer.close()
