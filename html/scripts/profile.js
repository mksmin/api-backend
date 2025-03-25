async function verifyWithServer(initData) {
    const statusBlock = document.getElementById('statusBlock');
    const profileSection = document.getElementById('profileSection');

    try {
        const response = await fetch('https://api.атом-лаб.рф/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ initData })
        });

        if (!response.ok) {
            throw new Error('Ошибка проверки данных');
        }

        statusBlock.classList.add('status-success');
        statusBlock.textContent = '✅ Проверка пройдена';
        profileSection.classList.remove('hidden');

        const user = Telegram.WebApp.initDataUnsafe.user;
        updateProfile(user);

    } catch (error) {
        statusBlock.classList.add('status-error');
        statusBlock.textContent = `❌ Ошибка: ${error.message}`;
        profileSection.classList.add('hidden');
    }
}

function updateProfile(userData) {
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
}

document.addEventListener('DOMContentLoaded', () => {
    try {
        Telegram.WebApp.ready();
        Telegram.WebApp.expand();

        const initData = Telegram.WebApp.initData;
        document.getElementById('statusBlock').textContent = 'Идет проверка...';

        verifyWithServer(initData);

    } catch (error) {
        console.error('Fatal error:', error);
        document.getElementById('statusBlock').textContent =
        'Критическая ошибка: ' + error.message;
    }
});