document.addEventListener('DOMContentLoaded', () => {
    // Inicializar fecha si existe el elemento
    const dateElement = document.getElementById('current-date');
    if (dateElement) {
        const today = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        const dateStr = today.toLocaleDateString('es-MX', options);
        dateElement.textContent = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
    }

    // Ejecutar Paginación con un retraso para asegurar carga de estilos
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
    if (pageNum > 20) return;

    const contentWrapper = page.querySelector('.content-wrapper');
    const footer = page.querySelector('footer');
    if (!contentWrapper || !footer) return;

    // Use getBoundingClientRect so we cope with relative positioning accurately
    const pageRect = page.getBoundingClientRect();
    const footerRect = footer.getBoundingClientRect();

    // Calculate footer top relative to the page container
    let relativeFooterTop = footerRect.top - pageRect.top;

    // IMPORTANT: Fix for "Touching Footer" issue.
    // Screen view allows .page-container to expand (min-height). 
    // Print view forces fixed height (27.94cm -> ~1056px).
    // If container expanded, footer is pushed down, so we must clamp the limit to valid Print area.
    const MAX_PRINT_HEIGHT = 1050; // Approx 27.94cm minus safety
    if (pageRect.height > MAX_PRINT_HEIGHT) {
        // Simulate footer position on a fixed-height page
        // Footer is bottom: 1rem (approx 16px).
        const estimatedFooterBottom = MAX_PRINT_HEIGHT - 16;
        const estimatedFooterTop = estimatedFooterBottom - footerRect.height;
        relativeFooterTop = Math.min(relativeFooterTop, estimatedFooterTop);
    }

    // Determine buffer.
    // Added .photo-placeholder to check since actual images might be missing in templates
    const hasImages = contentWrapper.querySelector('.images-column, .photo-grid, .photo-placeholder');
    const buffer = 50; // Maintain a healthy buffer (approx 1.3cm)

    // Define the limit where content must stop
    const limit = relativeFooterTop - buffer;

    const children = Array.from(contentWrapper.children).filter(el =>
        el.nodeType === 1 && el !== footer && el.tagName !== 'SCRIPT' && !el.classList.contains('top-bar')
    );


    const firstContentIdx = children.findIndex(c => c.tagName !== 'HEADER' && !c.classList.contains('top-bar'));

    for (let i = 0; i < children.length; i++) {
        const child = children[i];
        if (child.tagName === 'HEADER' || child.classList.contains('top-bar')) continue;

        const childRect = child.getBoundingClientRect();
        const relativeBottom = childRect.bottom - pageRect.top;

        // Caso: Salto de página forzado
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

        if (relativeBottom > limit) {
            // CASO: Tablas (pueden dividirse)
            if (child.classList.contains('table-container') || child.classList.contains('table-container-alcance-table')) {
                const table = child.querySelector('table');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));

                for (let r = 0; r < rows.length; r++) {
                    const rowRect = rows[r].getBoundingClientRect();
                    if ((rowRect.bottom - pageRect.top) > limit) {
                        if (r === 0 && i > firstContentIdx) {
                            // Mover bloque completo
                            const newPage = createNewPageFrom(page);
                            const nextNum = pageNum + 1;
                            updatePageCounter(newPage, nextNum);
                            moveSiblingsToPage(children.slice(i), newPage);
                            await new Promise(r => setTimeout(r, 50));
                            await checkPageOverflow(newPage, nextNum);
                            return;
                        }

                        let splitIndex = (r === 0) ? 1 : r;
                        if (splitIndex >= rows.length && i === firstContentIdx) return;

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

            // CASO: Form Section (puede contener Grids de fotos o Tablas)
            if (child.classList.contains('form-section')) {
                const innerElements = Array.from(child.children).filter(el => !el.classList.contains('section-title-bar'));

                for (let e = 0; e < innerElements.length; e++) {
                    const innerEl = innerElements[e];
                    const elRect = innerEl.getBoundingClientRect();

                    if ((elRect.bottom - pageRect.top) > limit) {
                        // Si es el primer elemento del form-section y no estamos al inicio de la página, mover SECCIÓN COMPLETA
                        if (e === 0 && i > firstContentIdx) {
                            const newPage = createNewPageFrom(page);
                            const nextNum = pageNum + 1;
                            updatePageCounter(newPage, nextNum);
                            moveSiblingsToPage(children.slice(i), newPage);
                            await new Promise(r => setTimeout(r, 50));
                            await checkPageOverflow(newPage, nextNum);
                            return;
                        }

                        // Si el elemento interno es un GRID o IMAGE COLUMN, intentar dividirlo
                        const isGrid = innerEl.classList.contains('photo-grid') || innerEl.classList.contains('images-column');
                        if (isGrid) {
                            const gridItems = Array.from(innerEl.children);
                            for (let j = 0; j < gridItems.length; j++) {
                                const itemRect = gridItems[j].getBoundingClientRect();
                                if ((itemRect.bottom - pageRect.top) > limit) {
                                    let splitGridIdx = (j === 0) ? 1 : j;
                                    if (splitGridIdx >= gridItems.length) break; // Si no se puede dividir el grid, se moverá el bloque según lógica siguiente

                                    const newPage = createNewPageFrom(page);
                                    const nextNum = pageNum + 1;
                                    updatePageCounter(newPage, nextNum);

                                    const targetCW = newPage.querySelector('.content-wrapper');
                                    const targetFooter = targetCW.querySelector('footer');

                                    // Clonar la estructura de la sección en la nueva página
                                    const newSection = child.cloneNode(true);
                                    Array.from(newSection.children).forEach(nc => {
                                        if (nc.classList.contains('section-title-bar')) {
                                            nc.querySelector('.section-header-text').textContent += " (Cont.)";
                                        } else { nc.remove(); }
                                    });
                                    targetCW.insertBefore(newSection, targetFooter);

                                    // Crear nuevo contenedor de grid dentro de la nueva sección
                                    const newGrid = innerEl.cloneNode(false);
                                    newSection.appendChild(newGrid);
                                    gridItems.slice(splitGridIdx).forEach(item => newGrid.appendChild(item));

                                    // Mover elementos restantes del form-section
                                    innerElements.slice(e + 1).forEach(rem => newSection.appendChild(rem));
                                    // Mover hermanos del form-section original
                                    moveSiblingsToPage(children.slice(i + 1), newPage);

                                    await new Promise(r => setTimeout(r, 50));
                                    await checkPageOverflow(newPage, nextNum);
                                    return;
                                }
                            }
                        }

                        // Fallback: Dividir la sección moviendo este elemento y los siguientes
                        const newPage = createNewPageFrom(page);
                        const nextNum = pageNum + 1;
                        updatePageCounter(newPage, nextNum);

                        const targetCW = newPage.querySelector('.content-wrapper');
                        const targetFooter = targetCW.querySelector('footer');
                        const newSection = child.cloneNode(true);
                        Array.from(newSection.children).forEach(nc => {
                            if (nc.classList.contains('section-title-bar')) {
                                nc.querySelector('.section-header-text').textContent += " (Cont.)";
                            } else { nc.remove(); }
                        });
                        targetCW.insertBefore(newSection, targetFooter);

                        innerElements.slice(e).forEach(em => newSection.appendChild(em));
                        moveSiblingsToPage(children.slice(i + 1), newPage);

                        await new Promise(r => setTimeout(r, 50));
                        await checkPageOverflow(newPage, nextNum);
                        return;
                    }
                }
            }

            // CASO: Bloque indivisible o genérico
            if (i === firstContentIdx) {
                console.warn("Bloque irreductible. Se permite desbordamiento.");
                return;
            }

            const newPage = createNewPageFrom(page);
            const nextNum = pageNum + 1;
            updatePageCounter(newPage, nextNum);

            // Especial para Financial Group: intentar mover última fila de tabla previa
            let elementsToMove = children.slice(i);
            const isFin = child.classList.contains('financial-group') || child.classList.contains('financial-summary');
            if (isFin) {
                const prevTable = children.slice(0, i).reverse().find(el => el.classList.contains('table-container'));
                if (prevTable) {
                    const rows = Array.from(prevTable.querySelector('tbody').querySelectorAll('tr'));
                    if (rows.length > 0) {
                        moveTableRowsToPage([rows[rows.length - 1]], newPage, prevTable);
                    }
                }
            }

            moveSiblingsToPage(elementsToMove, newPage);
            await new Promise(r => setTimeout(r, 50));
            await checkPageOverflow(newPage, nextNum);
            return;
        }
    }
}

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
    selectors.forEach(sel => {
        contentWrapper.querySelectorAll(sel).forEach(e => e.remove());
    });

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

        // Fix: Evitar duplicidad del financial-summary.
        // Al clonar, el summary pasa a la nueva página. Lo eliminamos de la página anterior
        // para que solo aparezca al final de la tabla (en la última página).
        const oldSummary = originalContainer.querySelector('.financial-summary');
        if (oldSummary) {
            oldSummary.remove();
        }
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
