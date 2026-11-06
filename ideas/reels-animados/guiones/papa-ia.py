# Reel animado · El Papa eligió su nombre pensando en la IA (visita de León XIV a Uruguay, 6 al 8/11/2026)
# Fuentes: discurso al Colegio Cardenalicio del 10/5/2025 (Xataka, Forbes Argentina); agenda en Uruguay (El Observador, Infobae).
ESCENAS = [
    dict(tipo='gancho', dur=3.8, etiqueta='YO TAMPOCO SABÍA', px=112, lineas=[[('El Papa eligió', False)], [('su nombre pensando', False)], [('en la ', False), ('inteligencia', True)], [('artificial.', True)]]),
    dict(tipo='frase', dur=4.4, px=104, lineas=[[('Se llama León XIV', False)], [('por ', False), ('León XIII', True), (',', False)]], chico='el papa que en 1891 escribió sobre la primera revolución industrial.', chico_t=1.0),
    dict(tipo='frase', dur=4.4, px=104, lineas=[[('Y en su primer', False)], [('discurso dijo que', False)], [('hoy vivimos ', False), ('otra', True), (':', False)]], chico='la de la inteligencia artificial.', chico_t=1.4),
    dict(tipo='frase', dur=3.8, px=104, lineas=[[('Este fin de semana', False)], [('está en ', False), ('Uruguay', True), ('.', False)]], chico='Montevideo, Paysandú y Florida, del 6 al 8 de noviembre.', chico_t=0.9),
    dict(tipo='cierre', dur=4.4, px=96, lineas=[[('¿La IA nos saca', False)], [('trabajo o nos', False)], [('saca ', False), ('tareas', True), ('?', False)]], caja='CONTAME', caja_t=1.4),
]
