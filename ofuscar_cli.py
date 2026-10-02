import sys
import fitz  # PyMuPDF


def redactar_pdf(input_path: str, output_path: str):
    doc = fitz.open(input_path)

    for page in doc:
        rect_page = page.rect
        h = rect_page.height

        limite_derecho = 230.0
        fechas = page.search_for("Fecha y Hora")
        if fechas:
            limite_derecho = fechas[0].x0 - 5.0

        instancias = page.search_for("45509582")
        if not instancias:
            instancias = page.search_for("MOISES CEFERINO")

        if instancias:
            for inst in instancias:
                rect_area = fitz.Rect(
                    inst.x0 - 2,
                    inst.y0 - 2,
                    min(inst.x0 + 220, limite_derecho),
                    inst.y1 + 1,
                )
                page.add_redact_annot(rect_area, fill=(1, 1, 1))
        else:
            rect_fijo = fitz.Rect(
                15, h - 55, min(220, limite_derecho), h - 38
            )
            page.add_redact_annot(rect_fijo, fill=(1, 1, 1))

        page.apply_redactions()

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python ofuscar_cli.py <entrada.pdf> <salida.pdf>")
        sys.exit(1)
    redactar_pdf(sys.argv[1], sys.argv[2])
