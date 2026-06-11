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

    //Date calculation
    const fromDateInput = document.getElementById("from_date");
    const toDateInput = document.getElementById("to_date");
    const daysInput = document.getElementById("days");
    const daysDisplay = document.getElementById("days_display");

    function calculateTotalDays() {
        if (!fromDateInput.value || !toDateInput.value) return;
        
        const start = new Date(fromDateInput.value);
        const end = new Date(toDateInput.value);
        
        if (end >= start) {
            // Difference in days + 1 to make it inclusive
            const diffTime = Math.abs(end - start);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
            
            daysInput.value = diffDays;
            daysDisplay.textContent = diffDays;
        } else {
            daysInput.value = 0;
            daysDisplay.textContent = 0;
        }
    }

    if (fromDateInput && toDateInput) {
        fromDateInput.addEventListener("change", calculateTotalDays);
        toDateInput.addEventListener("change", calculateTotalDays);
    }

    document.querySelectorAll('.form-group-element').forEach(group => {
        const input = group.querySelector('input[type="date"]');
        if (input) {
            group.addEventListener('click', () => {
                input.showPicker ? input.showPicker() : input.focus();
            });
        }
    });

    // 2. Prevent duplicate dates (Now reads from the data bridge)
    const historyBridge = document.getElementById('leave-history-bridge');
    if (historyBridge && historyBridge.dataset.dates) {
        const takenDates = historyBridge.dataset.dates.split(',');
        
        const dateInputs = ['from_date', 'to_date'];
        dateInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('change', function() {
                    if (takenDates.includes(this.value)) {
                        alert('Warning: You have already taken leave on this date.');
                        this.value = ''; // Clear the input
                    }
                });
            }
        });
    } 
    
    const fileInput = document.getElementById('supporting_doc');
    const fileNameDisplay = document.getElementById('file_name_display');
    
    let dataTransfer = new DataTransfer();
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                dataTransfer.items.clear();
                dataTransfer.items.add(this.files[0]);
                fileNameDisplay.textContent = "Selected: " + this.files[0].name;
            } 
            else {
                if (dataTransfer.files.length > 0) {
                    this.files = dataTransfer.files;
                }
            }
        });
    }
    document.getElementById('leaveApplicationForm').addEventListener('submit', function(event) {
    const select = document.getElementById('leave_type');
    const selectedOption = select.options[select.selectedIndex];
    const remaining = parseInt(selectedOption.getAttribute('data-remaining'));
    const daysRequested = parseInt(document.getElementById('days').value);

    // Check if remaining balance is 0 or if requested days exceed balance
    if (remaining <= 0) {
        event.preventDefault(); // Stop form submission
        alert("You have no remaining balance for this leave category.");
        return false;
    }
    
    if (daysRequested > remaining) {
        event.preventDefault();
        alert("You requested " + daysRequested + " days, but only " + remaining + " are available.");
        return false;
    }
    });
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

// --- CSRF Helper ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- Global Popup System ---
function showGlobalPopup(message) {
    const popup = document.createElement('div');
    popup.className = 'global-toast-popup';
    popup.innerText = message;
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 3000);
}


async function handleLeaveAction(event, url, formData = null, onSuccessCallback = null) {
    if (event) event.preventDefault();
    
    // Prepare fetch options
    const fetchOptions = {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    };

    // Only add body if formData exists
    if (formData) {
        fetchOptions.body = formData;
    }
    
    try {
        const response = await fetch(url, fetchOptions);
        const data = await response.json();
        
        if (data.status === 'success') {
            showGlobalPopup(data.message);
            if (onSuccessCallback) onSuccessCallback();
        } else {
            showGlobalPopup(data.message || "Operation failed.");
        }
    } catch (e) {
        showGlobalPopup("Network error. Please try again.");
    }
}
async function refreshDashboardSection() {
    try {
        const response = await fetch(window.location.href);
        const htmlText = await response.text();
        const parser = new DOMParser();
        const newDoc = parser.parseFromString(htmlText, 'text/html');

        // IDs of the containers that need to be refreshed
        const panelsToRefresh = [
            'panel-leave-balance', 
            'panel-pending-reviews', 
            'panel-leave-history', 
            'panel-approval-logs'
        ];

        panelsToRefresh.forEach(id => {
            const oldPanel = document.getElementById(id);
            const newPanel = newDoc.getElementById(id);
            if (oldPanel && newPanel) {
                oldPanel.innerHTML = newPanel.innerHTML;
            }
        });
        
        console.log("Dashboard refreshed successfully.");
    } catch (error) {
        console.error("Error refreshing dashboard:", error);
    }
}
