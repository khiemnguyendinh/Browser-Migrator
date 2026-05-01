document.addEventListener('DOMContentLoaded', () => {
    const sourceSelect = document.getElementById('source-browser');
    const targetSelect = document.getElementById('target-browser');
    const migrateBtn = document.getElementById('migrate-btn');
    const btnText = migrateBtn.querySelector('.btn-text');
    const loader = migrateBtn.querySelector('.loader');
    const statusConsole = document.getElementById('status-console');
    const logMessages = document.getElementById('log-messages');

    let isMigrating = false;

    // Helper to log messages
    const log = (message, type = 'info') => {
        const line = document.createElement('div');
        line.className = `log-line log-${type}`;
        line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logMessages.appendChild(line);
        logMessages.scrollTop = logMessages.scrollHeight;
    };

    // Wait for pywebview API to be ready
    window.addEventListener('pywebviewready', async () => {
        try {
            const browsers = await window.pywebview.api.get_browsers();
            
            // Clear loading options
            sourceSelect.innerHTML = '<option value="">Select Source Browser</option>';
            targetSelect.innerHTML = '<option value="">Select Target Browser</option>';
            
            if (browsers.length === 0) {
                sourceSelect.innerHTML = '<option value="">No browsers found</option>';
                targetSelect.innerHTML = '<option value="">No browsers found</option>';
                return;
            }

            // Populate options
            browsers.forEach(b => {
                const option1 = document.createElement('option');
                option1.value = b.id;
                option1.textContent = b.name;
                
                const option2 = document.createElement('option');
                option2.value = b.id;
                option2.textContent = b.name;
                
                sourceSelect.appendChild(option1);
                targetSelect.appendChild(option2);
            });

            // Enable selects
            sourceSelect.disabled = false;
            targetSelect.disabled = false;

            // Check if ready to migrate
            const checkReady = () => {
                if (sourceSelect.value && targetSelect.value && sourceSelect.value !== targetSelect.value && !isMigrating) {
                    migrateBtn.disabled = false;
                } else {
                    migrateBtn.disabled = true;
                }
            };

            sourceSelect.addEventListener('change', checkReady);
            targetSelect.addEventListener('change', checkReady);

            // Start Migration
            migrateBtn.addEventListener('click', async () => {
                if (!sourceSelect.value || !targetSelect.value) return;

                isMigrating = true;
                migrateBtn.disabled = true;
                sourceSelect.disabled = true;
                targetSelect.disabled = true;
                
                btnText.textContent = "Migrating...";
                loader.classList.remove('hidden');
                
                statusConsole.style.display = 'flex';
                statusConsole.classList.remove('hidden');
                
                logMessages.innerHTML = '';
                log(`Starting migration from ${sourceSelect.options[sourceSelect.selectedIndex].text} to ${targetSelect.options[targetSelect.selectedIndex].text}...`);
                log("Please check if macOS prompts for Keychain password. You must click 'Allow'.", 'info');

                try {
                    // Collect options
                    const options = {
                        passwords: document.getElementById('opt-passwords').checked,
                        cookies: document.getElementById('opt-cookies').checked,
                        bookmarks: document.getElementById('opt-bookmarks').checked,
                        history: document.getElementById('opt-history').checked,
                        autofill: document.getElementById('opt-autofill').checked
                    };
                    
                    const result = await window.pywebview.api.start_migration(sourceSelect.value, targetSelect.value, options);
                    if (result.success) {
                        log(result.message, 'success');
                        btnText.textContent = "Migration Complete!";
                    } else {
                        log(result.message, 'error');
                        btnText.textContent = "Migration Failed";
                    }
                } catch (e) {
                    log(`Unexpected error: ${e}`, 'error');
                    btnText.textContent = "Error occurred";
                } finally {
                    loader.classList.add('hidden');
                    isMigrating = false;
                    sourceSelect.disabled = false;
                    targetSelect.disabled = false;
                    
                    // Reset button after 3 seconds
                    setTimeout(() => {
                        if (sourceSelect.value && targetSelect.value && sourceSelect.value !== targetSelect.value) {
                            migrateBtn.disabled = false;
                        }
                        btnText.textContent = "Start Migration";
                    }, 3000);
                }
            });

        } catch (error) {
            console.error("Failed to initialize API:", error);
            sourceSelect.innerHTML = '<option value="">Error connecting to API</option>';
        }
    });
});
