import io
import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(
    page_title="Ofuscador de Reportes Sentinel", page_icon="📄", layout="centered"
)

st.title("📄 Ofuscador de Reportes Sentinel")
st.write(
    "Sube el reporte en PDF para eliminar tus datos personales de la esquina inferior izquierda."
)


def redactar_pdf(pdf_bytes: bytes) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page in doc:
        rect_page = page.rect
        h = rect_page.height

        # Localizamos dónde empieza "Fecha y Hora" para nunca cruzar esa barrera horizontal
        limite_derecho = 230.0  # margen seguro por defecto
        fechas = page.search_for("Fecha y Hora")
        if fechas:
            limite_derecho = fechas[0].x0 - 5.0

        # Buscamos las instancias del DNI o nombre
        instancias = page.search_for("45509582")
        if not instancias:
            instancias = page.search_for("MOISES CEFERINO")

        if instancias:
            for inst in instancias:
                # Ofuscamos únicamente la altura de esa línea, sin tocar la línea inferior
                rect_area = fitz.Rect(
                    inst.x0 - 2,
                    inst.y0 - 2,
                    min(inst.x0 + 220, limite_derecho),
                    inst.y1 + 1,  # Muy ajustado para no invadir la línea de "Fecha..."
                )
                page.add_redact_annot(rect_area, fill=(1, 1, 1))
        else:
            # Respaldo posicional en la esquina inferior izquierda (solo la franja del nombre)
            rect_fijo = fitz.Rect(
                15,
                h - 55,  # Línea superior (donde está el DNI y nombre)
                min(220, limite_derecho),
                h - 38,  # Termina justo antes de "Fecha y Hora de creación"
            )
            page.add_redact_annot(rect_fijo, fill=(1, 1, 1))

        # Aplica la eliminación permanentemente
        page.apply_redactions()

    output_stream = io.BytesIO()
    doc.save(output_stream, garbage=4, deflate=True)
    doc.close()
    return output_stream.getvalue()


uploaded_file = st.file_uploader(
    "Selecciona el reporte PDF", type=["pdf"], accept_multiple_files=False
)

if uploaded_file is not None:
    if st.button("Procesar y Ofuscar PDF", type="primary"):
        with st.spinner("Ofuscando información sensible..."):
            pdf_bytes = uploaded_file.read()
            pdf_procesado = redactar_pdf(pdf_bytes)

            nombre_salida = uploaded_file.name.replace(".pdf", "_Reporte_Sentinel.pdf")
            st.success("¡Documento procesado correctamente!")
            st.download_button(
                label="⬇️ Descargar PDF Ofuscado",
                data=pdf_procesado,
                file_name=nombre_salida,
                mime="application/pdf",
            )
