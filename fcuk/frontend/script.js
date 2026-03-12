const API_URL = 'http://127.0.0.1:8000';

function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// Обновление хедера на всех страницах
function updateHeader() {
    const authButtons = document.querySelector('.auth-buttons');
    if (!authButtons) return;

    const user = JSON.parse(localStorage.getItem('user') || 'null');

    if (user) {
        authButtons.innerHTML = `
            <a href="profile.html" class="nav__link">Личный кабинет</a>
            <a href="#" class="btn-secondary" id="logoutBtn">Выйти</a>
        `;

        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm('Выйти из аккаунта?')) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('user');
                    window.location.href = 'index.html';
                }
            });
        }
    } else {
        authButtons.innerHTML = `
            <a href="login.html" class="btn-secondary">Войти</a>
            <a href="register.html" class="btn-primary">Регистрация</a>
        `;
    }
}

// Регистрация
async function handleRegister(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        full_name: formData.get('full_name') || null,
        phone: formData.get('phone') || null
    };

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Ошибка регистрации');
        }

        alert('Регистрация успешна! Теперь войдите.');
        window.location.href = 'login.html';
    } catch (err) {
        alert('Ошибка: ' + err.message);
    }
}

// Логин
async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = new URLSearchParams();

    // ✅ Отправляем поле username (даже если в форме оно называется login)
    data.append('username', formData.get('login'));
    data.append('password', formData.get('password'));

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: data
        });

        if (!response.ok) {
            // 🔥 Улучшенная обработка ошибок
            let errorMsg = 'Ошибка сервера';
            try {
                const errData = await response.json();
                if (errData.detail) {
                    if (Array.isArray(errData.detail)) {
                        // Собираем все сообщения валидации
                        errorMsg = errData.detail.map(d => d.msg).join('; ');
                    } else {
                        errorMsg = errData.detail;
                    }
                } else {
                    errorMsg = JSON.stringify(errData);
                }
            } catch {
                // Если ответ не JSON – читаем как текст
                errorMsg = await response.text();
            }
            throw new Error(errorMsg);
        }

        const result = await response.json();
        localStorage.setItem('access_token', result.access_token);

        // Получаем данные пользователя
        const userResponse = await fetch(`${API_URL}/auth/me`, {
            headers: getAuthHeaders()
        });
        if (!userResponse.ok) throw new Error('Не удалось получить данные пользователя');

        const user = await userResponse.json();
        localStorage.setItem('user', JSON.stringify(user));

        alert('Вход успешен!');
        window.location.href = 'profile.html';
    } catch (err) {
        alert('Ошибка: ' + err.message);   // Теперь сообщение будет понятным
    }
}

// Загрузка данных профиля
async function loadProfileData() {
    const usernameDisplay = document.getElementById('usernameDisplay');
    const ordersList = document.getElementById('ordersList');
    if (!usernameDisplay && !ordersList) return;

    try {
        const userResponse = await fetch(`${API_URL}/auth/me`, {
            headers: getAuthHeaders()
        });
        if (!userResponse.ok) throw new Error('Не авторизован');
        const user = await userResponse.json();

        if (usernameDisplay) {
            usernameDisplay.textContent = user.username;
        }

        if (ordersList) {
            const ordersResponse = await fetch(`${API_URL}/orders/my`, {
                headers: getAuthHeaders()
            });
            const orders = await ordersResponse.ok ? await ordersResponse.json() : [];

            if (orders.length === 0) {
                ordersList.innerHTML = '<p style="text-align: center; opacity: 0.8;">У вас пока нет заказов</p>';
            } else {
                ordersList.innerHTML = orders.map(order => `
                    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 20px; margin-bottom: 20px;">
                        <p><strong>Заказ #${order.id}</strong> — ${order.status}</p>
                        <p>Создан: ${new Date(order.created_at).toLocaleDateString('ru-RU')}</p>
                        <p>Товаров: ${order.items.length}</p>
                        <p>Доставка: ${order.delivery_method}${order.delivery_address ? ' — ' + order.delivery_address : ''}</p>
                    </div>
                `).join('');
            }
        }
    } catch (err) {
        console.error(err);
        localStorage.clear();
        window.location.href = 'login.html';
    }
}

// === ПОШАГОВЫЙ МАСТЕР ЗАКАЗА ===
const uploadedModels = [];
let currentStep = 1;

function showStep(step) {
    document.querySelectorAll('.order-step').forEach(s => s.classList.remove('active'));
    document.getElementById(`step${step}`).classList.add('active');

    document.querySelectorAll('.step-indicator').forEach((ind, i) => {
        ind.classList.toggle('active', i + 1 <= step);
        if (i < 3) {
            const line = ind.nextElementSibling;
            if (line) line.style.background = i + 1 < step ? '#FF3B30' : 'rgba(255,255,255,0.2)';
        }
    });
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/orders/upload`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Ошибка загрузки');
    }
    return await response.json();
}

function addModelPreview(modelData, file) {
    const preview = document.getElementById('modelsPreview');
    const div = document.createElement('div');
    div.className = 'model-preview-item';
    div.innerHTML = `
        <img src="images/icons/upload0.png" alt="model">
        <div>
            <strong>${modelData.original_name}</strong><br>
            <small>Размер: ${(file.size / 1024 / 1024).toFixed(2)} МБ</small>
        </div>
        <button class="remove-model">×</button>
    `;

    div.querySelector('.remove-model').addEventListener('click', () => {
        div.remove();
        const index = uploadedModels.findIndex(m => m.serverData.filename === modelData.filename);
        if (index > -1) uploadedModels.splice(index, 1);
        document.getElementById('next1').disabled = uploadedModels.length === 0;
    });

    preview.appendChild(div);
    document.getElementById('next1').disabled = false;
}

function renderModelsConfig() {
    const container = document.getElementById('modelsConfig');
    container.innerHTML = '';

    uploadedModels.forEach(model => {
        const div = document.createElement('div');
        div.className = 'model-config-item';
        div.innerHTML = `
            <h4>${model.serverData.original_name}</h4>
            <div class="model-options-grid">
                <div>
                    <label>Количество</label>
                    <input type="number" min="1" value="${model.quantity}" class="quantity-input">
                </div>
                <div>
                    <label>Филамент</label>
                    <select class="filament-select">
                        <option value="PLA" ${model.filament_type === 'PLA' ? 'selected' : ''}>PLA</option>
                        <option value="ABS" ${model.filament_type === 'ABS' ? 'selected' : ''}>ABS</option>
                        <option value="PETG" ${model.filament_type === 'PETG' ? 'selected' : ''}>PETG</option>
                        <option value="TPU" ${model.filament_type === 'TPU' ? 'selected' : ''}>TPU</option>
                    </select>
                </div>
                <div>
                    <label>Цвет</label>
                    <select class="color-select">
                        <option value="черный" ${model.filament_color === 'черный' ? 'selected' : ''}>Чёрный</option>
                        <option value="белый" ${model.filament_color === 'белый' ? 'selected' : ''}>Белый</option>
                        <option value="красный" ${model.filament_color === 'красный' ? 'selected' : ''}>Красный</option>
                        <option value="синий" ${model.filament_color === 'синий' ? 'selected' : ''}>Синий</option>
                        <option value="зеленый" ${model.filament_color === 'зеленый' ? 'selected' : ''}>Зелёный</option>
                    </select>
                </div>
            </div>
        `;

        div.querySelector('.quantity-input').addEventListener('change', (e) => model.quantity = parseInt(e.target.value) || 1);
        div.querySelector('.filament-select').addEventListener('change', (e) => model.filament_type = e.target.value);
        div.querySelector('.color-select').addEventListener('change', (e) => model.filament_color = e.target.value);

        container.appendChild(div);
    });
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    updateHeader();

    const page = window.location.pathname.split('/').pop();

    // Формы логина и регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) registerForm.addEventListener('submit', handleRegister);

    const loginForm = document.getElementById('loginForm');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    // Профиль
    loadProfileData();

    // Мастер заказа
    if (page === 'order-create.html') {
        if (!localStorage.getItem('access_token')) {
            window.location.href = 'login.html';
            return;
        }

        const uploadArea = document.getElementById('uploadArea');
        const chooseBtn = document.getElementById('chooseFilesBtn');
        const fileInput = document.getElementById('fileInput');

        // Клик по всей зоне и кнопке
        uploadArea.addEventListener('click', (e) => {
            if (e.target.closest('#chooseFilesBtn')) return;
            fileInput.click();
        });
        chooseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });

        // Drag & drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (!uploadArea.contains(e.relatedTarget)) {
                uploadArea.classList.remove('drag-over');
            }
        });

        uploadArea.addEventListener('drop', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('drag-over');
            await processFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', async (e) => {
            await processFiles(e.target.files);
            e.target.value = '';
        });

        async function processFiles(files) {
            for (let file of files) {
                if (!file.name.match(/\.(stl|obj|3mf)$/i)) {
                    alert(`Неподдерживаемый формат: ${file.name}`);
                    continue;
                }

                try {
                    const data = await uploadFile(file);
                    uploadedModels.push({
                        file,
                        serverData: data,
                        quantity: 1,
                        filament_type: 'PLA',
                        filament_color: 'черный'
                    });
                    addModelPreview(data, file);
                } catch (err) {
                    alert(`Ошибка загрузки ${file.name}: ${err.message}`);
                }
            }
        }

        // Навигация по шагам
        document.getElementById('next1').addEventListener('click', () => {
            renderModelsConfig();
            showStep(2);
        });

        document.querySelectorAll('.prev-btn').forEach(btn => {
            btn.addEventListener('click', () => showStep(currentStep - 1));
        });

        document.getElementById('next2').addEventListener('click', () => showStep(3));
        document.getElementById('next3').addEventListener('click', () => {
            document.getElementById('totalPrice').textContent = '1500 ₽'; // заглушка
            showStep(4);
        });

        document.getElementById('confirmOrder').addEventListener('click', async () => {
            if (uploadedModels.length === 0) return alert('Загрузите модели');

            const items = uploadedModels.map(m => ({
                filename: m.serverData.filename,
                original_name: m.serverData.original_name,
                quantity: m.quantity,
                filament_type: m.filament_type,
                filament_color: m.filament_color
            }));

            const orderData = {
                items,
                delivery_method: document.getElementById('deliveryMethod').value,
                delivery_address: document.getElementById('deliveryAddress').value || null,
                comment: document.getElementById('comment').value || null
            };

            try {
                const response = await fetch(`${API_URL}/orders/`, {
                    method: 'POST',
                    headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
                    body: JSON.stringify(orderData)
                });

                if (!response.ok) throw new Error('Ошибка создания заказа');

                document.getElementById('paymentStatus').innerHTML = `
                    <p style="color: #0f0; font-size: 24px;">Заказ успешно создан!</p>
                    <a href="profile.html" class="btn-primary" style="margin-top: 20px; display: inline-block;">Перейти в личный кабинет</a>
                `;
            } catch (err) {
                document.getElementById('paymentStatus').innerHTML = `<p style="color: #f00;">Ошибка: ${err.message}</p>`;
            }
        });
    }
});

// script.js — общий скрипт для сайта (можно подключить и в index.html, и в lk)

const API_BASE = 'http://127.0.0.1:8000';
const token = localStorage.getItem('access_token');

// Проверка авторизации (если нет токена → на логин)
if (!token && window.location.pathname.includes('lk.html')) {
    window.location.href = 'login.html';
}

// Выход
document.getElementById('logoutBtn')?.addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('access_token');
    window.location.href = 'index.html';
});

// Отображение имени пользователя (если есть эндпоинт /auth/me)
async function loadUserProfile() {
    if (!token) return;

    try {
        const res = await fetch(`${API_BASE}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Ошибка авторизации');
        const user = await res.json();
        document.getElementById('usernameDisplay').textContent = user.username || user.full_name || 'пользователь';
    } catch (err) {
        console.error(err);
    }
}

// Загрузка и отображение заказов
async function loadOrders() {
    if (!token) return;

    const container = document.getElementById('ordersList');
    if (!container) return;

    container.innerHTML = '<p>Загрузка заказов...</p>';

    try {
        const res = await fetch(`${API_BASE}/orders/my`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (res.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
            return;
        }

        if (!res.ok) throw new Error('Ошибка сервера');

        const orders = await res.json();

        if (orders.length === 0) {
            container.innerHTML = '<p style="text-align: center; opacity: 0.8;">У вас пока нет заказов</p>';
            return;
        }

        container.innerHTML = orders.map(order => `
            <div class="order-card" style="
                background: rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">Заказ №${order.id}</h4>
                    <span style="
                        padding: 6px 12px;
                        border-radius: 20px;
                        font-size: 14px;
                        background: ${getStatusColor(order.status)};
                        color: white;
                    ">
                        ${getStatusText(order.status)}
                    </span>
                </div>

                <p style="margin: 12px 0 8px; opacity: 0.9;">
                    Создан: ${new Date(order.created_at).toLocaleString('ru-RU')}
                </p>

                ${order.paid_at ? `<p>Оплачен: ${new Date(order.paid_at).toLocaleString('ru-RU')}</p>` : ''}
                ${order.finished_at ? `<p>Завершён: ${new Date(order.finished_at).toLocaleString('ru-RU')}</p>` : ''}

                <div style="margin-top: 16px;">
                    <strong>Позиции:</strong>
                    <ul style="margin: 8px 0; padding-left: 20px; list-style: none;">
                        ${order.items.map(item => `
                            <li style="margin-bottom: 8px;">
                                • ${item.original_name} × ${item.quantity} 
                                (${item.filament_type}, ${item.filament_color})
                                ${item.weight_grams ? ` — ${item.weight_grams} г` : ''}
                                ${item.price_per_item ? ` — ${item.price_per_item} ₽` : ''}
                            </li>
                        `).join('')}
                    </ul>
                </div>

                <p style="margin-top: 16px;">
                    <strong>Способ доставки:</strong> ${order.delivery_method === 'pickup' ? 'Самовывоз' : order.delivery_method}
                    ${order.delivery_address ? `<br><strong>Адрес:</strong> ${order.delivery_address}` : ''}
                </p>

                ${order.comment ? `
                    <p style="margin-top: 12px; opacity: 0.9;">
                        <strong>Комментарий:</strong> ${order.comment}
                    </p>
                ` : ''}

                ${order.total_price ? `
                    <p style="font-size: 20px; font-weight: bold; margin-top: 20px; text-align: right;">
                        Итого: ${order.total_price} ₽
                    </p>
                ` : ''}

                ${order.photos?.length > 0 ? `
                    <div style="margin-top: 16px;">
                        <strong>Фото упаковки:</strong>
                        <div style="display: flex; gap: 12px; margin-top: 8px; flex-wrap: wrap;">
                            ${order.photos.map(photo => `
                                <img src="${photo}" alt="Фото заказа" style="max-width: 120px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
        container.innerHTML = '<p style="color: #ff6b6b; text-align: center;">Ошибка загрузки заказов</p>';
    }
}

// Вспомогательные функции для статусов
function getStatusText(status) {
    const map = {
        'new': 'Новый',
        'processing': 'В обработке',
        'printing': 'Печатается',
        'packing': 'Упаковка',
        'shipped': 'Отправлен',
        'completed': 'Завершён',
        'cancelled': 'Отменён'
    };
    return map[status] || status;
}

function getStatusColor(status) {
    const map = {
        'new': '#ffb300',
        'processing': '#4fc3f7',
        'printing': '#ab47bc',
        'packing': '#66bb6a',
        'shipped': '#ffa726',
        'completed': '#66bb6a',
        'cancelled': '#ef5350'
    };
    return map[status] || '#78909c';
}

// Инициализация при загрузке страницы ЛК
document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
    loadOrders();

    // Переключение вкладок (если нужно доработать)
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });

    // Сохранение контактных данных (можно добавить позже)
    document.getElementById('contactsForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        // Здесь можно сделать PATCH /users/me или аналогичный эндпоинт
        alert('Данные сохранены (эндпоинт пока не реализован)');
    });
});