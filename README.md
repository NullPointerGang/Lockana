# Lockana

Lockana — это высокобезопасное решение для хранения и управления секретными данными, разработанное для обеспечения конфиденциальности и безопасности доступа к данным. Приложение использует современную аутентификацию через одноразовые пароли (TOTP) для получения доступа к данным, что гарантирует, что только авторизованные пользователи могут получить доступ к секретной информации.

## Основные особенности Lockana:

### 1. **Безопасность на первом месте:**

- Данные хранятся в зашифрованном виде.
- Доступ к данным возможен только после успешной аутентификации с использованием одноразового пароля (TOTP).
- Каждая попытка входа (успешная или неудачная) логируется для мониторинга активности и предупреждения о возможных угрозах.

### 2. **Централизованное управление секретами:**

- Секреты (например, API-ключи, пароли, ключи доступа) хранятся в одном месте, что упрощает управление.
- Возможность быстро обновлять или удалять секреты без необходимости изменения `.env` файлов или другого локального хранилища.

### 3. **Простой и быстрый доступ:**

- Запрос секретов осуществляется через API с использованием имени проекта и одноразового пароля.
- Возможность интеграции с различными сервисами и приложениями для безопасного доступа к данным.

### 4. **Мгновенные уведомления:**

- В случае любой попытки доступа (успешной или неуспешной) пользователю сразу отправляется уведомление, что обеспечивает дополнительный уровень безопасности.

### 5. **Изоляция и безопасность:**

- Lockana можно развернуть в изолированном окружении (например, в Docker), что минимизирует риски при эксплуатации.
- Логирование всех действий позволяет отслеживать, кто, когда и какие данные пытался получить.

## Преимущества использования Lockana:

- **Гибкость**: Легко интегрируется с любыми проектами и сервисами.
- **Простота использования**: API предоставляет простой и удобный интерфейс для запросов и управления секретами.
- **Конфиденциальность**: Хранение секретов в зашифрованном виде и использование TOTP для аутентификации минимизируют риски утечек данных.
- **Уведомления**: Мгновенные уведомления о попытках доступа дают вам контроль и видимость над активностью.

## Как работает Lockana:

1. **Аутентификация**: Пользователь отправляет запрос с именем проекта и одноразовым паролем (TOTP).
2. **Проверка данных**: API проверяет данные на сервере и, если всё верно, возвращает секреты, связанные с проектом.
3. **Уведомления**: В случае успешного или неудачного входа система отправляет уведомление пользователю.
4. **Логирование**: Все запросы и попытки доступа логируются для анализа безопасности.

Lockana идеально подходит для проектов, которым нужна безопасная и централизованная система для хранения и управления секретами, а также для тех, кто хочет избавиться от хранения чувствительных данных в файлах на сервере.

Ваши инструкции для установки выглядят в целом хорошо, но можно немного улучшить их для удобства и ясности. Вот несколько предложений:

1. **Пояснение для создания окружения**:
   Можно добавить, что при создании окружения лучше использовать `python -m venv` вместо `python3 -m venv` для большей совместимости, если на системе установлен только один Python 3.

2. **Уточнение в экспорте переменных окружения**:
   Можно добавить, что перед экспортом переменных нужно заменить `YOUR_SUPER_USER`, `YOUR_SUPER_PASSWORD` и `YOUR_SUPER_SECRET` на реальные значения.

3. **Завершение "TODO"**:
   Можно дополнить описание в `TODO` для большей информативности.

Вот обновленная версия:

---

## Установка

⚠️ **Важно!** ⚠️

Lockana использует MySQL для хранения данных, поэтому перед запуском убедитесь, что:  
- MySQL установлен, запущен и настроен корректно.  
- База данных создана и настроена, либо укажите параметры подключения в `config.yaml`.  
- Redis установлен и запущен, так как он используется для хранения JWT.  

Клонирование репозитория:
```bash 
git clone https://github.com/NullPointerGang/Lockana.git
```

Переход в деректорию:
```bash
cd Lockana
```

Создание вирутуального окружения:
```bash
python3 -m venv venv
```

Вход в виртуальное окружение:

```bash
source venv/bin/activate
```

Настройка:
 - Переменные виртуального окружения:

   ```bash
   export DATABASE_USER="vaule"     # Имя пользователя MySQL БД
   export MYSQL_PASSWORD="vaule"    # Пароль для пользователя
                                    #
   export JWT_SECRET_KEY="vaule"    # Секретный ключ для генерации JWT токенов
                                    #
   export SECRET_KEY="vaule"        # Секретный ключ для шифровки данных в БД
   ```

 - Конфигурационный файл:

   ```bash
   nano config.yaml
   ```

   ```yaml
   database:
      host: localhost  # Адрес хоста базы данных (например, localhost или IP)
      port: 3306  # Порт для подключения к базе данных MySQL
      name: lockana  # Имя базы данных

   jwt:
      access_token_expire_minutes: 1  # Время жизни токена доступа в минутах

   encryption:
      # Возможные алгоритмы шифрования:
      # aes - Алгоритм AES (симметричное шифрование)
      # rsa - Алгоритм RSA (асимметричное шифрование)
      # cha20cha20 - Алгоритм ChaCha20 (современный потоковый шифратор)
      algorithm: aes  # Выбранный алгоритм шифрования (по умолчанию aes)

   logging:
      filename: lockana.log  # Имя файла для логов
   ```

Установка зависимостей:
```
pip3 install -r requirements.txt
```

Запуск:

```bash
"./venv/bin/python3" "app.py"
```

Добавление пользователей:

Запустите скрипт `add_user.py`
```bash
python3 -m scripts.add_user
```
После чего вводите данные для содания пользователя. 

Если вы не ввели `Secret` то он сгенерируеться автоматичиски. 


## API Документация

Для доступа к API используется аутентификация через одноразовые пароли (TOTP). API позволяет безопасно запрашивать и управлять секретами через защищённый интерфейс. Подробнее о маршрутах и запросах читайте в [документации API](docs/API.md).

## Журнал изменений:

- `beta v1` — Первая бета-версия API. Система пользователей с ролями, управление пользователями и секретами.

- `RC v.1.1` — Кандидат на релиз. Нуждается в дополнительном тестировании, добавлены новые алгоритмы шифрования, такие как RSA и ChaCha20.
