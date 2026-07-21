# -*- coding: utf-8 -*-
"""
Genera BITACORA.pdf a partir de BITACORA.md (misma carpeta).

Uso:  python generar_bitacora.py

Se edita SIEMPRE el .md y se vuelve a ejecutar esto. El PDF es solo para leer/imprimir.
Requiere: pip install reportlab
"""
import os
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                               Spacer, HRFlowable, ListFlowable, ListItem)

CARPETA = os.path.dirname(os.path.abspath(__file__))
ORIGEN = os.path.join(CARPETA, 'BITACORA.md')
DESTINO = os.path.join(CARPETA, 'BITACORA.pdf')

AZUL = colors.HexColor('#4472c4')
AZUL_OSCURO = colors.HexColor('#2e5fa3')
GRIS = colors.HexColor('#555555')

_estilos = getSampleStyleSheet()


def _st(nombre, **kw):
    base = dict(fontName='Times-Roman', fontSize=10.5, leading=14.5, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(nombre, parent=_estilos['Normal'], **base)


TITULO = _st('T', fontName='Times-Bold', fontSize=20, leading=24, alignment=1, spaceAfter=2)
SUBTITULO = _st('S', fontSize=11, alignment=1, textColor=GRIS, spaceAfter=14)
H1 = _st('H1', fontName='Times-Bold', fontSize=15, leading=19, textColor=AZUL_OSCURO,
         spaceBefore=16, spaceAfter=7)
H2 = _st('H2', fontName='Times-Bold', fontSize=12, leading=16, textColor=AZUL,
         spaceBefore=11, spaceAfter=5)
CUERPO = _st('C', alignment=TA_JUSTIFY)
CITA = _st('Q', fontSize=9.5, leading=13, textColor=GRIS, leftIndent=10, spaceBefore=4)
VINETA = _st('V', alignment=TA_JUSTIFY, spaceAfter=3)


# Las fuentes internas del PDF (Times) no traen emojis: saldrían como cuadros negros.
# Se reemplazan por equivalentes en texto. Cualquier otro símbolo raro se descarta.
REEMPLAZOS = {
    '✅': '[OK]', '❌': '[X]', '⚠': '[!]', '✔': '[OK]',
    '→': '->', '←': '<-', '⇒': '=>',
    '☁': '[nube]', '\U0001F512': '[candado]', '•': '-',
    '‘': "'", '’': "'", '“': '"', '”': '"',
    '…': '...', ' ': ' ',
}


def limpiar_glifos(t):
    for viejo, nuevo in REEMPLAZOS.items():
        t = t.replace(viejo, nuevo)
    # Fuera todo lo que Times no puede dibujar (emojis, pictogramas, flechas raras)
    return ''.join(c for c in t if ord(c) < 0x2100 or c in '–—')


def escapar(t):
    t = limpiar_glifos(t)
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def enriquecer(t):
    """Convierte **negrita**, *cursiva* y `código` del Markdown a etiquetas de ReportLab."""
    t = escapar(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'<font face="Courier" size="9">\1</font>', t)
    return t


def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 8)
    canvas.setFillColor(GRIS)
    canvas.drawString(20 * mm, 12 * mm, 'Análisis de Procesos Críticos — Bitácora de trabajo')
    canvas.drawRightString(letter[0] - 20 * mm, 12 * mm, 'Página %d' % doc.page)
    canvas.setStrokeColor(colors.HexColor('#cccccc'))
    canvas.line(20 * mm, 15 * mm, letter[0] - 20 * mm, 15 * mm)
    canvas.restoreState()


def construir():
    with open(ORIGEN, encoding='utf-8') as f:
        lineas = f.read().split('\n')

    historia = []
    vinetas = []          # acumula ítems de una lista para emitirlos juntos
    numerada = False

    def cerrar_lista():
        nonlocal vinetas, numerada
        if not vinetas:
            return
        historia.append(ListFlowable(
            [ListItem(Paragraph(v, VINETA), leftIndent=14) for v in vinetas],
            bulletType='1' if numerada else 'bullet',
            bulletFontName='Times-Roman', bulletFontSize=9,
            leftIndent=16, spaceAfter=7))
        vinetas = []
        numerada = False

    primera = True
    for linea in lineas:
        l = linea.rstrip()

        if l.startswith('# '):
            cerrar_lista()
            historia.append(Paragraph(enriquecer(l[2:]), TITULO))
            historia.append(Paragraph(
                'Generado el ' + datetime.now().strftime('%d-%m-%Y a las %H:%M'), SUBTITULO))
            historia.append(HRFlowable(width='100%', color=AZUL, thickness=1.2, spaceAfter=10))
            primera = False
        elif l.startswith('### '):
            cerrar_lista()
            historia.append(Paragraph(enriquecer(l[4:]), H2))
        elif l.startswith('## '):
            cerrar_lista()
            if not primera:
                historia.append(Spacer(1, 6))
            historia.append(Paragraph(enriquecer(l[3:]), H1))
            historia.append(HRFlowable(width='100%', color=colors.HexColor('#dddddd'),
                                       thickness=0.7, spaceAfter=8))
        elif l.startswith('> '):
            cerrar_lista()
            historia.append(Paragraph(enriquecer(l[2:]), CITA))
        elif l.startswith('---'):
            cerrar_lista()
        elif re.match(r'^\s*[-*] ', l):
            item = re.sub(r'^\s*[-*] ', '', l)
            if numerada:
                cerrar_lista()
            vinetas.append(enriquecer(item))
        elif re.match(r'^\s*\d+\. ', l):
            item = re.sub(r'^\s*\d+\. ', '', l)
            if vinetas and not numerada:
                cerrar_lista()
            numerada = True
            vinetas.append(enriquecer(item))
        elif l.strip() == '':
            cerrar_lista()
        else:
            # Continuación de una viñeta (línea indentada bajo un ítem)
            if vinetas and linea.startswith('   '):
                vinetas[-1] += ' ' + enriquecer(l.strip())
            else:
                cerrar_lista()
                historia.append(Paragraph(enriquecer(l), CUERPO))

    cerrar_lista()

    doc = BaseDocTemplate(DESTINO, pagesize=letter,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=18 * mm, bottomMargin=22 * mm,
                          title='Bitácora — Análisis de Procesos Críticos',
                          author='V División — Ejército de Chile')
    marco = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='n')
    doc.addPageTemplates([PageTemplate(id='base', frames=marco, onPage=pie)])
    doc.build(historia)
    print('PDF generado: %s' % DESTINO)


if __name__ == '__main__':
    construir()
