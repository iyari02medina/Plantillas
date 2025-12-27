/**
 * Archivo: paginacion.js
 * Descripción: Script centralizado para manejar la paginación dinámica.
 *              Incluye "Guillotina Lógica" para prevenir invasión de footer.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Inicialización de Fecha
    const dateElement = document.getElementById('current-date');
    if (dateElement) {
        const today = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        const dateStr = today.toLocaleDateString('es-MX', options);
        dateElement.textContent = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
    }

    // 2. Ejecutar Paginación con retraso
    setTimeout(paginateContent, 1000);
});

async function paginateContent() {
    const firstPage = document.querySelector('.page-container');
    if (!firstPage) return;

    await checkPageOverflow(firstPage, 1);

    const totalPages = document.querySelectorAll('.page-container').length;
    document.querySelectorAll('.total-pages').forEach(el => {
        el.textContent = totalPages;
    });
}

async function checkPageOverflow(page, pageNum) {
    if (!pageNum) pageNum = 1;
    if (pageNum > 20) return; // Evitar bucle infinito

    const contentWrapper = page.querySelector('.content-wrapper');
    const footer = page.querySelector('footer');
    if (!contentWrapper || !footer) return;

    const pageRect = page.getBoundingClientRect();

    // --- GUILLOTINA LÓGICA ---
    // Límite absoluto en píxeles desde el tope de la hoja.
    // Footer empieza aprox en 1020px-1074px (dependiendo del zoom/render).
    // Dejamos un buffer masivo: NADA debe pasar del pixel 850.
    const PIXEL_DE_LA_MUERTE = 850;

    // Para Grids de Imágenes aislados, permitimos un poco más de espacio
    const LIMITE_PERMISIVO_IMAGENES = 940;

    const children = Array.from(contentWrapper.children).filter(el =>
        el.nodeType === 1 && el !== footer && el.tagName !== 'SCRIPT' && !el.classList.contains('top-bar')
    );

    const firstContentIdx = children.findIndex(c => c.tagName !== 'HEADER' && !c.classList.contains('top-bar'));

    for (let i = 0; i < children.length; i++) {
        const child = children[i];
        if (child.tagName === 'HEADER' || child.classList.contains('top-bar')) continue;

        const childRect = child.getBoundingClientRect();
        const relativeBottom = childRect.bottom - pageRect.top;

        // Determinar límite para este elemento
        const esGridImagenes = child.querySelector('.images-column, .photo-grid') ||
            child.classList.contains('images-column') ||
            child.classList.contains('photo-grid');

        const limiteActual = esGridImagenes ? LIMITE_PERMISIVO_IMAGENES : PIXEL_DE_LA_MUERTE;

        // Caso: Salto de página forzado manual
        if (child.classList.contains('force-break')) {
            const nextSiblings = children.slice(i + 1);
            if (nextSiblings.length > 0) {
                const newPage = createNewPageFrom(page);
                const nextNum = pageNum + 1;
                updatePageCounter(newPage, nextNum);
                moveSiblingsToPage(nextSiblings, newPage);
                await new Promise(r => setTimeout(r, 50));
                await checkPageOverflow(newPage, nextNum);
                return;
            }
        }

        // --- VERIFICACIÓN DE DESBORDAMIENTO ---
        if (relativeBottom > limiteActual) {

            // EXCEPCIÓN: Grid de imágenes al inicio de página limpia
            if (esGridImagenes && i === firstContentIdx) {
                if (childRect.height < 700) {
                    console.warn("Grid invade zona de seguridad pero es el primero. Excepción permitida.");
                    continue;
                }
            }

            // ESTRATEGIA PRINCIPAL: Si no es el primero, MOVER TODO
            if (i > firstContentIdx) {
                console.log(`Elemento ${child.className} toca ${relativeBottom.toFixed(0)}px. Moviendo bloque completo.`);
                const newPage = createNewPageFrom(page);
                const nextNum = pageNum + 1;
                updatePageCounter(newPage, nextNum);
                moveSiblingsToPage(children.slice(i), newPage);
                await new Promise(r => setTimeout(r, 50));
                await checkPageOverflow(newPage, nextNum);
                return;
            }

            // ESTRATEGIA SECUNDARIA: Dividir internamente (porque está al inicio)

            // Sub-caso: Tablas
            if (child.classList.contains('table-container') || child.classList.contains('table-container-alcance-table')) {
                const table = child.querySelector('table');
                const rows = Array.from(table.tBodies[0].rows);
                for (let r = 0; r < rows.length; r++) {
                    if ((rows[r].getBoundingClientRect().bottom - pageRect.top) > limiteActual) {
                        const splitIndex = r === 0 ? 1 : r;
                        if (splitIndex >= rows.length) break;

                        const newPage = createNewPageFrom(page);
                        const nextNum = pageNum + 1;
                        updatePageCounter(newPage, nextNum);
                        moveTableRowsToPage(rows.slice(splitIndex), newPage, child);
                        moveSiblingsToPage(children.slice(i + 1), newPage);
                        await new Promise(r => setTimeout(r, 50));
                        await checkPageOverflow(newPage, nextNum);
                        return;
                    }
                }
            }

            // Sub-caso: Form Section (dividir hijos)
            if (child.classList.contains('form-section')) {
                const innerElements = Array.from(child.children).filter(el => !el.classList.contains('section-title-bar'));
                for (let e = 0; e < innerElements.length; e++) {
                    if ((innerElements[e].getBoundingClientRect().bottom - pageRect.top) > limiteActual) {

                        // PROTECCIÓN CONTRA BUCLE INFINITO
                        // Si es el PRIMER elemento interno el que se sale, y estamos en el PRIMER bloque de la página:
                        // Significa que este elemento por sí solo es más grande que el espacio permitido (850px).
                        // No podemos moverlo a la siguiente página porque pasará exactamente lo mismo.
                        // Debemos permitir que desborde (break) o intentar dividirlo si fuera un grid (ya manejado arriba).
                        if (e === 0) {
                            console.warn("Elemento interno gigante al inicio de página. No se puede dividir más. Aceptando desborde.");
                            break;
                        }

                        const newPage = createNewPageFrom(page);
                        const nextNum = pageNum + 1;
                        updatePageCounter(newPage, nextNum);

                        // Clonar estructura y mover
                        const targetCW = newPage.querySelector('.content-wrapper');
                        const targetFooter = targetCW.querySelector('footer');
                        const newSection = child.cloneNode(true);
                        // Limpiar clon
                        Array.from(newSection.children).forEach(nc => {
                            if (nc.classList.contains('section-title-bar')) nc.querySelector('.section-header-text').textContent += " (Cont.)";
                            else nc.remove();
                        });
                        targetCW.insertBefore(newSection, targetFooter);

                        // Mover hijos desde el punto de corte
                        innerElements.slice(e).forEach(item => newSection.appendChild(item));
                        // Mover hermanos del bloque padre
                        moveSiblingsToPage(children.slice(i + 1), newPage);

                        await new Promise(r => setTimeout(r, 50));
                        await checkPageOverflow(newPage, nextNum);
                        return;
                    }
                }
            }

            // Si llegamos aquí, es un bloque gigante indivisible al inicio.
            console.warn("Bloque irreductible gigante al inicio. Nada que hacer.");
        }
    }
}

// --- FUNCIONES AUXILIARES ---

function updatePageCounter(page, num) {
    const val = page.querySelector('.page-val');
    if (val) val.textContent = num;
}

function createNewPageFrom(originalPage) {
    const newPage = originalPage.cloneNode(true);
    const contentWrapper = newPage.querySelector('.content-wrapper');
    const selectors = [
        '.client-card', '.main-section', '.table-container', '.financial-summary',
        '.financial-group', '.images-column', '.table-container-alcance-table',
        '.form-section', '.closing-section', '.volumen-container'
    ];
    selectors.forEach(sel => contentWrapper.querySelectorAll(sel).forEach(e => e.remove()));
    document.body.appendChild(newPage);
    return newPage;
}

function moveTableRowsToPage(rows, targetPage, originalContainer) {
    const cw = targetPage.querySelector('.content-wrapper');
    const footer = cw.querySelector('footer');
    let targetContainer = cw.querySelector('.' + Array.from(originalContainer.classList).join('.'));

    if (!targetContainer) {
        targetContainer = originalContainer.cloneNode(true);
        targetContainer.querySelector('tbody').innerHTML = '';
        cw.insertBefore(targetContainer, footer);
        const oldSummary = originalContainer.querySelector('.financial-summary');
        if (oldSummary) oldSummary.remove();
    }
    const tbody = targetContainer.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));
}

function moveSiblingsToPage(elements, targetPage) {
    const cw = targetPage.querySelector('.content-wrapper');
    const footer = cw.querySelector('footer');
    elements.forEach(el => {
        if (el.nodeType === 1 && el.tagName !== 'SCRIPT' && el !== footer) {
            cw.insertBefore(el, footer);
        }
    });
}
