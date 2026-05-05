document.addEventListener('DOMContentLoaded', () => {
    // Pages
    const pageScan = document.getElementById('page-scan');
    const pageMigration = document.getElementById('page-migration');
    const pageStatus = document.getElementById('page-status');

    // Buttons
    const btnScan = document.getElementById('btn-scan');
    const btnRetry = document.getElementById('btn-retry');
    const btnExit = document.getElementById('btn-exit');
    const scanError = document.getElementById('scan-error');
    
    // Selects
    const sourceSelect = document.getElementById('source-browser');
    const targetSelect = document.getElementById('target-browser');
    const sourceProfile = document.getElementById('source-profile');
    const targetProfile = document.getElementById('target-profile');
    const migrateBtn = document.getElementById('migrate-btn');
    
    const logMessages = document.getElementById('log-messages');
    let browserData = [];

    // Helper to log messages
    const log = (message, type = 'info') => {
        const line = document.createElement('div');
        line.className = `log-line log-${type}`;
        line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logMessages.appendChild(line);
        logMessages.scrollTop = logMessages.scrollHeight;
    };

    const showPage = (page) => {
        console.log("Switching to page:", page.id);
        document.querySelectorAll('.page').forEach(p => {
            p.classList.remove('active');
            p.classList.add('hidden');
        });
        page.classList.add('active');
        page.classList.remove('hidden');
    };

    // Wait for pywebview API to be ready
    window.addEventListener('pywebviewready', () => {
        
        btnScan.addEventListener('click', async () => {
            const btnText = btnScan.querySelector('.btn-text');
            const loader = btnScan.querySelector('.loader');
            
            btnScan.disabled = true;
            btnText.textContent = "Scanning...";
            loader.classList.remove('hidden');

            try {
                browserData = await window.pywebview.api.get_browsers();
                
                if (browserData.error) {
                    scanError.textContent = "Scanning Error: " + browserData.error;
                    scanError.classList.remove('hidden');
                    btnScan.disabled = false;
                    btnText.textContent = "Scan Browsers";
                    loader.classList.add('hidden');
                    return;
                }
                
                sourceSelect.innerHTML = '<option value="">Select Browser</option>';
                targetSelect.innerHTML = '<option value="">Select Browser</option>';
                sourceProfile.innerHTML = '<option value="">Select Browser First</option>';
                targetProfile.innerHTML = '<option value="">Select Browser First</option>';
                
                if (!browserData || browserData.length === 0) {
                    scanError.textContent = "No supported Chromium browsers found! Please check if they are installed correctly.";
                    scanError.classList.remove('hidden');
                    btnScan.disabled = false;
                    btnText.textContent = "Scan Browsers";
                    loader.classList.add('hidden');
                    return;
                }

                scanError.classList.add('hidden');
                browserData.forEach(b => {
                    const opt1 = document.createElement('option');
                    opt1.value = b.id; opt1.textContent = b.name;
                    sourceSelect.appendChild(opt1);
                    
                    const opt2 = document.createElement('option');
                    opt2.value = b.id; opt2.textContent = b.name;
                    targetSelect.appendChild(opt2);
                });
                
                showPage(pageMigration);


            } catch (e) {
                alert("Error: " + e);
            } finally {
                btnScan.disabled = false;
                btnText.textContent = "Scan Browsers";
                loader.classList.add('hidden');
            }
        });

        const updateProfiles = (browserId, profileSelect) => {
            profileSelect.innerHTML = '<option value="">Select Profile</option>';
            profileSelect.disabled = true;
            
            if (!browserId) return;
            
            const browser = browserData.find(b => b.id === browserId);
            if (browser && browser.profiles.length > 0) {
                browser.profiles.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.path;
                    opt.textContent = p.name + (p.is_default ? " (Default)" : "");
                    if (p.is_default) opt.selected = true;
                    profileSelect.appendChild(opt);
                });
                profileSelect.disabled = false;
            } else {
                profileSelect.innerHTML = '<option value="">No Profiles Found</option>';
            }
            checkReady();
        };

        sourceSelect.addEventListener('change', () => updateProfiles(sourceSelect.value, sourceProfile));
        targetSelect.addEventListener('change', () => updateProfiles(targetSelect.value, targetProfile));
        sourceProfile.addEventListener('change', checkReady);
        targetProfile.addEventListener('change', checkReady);

        function checkReady() {
            if (sourceSelect.value && targetSelect.value && 
                sourceProfile.value && targetProfile.value && 
                (sourceSelect.value !== targetSelect.value || sourceProfile.value !== targetProfile.value)) {
                migrateBtn.disabled = false;
            } else {
                migrateBtn.disabled = true;
            }
        }

        migrateBtn.addEventListener('click', async () => {
            showPage(pageStatus);
            logMessages.innerHTML = '';
            
            log(`Starting migration...`);
            log("Please check if macOS prompts for your Computer Password. You must click 'Allow'.", 'info');

            try {
                const options = {
                    passwords: document.getElementById('opt-passwords').checked,
                    cookies: document.getElementById('opt-cookies').checked,
                    bookmarks: document.getElementById('opt-bookmarks').checked,
                    history: document.getElementById('opt-history').checked,
                    autofill: document.getElementById('opt-autofill').checked
                };
                
                const result = await window.pywebview.api.start_migration(
                    sourceSelect.value, 
                    sourceProfile.value, 
                    targetSelect.value, 
                    targetProfile.value, 
                    options
                );
                
                if (result.success) {
                    log(result.message, 'success');
                } else {
                    log(result.message, 'error');
                }
            } catch (e) {
                log(`Unexpected error: ${e}`, 'error');
            }
        });

        btnRetry.addEventListener('click', () => {
            showPage(pageMigration);
        });

        btnExit.addEventListener('click', () => {
            document.body.innerHTML = '<div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh;"><h2 style="margin-bottom:10px;">Safe to close</h2><p style="color:var(--text-secondary)">You may now close this window safely.</p></div>';
        });
    });
});
