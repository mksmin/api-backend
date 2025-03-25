async function verifyWithServer(initData) {
    const statusBlock = document.getElementById('statusBlock');
    const serverResponse = document.getElementById('serverResponse');

    try {
        // Показываем сырые данные
        document.getElementById('initDataRaw').textContent =
        JSON.stringify(Telegram.WebApp.initDataUnsafe, null, 2);

        const response = await fetch('https://api.атом-лаб.рф/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ initData })
        });

        const result = await response.json();
        serverResponse.textContent = JSON.stringify(result, null, 2);

        if (!response.ok) {
            throw new Error(result.detail || 'Ошибка сервера');
        }

        statusBlock.classList.add('status-success');
        statusBlock.textContent = '✅ Проверка пройдена';
        document.getElementById('profileSection').classList.remove('hidden');

        updateProfile(Telegram.WebApp.initDataUnsafe.user);

    } catch (error) {
        statusBlock.classList.add('status-error');
        statusBlock.textContent = `❌ Ошибка: ${error.message}`;
        serverResponse.textContent = error.stack || error.message;
        document.getElementById('profileSection').classList.add('hidden');
    }
}