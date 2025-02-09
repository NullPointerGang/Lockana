### **Версия API**: v1

### **Основной роутер**: `/admin`, `/auth`, `/logs`, `/secrets`

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
- `200 OK`: Пользователь успешно создан.
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

#### **GET /logs/logs**
Получает список логов.

**Ответ**:
- `200 OK`: Список логов.

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

#### **DELETE /logs/logs-file**
Удаляет файл логов.

**Ответ**:
- `200 OK`: Файл успешно удалён.
- `401 Unauthorized`: Неверные данные авторизации.
- `500 Internal Server Error`: Ошибка при удалении файла.

**Пример**:
```json
{
    "message": "Internal server error"
}
```

---

#### **DELETE /logs**
Удаляет все логи из базы данных.

**Ответ**:
- `200 OK`: Логи успешно удалены.

**Пример**:
```json
{
    "message": "Successfully deleted logs from the database"
}
```

---

### **/secrets**

#### **GET /secrets/list**
Получает список секретов пользователя.

**Ответ**:
- `200 OK`: Список секретов.

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

#### **POST /secrets/create**
Создаёт новый секрет.

**Запрос**:
- `name`: (str) Имя секрета.
- `encrypted_data`: (str) Зашифрованные данные секрета.

**Ответ**:
- `200 OK`: Секрет успешно создан.
- `500 Internal Server Error`: Ошибка на сервере.

**Пример**:
```json
{
    "message": "Secret created successfully"
}
```

---

## **Ошибки**

- `401 Unauthorized`: Ошибка авторизации, например, неправильный токен.
- `403 Forbidden`: Отказ в доступе, например, недостаточно прав.
- `404 Not Found`: Ресурс не найден.
- `500 Internal Server Error`: Ошибка на сервере.
