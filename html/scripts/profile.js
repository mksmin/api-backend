// app.js
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Инициализация Telegram Web App
        Telegram.WebApp.ready();
        Telegram.WebApp.expand();

        // Элементы интерфейса
        const statusBlock = document.getElementById('statusBlock');
        const initDataRaw = document.getElementById('initDataRaw');
        const serverResponse = document.getElementById('serverResponse');
        const profileSection = document.getElementById('profileSection');

        // Получаем данные от Telegram
        const initData = Telegram.WebApp.initData;
        const unsafeData = Telegram.WebApp.initDataUnsafe;

        // Показываем сырые данные
        initDataRaw.textContent = JSON.stringify(unsafeData, null, 2);
        statusBlock.textContent = 'Начинаем проверку...';

        // Функция обновления профиля
        const updateProfile = (userData) => {
            document.getElementById('userName').textContent =
            [userData.first_name, userData.last_name].filter(Boolean).join(' ');

            document.getElementById('userUsername').textContent =
            userData.username ? `@${userData.username}` : '';

            const avatar = document.getElementById('userAvatar');
            if(userData.photo_url) {
                avatar.src = userData.photo_url;
                avatar.onerror = () => avatar.style.display = 'none';
            }

            document.getElementById('premiumBadge').style.display =
            userData.is_premium ? 'inline-block' : 'none';

            document.getElementById('userId').textContent = userData.id;
            document.getElementById('userLang').textContent = userData.language_code;
            document.getElementById('userCanWrite').textContent =
            userData.allows_write_to_pm ? 'Да' : 'Нет';
            document.getElementById('accountType').textContent =
            userData.is_premium ? 'Премиум' : 'Обычный';
        };

        // Отправка данных на сервер
        const verifyWithServer = async () => {
            try {
                const response = await fetch('https://api.атом-лаб.рф/verify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ initData })
                });

                const responseText = await response.text();
                serverResponse.textContent = responseText;

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = JSON.parse(responseText);
                statusBlock.className = 'status-indicator status-success';
                statusBlock.innerHTML = '✅ Данные проверены!';

                profileSection.classList.remove('hidden');
                updateProfile(unsafeData.user);

            } catch (error) {
                console.error('Ошибка:', error);
                statusBlock.className = 'status-indicator status-error';
                statusBlock.innerHTML = `❌ Ошибка: ${error.message}`;
                profileSection.classList.add('hidden');
                serverResponse.textContent = error.stack || error.message;
            }
        };

        // Запуск проверки
        verifyWithServer();

    } catch (error) {
        console.error('Фатальная ошибка:', error);
        document.getElementById('statusBlock').textContent =
        `Критическая ошибка: ${error.message}`;
    }
});