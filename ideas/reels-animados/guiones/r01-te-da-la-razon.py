# R01 animado · ChatGPT siempre te da la razón (respaldo sin cara, mar 3/11 18:00)
ESCENAS = [
    dict(tipo='gancho', dur=3.4, etiqueta='CHATGPT', px=128, lineas=[[('ChatGPT siempre', False)], [('te dice que', False)], [('está buenísimo.', True)]]),
    dict(tipo='frase', dur=3.6, lineas=[[('No es verdad.', False)]], chico='Está entrenado para ser amable con vos, y pasa igual con Claude y con Gemini.', chico_t=0.8),
    dict(tipo='chat', dur=6.2, etiqueta='PEDILE ESTO', pedido='Decime los 3 puntos más débiles de mi idea, sin suavizarlo.', respuesta='renglones', n=3, numerada=True, alto=640),
    dict(tipo='frase', dur=3.8, lineas=[[('Probalo con tu ', False), ('currículum', True), (',', False)], [('el mail a tu jefe o esa', False)], [('idea de hace 2 meses.', False)]], px=96),
    dict(tipo='cierre', dur=4.0, lineas=[[('Guardalo para la próxima', False)], [('vez que te diga que', False)], [('está buenísimo.', True)]], px=96, caja='GUARDALO', caja_t=1.3),
]
