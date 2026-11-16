---
name: pdf-watermark-remover
description: "Remove an authorized watermark from a PDF while preserving its original text, images, layout, and pages. Use this skill whenever a user asks to remove, delete, strip, clear, or export a PDF without a watermark, including a resume, invoice, draft, or document with a visible translucent/diagonal watermark."
compatibility: "Requires Python 3 with pypdf and a PDF renderer such as Poppler pdftoppm."
---

# PDF Watermark Remover

Use this workflow only for a document the user is authorized to alter. Preserve the source PDF and make a separately named output file.

## Outcome

Deliver a non-watermarked PDF at the destination requested by the user. Before delivery, prove both of these:

1. The script removed only PDF objects marked as watermarks.
2. Every output page renders cleanly with the original page count and layout intact.

## Quick workflow

1. Resolve the source PDF and requested output location. Do not overwrite the source. If the user asks for the desktop, write a descriptive `_无水印.pdf` / `_no_watermark.pdf` file there.
2. Inspect the source visually before editing. Render every page, not just page one:

   ```bash
   mkdir -p work/pdfs
   pdftoppm -png -r 150 "$SOURCE_PDF" work/pdfs/source
   ```

   Use the bundled Poppler path if `pdftoppm` is not on `PATH`.
3. Run the bundled script. It finds direct page-content invocations of Form XObjects explicitly tagged `/Private /Watermark`, then creates an incremental PDF update that removes only those invocations. Incremental writing is deliberate: broad `pypdf` document rewrites can damage complex WeasyPrint/WPS content streams.

   ```bash
   python3 scripts/remove_form_watermark.py "$SOURCE_PDF" "$OUTPUT_PDF"
   ```

4. Reopen and render the output:

   ```bash
   pdfinfo "$OUTPUT_PDF"
   pdftoppm -png -r 150 "$OUTPUT_PDF" work/pdfs/clean
   ```

   Compare every rendered page against the source. Check that the watermark is gone and that text, images, margins, headers, footers, page breaks, and page count remain intact.
5. If the script reports no tagged watermark or rejects the PDF, stop. Explain the reason and use a format-specific, non-destructive investigation rather than deleting arbitrary text or painting white rectangles over the page.

## Safety and handling rules

- Do not remove a watermark merely by matching visible words: the same words can appear in the document body.
- Do not rasterize/rebuild a page as the default. That needlessly harms selectable text, links, and visual quality.
- Do not process encrypted or digitally signed PDFs with this script. A signed PDF’s signature is invalidated by editing, and password-protected files need an explicit user-provided access path.
- Keep watermark resources in the PDF if they become unreachable. Removing their page references is the smallest safe change and is sufficient to remove their visual effect.
- Never replace the source PDF. If an output path already exists, ask before overwriting it unless the user explicitly asked to regenerate that exact file.

## How the script decides what to remove

The script operates only when all of the following are true:

- a page’s content stream invokes a Form XObject with the `Do` operator;
- that exact Form XObject has `/PieceInfo /ADBE_CompoundType /Private /Watermark`; and
- the invocation is direct in a page content stream.

This handles common Acrobat/WPS watermarks, including nested forms such as `KSPX2 -> KSPX1`. It removes the outer direct call (for example, `/KSPX2 Do`), leaving photos and regular form/image content alone.

## Verification checklist

- Read the script’s JSON report: `removed_references` must be positive and equal to the number of removed direct watermark calls.
- Reopen the output with `pypdf`; the report must say `remaining_direct_watermark_references: 0`.
- Confirm `pdfinfo` reports the same number of pages and page dimensions as the source.
- Inspect all rendered output pages. Do not deliver if they show missing/shifted text, clipped elements, overlays, black blocks, or a remaining watermark.

## Final response

State that the watermark was removed, give the resulting file, and mention that the pages were visually verified. For a PDF artifact, cite the output PDF once using the environment’s file-citation format.
