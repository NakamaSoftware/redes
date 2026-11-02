# R02 animado · Tres frases que cambian a ChatGPT (respaldo sin cara, mié 4/11 18:00)
ESCENAS = [
    dict(tipo='gancho', dur=3.2, etiqueta='GUARDALO', px=128, lineas=[[('Tres frases', False)], [('que ', False), ('cambian', True)], [('a ChatGPT.', False)]]),
    dict(tipo='cortinilla', dur=0.6, n='01'),
    dict(tipo='pedido', dur=3.9, etiqueta='PASO 01', pedido='Respondeme en 3 líneas.', alto=380, leyenda='Chau respuestas de 2 pantallas.', clave=['pantallas']),
    dict(tipo='cortinilla', dur=0.6, n='02'),
    dict(tipo='pedido', dur=4.6, etiqueta='PASO 02', pedido='Si no estás seguro de algo, decímelo antes de contestar.', alto=440, leyenda='Así no inventa.', clave=['inventa']),
    dict(tipo='cortinilla', dur=0.6, n='03'),
    dict(tipo='pedido', dur=4.1, etiqueta='PASO 03', pedido='Dame 3 opciones bien distintas.', alto=380, leyenda='Y elegís vos.', clave=['vos']),
    dict(tipo='cierre', dur=4.0, lineas=[[('Pegalas al final', False)], [('de cualquier pedido.', False)], [('Probá una hoy.', True)]], px=96, caja='GUARDALO', caja_t=1.3),
]
