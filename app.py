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


def redactar_pdf(pdf_bytes: bytes, texto_clave: str = "45509582") -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page in doc:
        # Altura y ancho de la página
        rect_page = page.rect
        h = rect_page.height

        # 1. Búsqueda directa del texto si es texto seleccionable
        instancias = page.search_for(texto_clave)
        if instancias:
            for inst in instancias:
                # Expandir ligeramente el rectángulo encontrado para cubrir el nombre completo si están en el mismo bloque
                rect_area = fitz.Rect(
                    inst.x0 - 5,
                    inst.y0 - 2,
                    min(inst.x0 + 350, rect_page.width / 2),
                    inst.y1 + 4,
                )
                page.add_redact_annot(rect_area, fill=(1, 1, 1))  # Fondo blanco
        else:
            # 2. Ofuscación posicional de respaldo en la esquina inferior izquierda
            # Ubicada entre los 30 y 60 puntos desde el fondo
            x0 = 15
            y0 = h - 60
            x1 = 280
            y1 = h - 35
            rect_fijo = fitz.Rect(x0, y0, x1, y1)
            page.add_redact_annot(rect_fijo, fill=(1, 1, 1))

        # Aplica la redacción permanentemente (elimina los metadatos y glifos del área)
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

            nombre_salida = uploaded_file.name.replace(".pdf", "_ofuscado.pdf")
            st.success("¡Documento procesado correctamente!")
            st.download_button(
                label="⬇️ Descargar PDF Ofuscado",
                data=pdf_procesado,
                file_name=nombre_salida,
                mime="application/pdf",
            )
