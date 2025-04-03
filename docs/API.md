### **Версия API**: v1

### **Основной роутер**: `/admin`, `/auth`, `/logs`, `/secrets`, `/notifications`

## **Аутентификация**

Для всех защищённых маршрутов требуется авторизация с использованием **OAuth2**. Токен передаётся через заголовок `Authorization` в формате `Bearer <token>`.

---

## **Маршруты API**

### **/admin**

#### **POST /admin/users/create**
Создаёт нового пользователя.

**Запрос**:
- `username`: (str) Имя пользователя для создания.

**Ответ**:
- `201 Created`: Пользователь успешно создан.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Внутренняя ошибка сервера.

**Пример**:
```json
{
    "message": "User created successfully",
    "user_id": 1
}
```

---

#### **DELETE /admin/users/delete**
Удаляет пользователя.

**Запрос**:
- `username`: (str) Имя пользователя для удаления.

**Ответ**:
- `200 OK`: Пользователь успешно удалён.
- `401 Unauthorized`: Неверные данные авторизации.
- `404 Not Found`: Пользователь не найден.
- `500 Internal Server Error`: Внутренняя ошибка сервера.

**Пример**:
```json
{
    "message": "User deleted successfully"
}
```

---

#### **GET /admin/users/list**
Получает список пользователей.

**Ответ**:
- `200 OK`: Список пользователей.

**Пример**:
```json
{
    "users": [
        {
            "id": 1,
            "username": "example_user",
            "created_at": "2025-02-09T12:00:00"
        }
    ]
}
```

---

### **/auth**

#### **POST /auth/login**
Осуществляет вход пользователя в систему.

**Запрос**:
- `username`: (str) Имя пользователя.
- `totp_code`: (str) Код TOTP.

**Ответ**:
- `200 OK`: Успешный вход. Возвращает токен.
- `401 Unauthorized`: Неверные данные авторизации или неверный код TOTP.
- `500 Internal Server Error`: Ошибка на сервере.
- `429 Too Many Requests`: Слишком много без успешных попыток входа.
 
**Пример**:
```json
{
    "message": "Login successful",
    "access_token": "<token>",
    "token_type": "bearer"
}
```

---

#### **POST /auth/logout**
Выход пользователя из системы. Добавляет токен в чёрный список.

**Ответ**:
- `200 OK`: Выход успешен.

**Пример**:
```json
{
    "message": "Logged out successfully"
}
```

---

#### **GET /auth/protected**
Защищённый маршрут, доступ к которому возможен только при наличии валидного токена.

**Ответ**:
- `200 OK`: Доступ разрешён.

**Пример**:
```json
{
    "message": "Welcome to the protected route!"
}
```

---

### **/logs**

#### **GET /logs/logs-file**
Загружает файл логов.

**Ответ**:
- `200 OK`: Успешная загрузка файла.
- `404 Not Found`: Файл логов не найден.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка при загрузке файла.

**Пример**:
```json
{
    "message": "Log file not found"
}
```

---

#### **GET /logs/auth-logs**
Получает список логов аутентификации.

**Ответ**:
- `200 OK`: Список логов аутентификации.

**Пример**:
```json
{
    "logs": [
        {
            "id": 1,
            "username": "example_user",
            "action": "LOGIN_SUCCESS",
            "timestamp": "2025-02-09T12:00:00",
            "ip_address": "127.0.0.1"
        }
    ]
}
```

---

#### **DELETE /logs/auth-logs**
Удаляет все логи аутентификации из базы данных.

**Ответ**:
- `200 OK`: Логи успешно удалены.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка при удалении логов.

**Пример**:
```json
{
    "message": "Successfully deleted auth logs from the database"
}
```

---

### **/secrets**

#### **GET /secrets/list**
Получает список секретов пользователя.

**Ответ**:
- `200 OK`: Список секретов.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка на сервере.

**Пример**:
```json
{
    "secrets": [
        {
            "id": 1,
            "name": "example_secret",
            "encrypted_data": "encrypted_data_here"
        }
    ]
}
```

#### **POST /secrets/add**
Создаёт новый секрет.

**Запрос**:
- `name`: (str) Имя секрета.
- `encrypted_data`: (str) Зашифрованные данные секрета.

**Ответ**:
- `200 OK`: Секрет успешно создан.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка на сервере.

**Пример**:
```json
{
    "message": "Secret added successfully",
    "secret": "example_secret"
}
```

---

#### **POST /secrets/get**
Получает данные конкретного секрета.

**Запрос**:
- `name`: (str) Имя секрета.

**Ответ**:
- `200 OK`: Данные секрета.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка на сервере.

**Пример**:
```json
{
    "secret": {
        "name": "example_secret",
        "encrypted_data": "encrypted_data_here"
    }
}
```

---

#### **PUT /secrets/update**
Обновляет существующий секрет.

**Запрос**:
- `name`: (str) Имя секрета.
- `encrypted_data`: (str) Зашифрованные данные секрета.

**Ответ**:
- `200 OK`: Секрет успешно обновлен.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка на сервере.

**Пример**:
```json
{
    "message": "Secret updated successfully",
    "secret": "example_secret"
}
```

---

#### **DELETE /secrets/delete**
Удаляет секрет.

**Запрос**:
- `name`: (str) Имя секрета для удаления.

**Ответ**:
- `200 OK`: Секрет успешно удален.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка на сервере.

**Пример**:
```json
{
    "message": "Secret deleted successfully"
}
```

---

### **/notifications**

#### **POST /notifications/test**
Отправляет тестовое уведомление пользователю.

**Ответ**:
- `200 OK`: Тестовое уведомление успешно отправлено.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка при отправке уведомления.

**Пример**:
```json
{
    "message": "Test notification sent successfully"
}
```

---

#### **POST /notifications/connect_telegram**
Подключает Telegram аккаунт пользователя.

**Запрос**:
- `telegram_id`: (int) ID пользователя в Telegram.
- `username`: (str) Имя пользователя в Telegram.

**Ответ**:
- `200 OK`: Telegram успешно подключен.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка при подключении Telegram.

**Пример**:
```json
{
    "message": "Telegram connected successfully"
}
```

---

## **Ошибки**

- `401 Unauthorized`: Ошибка авторизации, например, неправильный токен.
- `403 Forbidden`: Отказ в доступе, например, недостаточно прав.
- `404 Not Found`: Ресурс не найден.
- `500 Internal Server Error`: Ошибка на сервере.
