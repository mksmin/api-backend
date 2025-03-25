document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const isDevMode = urlParams.has('dev');

    // Используем Punycode для кириллических доменов
    const API_URL = urlParams.get('api_url') || (isDevMode
    ? 'http://localhost:8000/verify'
    : 'https://api.xn--80aadumbmbfkg6aqxd.xn--p1ai/verify');

    // Мок-данные для разработки
    if (isDevMode) {
        console.log('[DEV] Режим разработки активирован');
        window.Telegram = {
            WebApp: {
                initData: 'query_id=AAHsjjUFAAAAAOyONQVSt2os&user=%7B%22id%22%3A87396076%2C%22first_name%22%3A%22%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%22%2C%22last_name%22%3A%22%D0%9C%D0%B8%D0%BD%D0%B8%D0%BD%22%2C%22username%22%3A%22mks_min%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FKAW0oZ7WjH_Mp1p43zuUi2lzp_IW2rxF954-zq5f3us.svg%22%7D&auth_date=1742927059&hash=5ef28ede724f7a0fce1c7158e1e3a535a2de42003f8dee5cfa2bc9677e029455',
                initDataUnsafe: {
                    user: {
                        id: 87396076,
                        first_name: "Максим",
                        last_name: "Минин",
                        username: "mks_min",
                        language_code: "ru",
                        is_premium: true,
                        allows_write_to_pm: true,
                        photo_url: "https://t.me/i/userpic/320/KAW0oZ7WjH_Mp1p43zuUi2lzp_IW2rxF954-zq5f3us.svg"
                    },
                    auth_date: 1742927059,
                    hash: "5ef28ede724f7a0fce1c7158e1e3a535a2de42003f8dee5cfa2bc9677e029455"
                },
                ready: () => console.log('[DEV] Telegram.WebApp.ready()'),
                expand: () => console.log('[DEV] Telegram.WebApp.expand()')
            }
        };
    }

    try {
        // Инициализация Telegram
        Telegram.WebApp.ready();
        Telegram.WebApp.expand();

        // Получение элементов DOM
        const elements = {
            statusBlock: document.getElementById('statusBlock'),
            initDataRaw: document.getElementById('initDataRaw'),
            serverResponse: document.getElementById('serverResponse'),
            profileSection: document.getElementById('profileSection'),
            userName: document.getElementById('userName'),
            userUsername: document.getElementById('userUsername'),
            userAvatar: document.getElementById('userAvatar'),
            premiumBadge: document.getElementById('premiumBadge'),
            userId: document.getElementById('userId'),
            userLang: document.getElementById('userLang'),
            userCanWrite: document.getElementById('userCanWrite'),
            accountType: document.getElementById('accountType')
        };

        // Показать сырые данные
        elements.initDataRaw.textContent = JSON.stringify(
            Telegram.WebApp.initDataUnsafe,
            null,
            2
        );

        // Обновление профиля
        const updateProfile = (userData) => {
            try {
                elements.userName.textContent =
                [userData.first_name, userData.last_name]
                    .filter(Boolean)
                    .join(' ') || 'Неизвестный пользователь';

                elements.userUsername.textContent =
                userData.username ? `@${userData.username}` : '';

                if (userData.photo_url) {
                    elements.userAvatar.src = userData.photo_url;
                    elements.userAvatar.onerror = () => {
                        elements.userAvatar.style.display = 'none';
                    };
                    elements.userAvatar.style.display = 'block';
                }

                elements.premiumBadge.style.display =
                userData.is_premium ? 'inline-block' : 'none';

                elements.userId.textContent = userData.id;
                elements.userLang.textContent = userData.language_code;
                elements.userCanWrite.textContent =
                userData.allows_write_to_pm ? 'Да' : 'Нет';
                elements.accountType.textContent =
                userData.is_premium ? 'Премиум' : 'Обычный';

            } catch (error) {
                console.error('Ошибка обновления профиля:', error);
            }
        };

        // Режим разработки
        if (isDevMode) {
            console.log('[DEV] Показ профиля без проверки');
            elements.profileSection.classList.remove('hidden');
            updateProfile(Telegram.WebApp.initDataUnsafe.user);
            elements.statusBlock.textContent = 'Режим разработки: проверка отключена';
            return;
        }

        // Проверка на сервере
        const verifyWithServer = async () => {
            try {
                console.log('[HTTP] Отправка запроса на:', API_URL);
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        initData: Telegram.WebApp.initData
                    })
                });

                const data = await response.json();
                elements.serverResponse.textContent = JSON.stringify(data, null, 2);

                if (response.ok) {
                    elements.statusBlock.className = 'status-indicator status-success';
                    elements.statusBlock.textContent = '✅ Проверка пройдена!';
                    elements.profileSection.classList.remove('hidden');
                    updateProfile(Telegram.WebApp.initDataUnsafe.user);
                } else {
                    throw new Error(data.detail || 'Ошибка сервера');
                }
            } catch (error) {
                console.error('[HTTP] Ошибка:', error);
                elements.statusBlock.className = 'status-indicator status-error';
                elements.statusBlock.textContent = `❌ Ошибка: ${error.message}`;
                elements.profileSection.classList.add('hidden');
            }
        };

        verifyWithServer();

    } catch (error) {
        console.error('Фатальная ошибка:', error);
        if (elements.statusBlock) {
            elements.statusBlock.className = 'status-indicator status-error';
            elements.statusBlock.textContent = `⛔ Ошибка: ${error.message}`;
        }
    }
});