/* Tamil Nadu Sports Tournament - Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Cascading District -> Taluk -> Village Dropdown Handler
    const districtSelect = document.getElementById('id_district') || document.getElementById('district_select');
    const talukSelect = document.getElementById('id_taluk') || document.getElementById('taluk_select');
    const villageSelect = document.getElementById('id_village') || document.getElementById('village_select');

    if (districtSelect && talukSelect) {
        const initialTalukId = talukSelect.value || talukSelect.getAttribute('data-selected');
        const initialVillageId = villageSelect ? (villageSelect.value || villageSelect.getAttribute('data-selected')) : null;


        function loadTaluks(districtId, selectedTalukId, callback) {
            talukSelect.innerHTML = '<option value="">-- Select Taluk --</option>';
            if (villageSelect) {
                villageSelect.innerHTML = '<option value="">-- Select Village --</option>';
            }
            if (!districtId) return;

            fetch(`/api/locations/taluks/?district_id=${districtId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(taluk => {
                        const option = document.createElement('option');
                        option.value = taluk.id;
                        option.textContent = taluk.name;
                        if (selectedTalukId && (taluk.id == selectedTalukId || taluk.name == selectedTalukId)) {
                            option.selected = true;
                        }
                        talukSelect.appendChild(option);
                    });
                    if (callback) callback();
                })
                .catch(err => console.error('Error fetching taluks:', err));
        }

        function loadVillages(talukId, selectedVillageId) {
            if (!villageSelect) return;
            villageSelect.innerHTML = '<option value="">-- Select Village --</option>';
            if (!talukId) return;

            fetch(`/api/locations/villages/?taluk_id=${talukId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(village => {
                        const option = document.createElement('option');
                        option.value = village.id;
                        option.textContent = village.name;
                        if (selectedVillageId && (village.id == selectedVillageId || village.name == selectedVillageId)) {
                            option.selected = true;
                        }
                        villageSelect.appendChild(option);
                    });
                })
                .catch(err => console.error('Error fetching villages:', err));
        }

        // On district change: reset taluk, reset village, load taluks for district
        districtSelect.addEventListener('change', function() {
            loadTaluks(this.value, null, null);
        });

        // On taluk change: reset village, load villages for taluk
        talukSelect.addEventListener('change', function() {
            loadVillages(this.value, null);
        });

        // On page load if district is already selected
        if (districtSelect.value) {
            loadTaluks(districtSelect.value, initialTalukId, function() {
                if (talukSelect.value) {
                    loadVillages(talukSelect.value, initialVillageId);
                }
            });
        }
    }

    // 2. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

