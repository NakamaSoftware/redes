# R05 animado · La IA no te avisa cuando no sabe (respaldo sin cara, jue 5/11 18:00)
ESCENAS = [
    dict(tipo='gancho', dur=3.2, etiqueta='OJO', px=128, lineas=[[('La IA no te', False)], [('avisa cuando', False)], [('no sabe.', True)]]),
    dict(tipo='chat', dur=5.6, etiqueta='UN EJEMPLO', pedido='¿A qué hora cierra la farmacia de Pocitos el domingo?', respuesta='Cierra a las 22.', sello='¿Y SI LO INVENTÓ?', alto=560),
    dict(tipo='frase', dur=3.4, px=100, lineas=[[('Te contesta con la', False)], [('misma seguridad,', False)], [('sepa o ', False), ('no sepa.', True)]]),
    dict(tipo='pedido', dur=4.8, etiqueta='AL FINAL DE TU PREGUNTA', pedido='Si no tenés el dato, decime que no sabés.', alto=380, leyenda='Sirve en ChatGPT, Claude y Gemini.', clave=['chatgpt', 'claude', 'gemini']),
    dict(tipo='frase', dur=3.4, px=100, lineas=[[('No es perfecto.', False)], [('Pero vas a ver', False)], [('muchos más ', False), ('no sé.', True)]]),
    dict(tipo='cierre', dur=3.8, lineas=[[('Guardalo, así la', False)], [('próxima te avisa.', True)]], px=100, caja='GUARDALO', caja_t=1.1),
]
