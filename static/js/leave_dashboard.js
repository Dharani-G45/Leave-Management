/**
 * Global Dashboard Utilities
 */
document.addEventListener("DOMContentLoaded", function() {
    // 1. Panel Switching Logic
    window.switchDashboardPanel = function(clickedButton, targetPanelId) {
        document.querySelectorAll('.dashboard-panel').forEach(p => p.classList.remove('panel-active'));
        document.querySelectorAll('.tab-trigger-btn').forEach(b => b.classList.remove('active-tab'));

        const target = document.getElementById(targetPanelId);
        if (target) {
            target.classList.add('panel-active');
            clickedButton.classList.add('active-tab');
        }
    };

    // 2. Data Bridge and Pie Chart Logic
    const dataBridge = document.getElementById("dashboard-data-bridge");
    if (dataBridge) {
        const data = {
            sick: parseInt(dataBridge.dataset.sick, 10) || 0,
            casual: parseInt(dataBridge.dataset.casual, 10) || 0,
            emergency: parseInt(dataBridge.dataset.emergency, 10) || 0,
            exam: parseInt(dataBridge.dataset.exam, 10) || 0,
            other: parseInt(dataBridge.dataset.other, 10) || 0,
            used: parseInt(dataBridge.dataset.used, 10) || 0,
            remaining: parseInt(dataBridge.dataset.remaining, 10) || 0
        };

        const totalAlloc = (data.sick + data.casual + data.emergency + data.exam + data.other) || 1;
        const totalUtil = (data.used + data.remaining) || 1;

        // Apply Backgrounds
        const allocPie = document.getElementById("allocationPie");
        if (allocPie) {
            allocPie.style.background = `conic-gradient(
                var(--color-sick) 0deg ${(data.sick / totalAlloc) * 360}deg,
                var(--color-casual) ${(data.sick / totalAlloc) * 360}deg ${((data.sick + data.casual) / totalAlloc) * 360}deg,
                var(--color-emergency) ${((data.sick + data.casual) / totalAlloc) * 360}deg ${((data.sick + data.casual + data.emergency) / totalAlloc) * 360}deg,
                var(--color-exam) ${((data.sick + data.casual + data.emergency) / totalAlloc) * 360}deg ${((data.sick + data.casual + data.emergency + data.exam) / totalAlloc) * 360}deg,
                var(--color-other) ${((data.sick + data.casual + data.emergency + data.exam) / totalAlloc) * 360}deg 360deg
            )`;
        }

        const utilPie = document.getElementById("utilizationPie");
        if (utilPie) {
            utilPie.style.background = `conic-gradient(
                var(--color-used) 0deg ${(data.used / totalUtil) * 360}deg,
                var(--color-remaining) ${(data.used / totalUtil) * 360}deg 360deg
            )`;
        }

        // Tooltip Configuration
        function configureTooltips(pieId, tooltipId, segments) {
            const pie = document.getElementById(pieId);
            const tooltip = document.getElementById(tooltipId);
            if (!pie || !tooltip) return;

            pie.addEventListener("mousemove", function(e) {
                const rect = pie.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = rect.height / 2 - (e.clientY - rect.top);
                let angle = (Math.atan2(x, y) * (180 / Math.PI) + 360) % 360;
                
                let currentSum = 0;
                let activeSegment = segments[segments.length - 1];

                for (let seg of segments) {
                    currentSum += seg.degrees;
                    if (angle <= currentSum) { activeSegment = seg; break; }
                }
                tooltip.style.display = "block";
                tooltip.innerHTML = `${activeSegment.label}<br><strong>${activeSegment.value} Days</strong>`;
                tooltip.style.left = (e.clientX + 15) + "px";
                tooltip.style.top = (e.clientY + 15) + "px"
            });
            pie.addEventListener("mouseleave", () => tooltip.style.display = "none");
        }

        configureTooltips("allocationPie", "allocationTooltip", [
            { label: "Sick Leave", degrees: (data.sick / totalAlloc) * 360, value: data.sick },
            { label: "Casual Leave", degrees: (data.casual / totalAlloc) * 360, value: data.casual },
            { label: "Emergency Leave", degrees: (data.emergency / totalAlloc) * 360, value: data.emergency },
            { label: "Exam Leave", degrees: (data.exam / totalAlloc) * 360, value: data.exam },
            { label: "Other Leave", degrees: (data.other / totalAlloc) * 360, value: data.other }
        ]);

        configureTooltips("utilizationPie", "utilizationTooltip", [
            { label: "Days Used", degrees: (data.used / totalUtil) * 360, value: data.used },
            { label: "Remaining", degrees: (data.remaining / totalUtil) * 360, value: data.remaining }
        ]);
    }

    // 3. Date Calculation Logic
    const fromDateInput = document.getElementById("from_date");
    const toDateInput = document.getElementById("to_date");
    const daysInput = document.getElementById("days");

    function calculateDays() {
        if (!fromDateInput.value || !toDateInput.value) return;
        const fromDate = new Date(fromDateInput.value);
        const toDate = new Date(toDateInput.value);
        
        if (toDate >= fromDate) {
            const diffDays = Math.ceil((toDate - fromDate) / (1000 * 60 * 60 * 24)) + 1;
            daysInput.value = diffDays;
        } else {
            daysInput.value = 0;
        }
    }

    if (fromDateInput && toDateInput) {
        fromDateInput.addEventListener("change", calculateDays);
        toDateInput.addEventListener("change", calculateDays);
    }
});

/**
 * Rejection Modal Controls
 */
window.openRejectModal = function(leaveId) {
    const modal = document.getElementById('rejectModal');
    document.getElementById('rejectForm').action = `/reject/${leaveId}/`;
    modal.style.display = 'flex';
};

window.closeRejectModal = function() {
    document.getElementById('rejectModal').style.display = 'none';
};