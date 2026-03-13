document.addEventListener("DOMContentLoaded", function () {
    function setupInlineSortable(inline) {
        var tbody = inline.querySelector("tbody");
        if (!tbody) return;

        var rows = Array.from(tbody.querySelectorAll("tr.form-row")).filter(function (row) {
            return !row.classList.contains("empty-form");
        });

        if (rows.length === 0) return;

        rows.forEach(function (row) {
            row.setAttribute("draggable", "true");
            if (!row.querySelector(".drag-handle")) {
                var firstCell = row.querySelector("td");
                if (firstCell) {
                    var handle = document.createElement("span");
                    handle.className = "drag-handle";
                    handle.title = "Déplacer";
                    handle.innerHTML = "↕";
                    firstCell.prepend(handle);
                }
            }
        });

        var dragSrc = null;

        function updateOrderInputs() {
            var orderedRows = Array.from(tbody.querySelectorAll("tr.form-row")).filter(function (row) {
                return !row.classList.contains("empty-form");
            });
            orderedRows.forEach(function (row, idx) {
                var input = row.querySelector('input[name$="-ordre"]');
                if (input) {
                    input.value = idx + 1;
                }
            });
        }

        tbody.addEventListener("dragstart", function (e) {
            var targetRow = e.target.closest("tr.form-row");
            if (!targetRow || targetRow.classList.contains("empty-form")) return;
            dragSrc = targetRow;
            targetRow.classList.add("dragging");
            e.dataTransfer.effectAllowed = "move";
        });

        tbody.addEventListener("dragover", function (e) {
            e.preventDefault();
            var targetRow = e.target.closest("tr.form-row");
            if (!targetRow || targetRow === dragSrc || targetRow.classList.contains("empty-form")) return;
            var rect = targetRow.getBoundingClientRect();
            var next = (e.clientY - rect.top) > (rect.height / 2);
            tbody.insertBefore(dragSrc, next ? targetRow.nextSibling : targetRow);
        });

        tbody.addEventListener("dragend", function () {
            if (dragSrc) {
                dragSrc.classList.remove("dragging");
            }
            dragSrc = null;
            updateOrderInputs();
        });
    }

    var inlineGroups = document.querySelectorAll(".inline-group");
    inlineGroups.forEach(setupInlineSortable);
});
