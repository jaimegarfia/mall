--------------------------- COPIAR DESDE AQUI HASTA EL FINAL (NO HAY QUE SUSTITUIR NADA MANUALMENTE SI USAS EL SCRIPT) -------------------------------

Necesito crear una apartado "Modelo de datos" para el readme de mi microservicio JAVA. Para ello te paso las principales entidades de mi microservicio

Tu objetivo es generar el apartado "Modelo de datos" en base a los datos de ENTIDADES_JSON

REGLAS IMPORTANTES (debes cumplirlas estrictamente):
1) Devuelve SOLO el Markdown del apartado "Modelo de datos". No añadas explicación, introducción, ni texto fuera del formato.
2) No envuelvas la respuesta en bloques de código (no uses ```).
3) No inventes atributos/campos que no aparezcan en ENTIDADES_JSON.
4) Si no puedes inferir con seguridad la descripción de una entidad o atributo, escribe literalmente: "Sin descripción".
5) Respeta exactamente la estructura y la indentación del formato indicado en FORMATO_EXAMPLE.

START ENTIDADES_JSON

{{ENTIDADES_JSON}}

END ENTIDADES_JSON


Este es el formato que debe tener tu resultado. Ten en cuenta solo el formato para tu respuesta. 

START FORMATO_EXAMPLE

#### 3. NOMBRE_ENTIDAD

-   Descripción: DESCRIPCION_ENTIDAD
-   Atributos:
    -   `NOMBRE_ATRIBUTO_1`: DESCRIPCION_ATRIBUTO_1
    -   `NOMBRE_ATRIBUTO_2`: DESCRIPCION_ATRIBUTO_2
    -   `NOMBRE_ATRIBUTO_3`: DESCRIPCION_ATRIBUTO_3
    -   `NOMBRE_ATRIBUTO_4`: DESCRIPCION_ATRIBUTO_4

END FORMATO_EXAMPLE

Para que tu respuesta sea considerada como correcta debe respetar esta estructura pero con los datos del apartado ENTIDADES_JSON
