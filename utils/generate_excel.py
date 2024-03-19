import os
import sys
import pandas as pd
from styleframe import StyleFrame, utils, Styler


def generate_excel_table():
    df = pd.read_json(f"{os.getcwd()}{os.sep}output{os.sep}musics.json")
    print(df.columns)
    df = df.rename(columns={
        'title': 'Título',
        'author': 'Publicado por',
        'publication_date': 'Data da Publicação',
        'download_url': 'Link de Download',
        'url_publication': 'Url da Publicação',
        'image_url': 'Link da Imagem'
    })
    writer = StyleFrame.ExcelWriter(f"{os.getcwd()}{os.sep}output{os.sep}cds_melody_brasil.xlsx")

    sf = StyleFrame(df)

    sf.set_column_width('Título', 55)
    sf.set_column_width('Link da Imagem', 65)
    sf.set_column_width('Publicado por', 40)
    sf.set_column_width('Data da Publicação', 50)
    sf.set_column_width('Url da Publicação', 50)
    sf.set_column_width('Link de Download', 80)

    sf.apply_column_style(cols_to_style=df.columns,
                          styler_obj=Styler(bg_color=utils.colors.white, bold=False, font=utils.fonts.arial,
                                            font_size=12), style_header=True, )
    sf.apply_column_style(cols_to_style=['Link da Imagem', 'Link de Download', 'Url da Publicação'],
                          styler_obj=Styler(font_color=utils.colors.blue, font_size=10))
    sf.apply_headers_style(styler_obj=Styler(font_size=14, bold=True, font=utils.fonts.arial))

    sf.to_excel(writer, sheet_name='Melody Brasil CDs')
    writer.close()

