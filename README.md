# stats_service

### Описание сервиса сбора и анализа статистики устройств

---

#### **Назначение**  
Сервис предназначен для:  
- Сбора метрик (x, y, z)
- Анализа данных в реальном времени  
- Предоставления агрегированной статистики через REST API  
- Масштабируемой обработки запросов  

---

#### **Ключевые функции**  
1. **Управление пользователями и устройствами**  
   - Регистрация пользователей  
   - Создание виртуальных устройств  
   - Привязка устройств к пользователям  

2. **Сбор данных**  
   - Прием метрик от устройств в формате JSON  
   - Валидация и сохранение в БД  

3. **Аналитика**  
   - Расчет статистики за произвольный период:  
     - Минимум/максимум  
     - Сумма/медиана  
     - Количество записей  
   - Асинхронная обработка через Celery  

4. **Мониторинг**  
   - Отслеживание статуса задач  

---

#### **Технологический стек**  
| Категория       | Технологии                          |
|-----------------|-------------------------------------|
| **Backend**     | Python 3.11, FastAPI, SQLAlchemy    |
| **База данных** | PostgreSQL, Redis (кеширование)     |
| **Асинхронность** | Celery                            |
| **Инфраструктура** | Docker, Docker Compose           |
| **Тестирование**  | Locust                            |

---

### **API Endpoints**  

| Метод   | Путь                            | Описание                                  | Ответ                          |
|---------|---------------------------------|-------------------------------------------|--------------------------------|
| `GET`   | `/users/`                       | Получение списка пользователей            | `list[UserOut]`                |
| `POST`  | `/users/`                       | Создание пользователя                     | `UserOut`                      |
| `POST`  | `/devices/`                     | Регистрация устройства                    | `DeviceOut`                    |
| `GET`   | `/devices/{device_id}`          | Получение информации об устройстве        | `DeviceOut`                    |
| `POST`  | `/devices/{device_id}/stats/`   | Отправка метрик устройства                | `{"status": "ok"}`             |
| `GET`   | `/devices/{device_id}/analytics/` | Запуск анализа статистики устройства      | `TaskStatus` (начало задачи)   |
| `GET`   | `/tasks/{task_id}`              | Проверка статуса задачи анализа           | `TaskStatus` (результат)       |
| `GET`   | `/stats/`                       | Получение всей статистики                 | `list[StatResponse]`           |
| `GET`   | `/stats/{device_id}/`           | Получение статистики по устройству        | `list[StatResponse]`           |

---

#### **Особенности реализации**  
1. **Асинхронная обработка**  
   - Длительные операции анализа вынесены в Celery-задачи  
   - Использование Redis для хранения состояния задач  

2. **Безопасность**  
   - Валидация входных данных через Pydantic  
   - Обработка ошибок с детализированными HTTP-статусами  

3. **Производительность**  
   - Connection Pool для PostgreSQL  
   - Индексация по timestamp и device_id  

4. **Масштабируемость**  
   - Контейнеризация всех компонентов  
   - Возможность горизонтального масштабирования Celery Workers  

5. **Проверка ошибок**  
   Для всех эндпоинтов реализована обработка ошибок:
   - `404 Not Found` — если устройство/пользователь не существует.  
   - `400 Bad Request` — при попытке создать дубликат email.  

---

#### **Развертывание**  
1. Требования:  
   - Docker 20.10+  
   - Docker Compose 2.0+  

2. Запуск:  
```bash
docker-compose up -d --build
```

3. Компоненты:  
   - **Web**: FastAPI (порт 8000)  
   - **DB**: PostgreSQL (порт 5432)  
   - **Queue**: Redis (порт 6379)  
   - **Monitoring**: Locust (порт 8089)  

---

#### **Тестирование API**

1. **Тестирование**  
   Примеры запросов через `curl`:
   ```bash
   # Создание пользователя
   curl -X POST "http://localhost:8000/users/" \
        -H "Content-Type: application/json" \
        -d '{"name": "User1", "email": "user1@test.com"}'

   # Создание устройства
   curl -X POST "http://localhost:8000/devices/" \
        -H "Content-Type: application/json" \
        -d '{"user_id": 1}'

   # Отправка метрик
   curl -X POST "http://localhost:8000/devices/8cb7.../stats/" \
        -H "Content-Type: application/json" \
        -d '{"x": 1.5, "y": 2.3, "z": 3.8}'

   # Получение аналитики
   curl "http://localhost:8000/devices/8cb7.../analytics/?start=2025-01-01T00:00:00&end=2025-12-31T23:59:59"
   ```

---

#### **Нагрузочное тестирование**  
1. **Нагрузочное тестирование**:  
```bash
locust -f locustfile.py --web-port 8090
```

2. **Метрики**:  
   - До 1000 RPS на запись метрик  
   - Среднее время ответа < 150 мс  

---

#### **Документация**  
- Swagger UI: `http://localhost:8000/docs`  
- Redoc: `http://localhost:8000/redoc`  

---