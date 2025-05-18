'''from openai import OpenAI
import os
import json
from datetime import date

# Установка API-ключа
os.environ[
    'OPENAI_API_KEY'] = "API-TOKEN"
client = OpenAI()


# === Сохранение задач в tasks.json ===
def save_tasks_to_json(tasks, path="../../FrontEnd/screens/tasks.json"):
    today_str = date.today().isoformat()

    default_structure = {
        today_str: [],
        "recurring_exclusions": {},
        "recurring_status": {}
    }

    if not os.path.exists(path) or os.stat(path).st_size == 0:
        data = default_structure
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = default_structure

    if today_str not in data:
        data[today_str] = []

    for task in tasks:
        task["done"] = False
        task["source"] = "ai"
        data[today_str].append(task)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def generate_personal_prompt(description: str, path="../../database/user_data.json"):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": """
Ты — инженер ИИ. Получив подробное описание конкретного человека с ОВЗ или травмой, создай индивидуальный промт для медицинского ассистента.

🔧 Персональный промт должен:
- Учитывать диагноз, возраст, состояние, ограничения, стиль общения.
- Подсказывать, как реагировать в сложных ситуациях.
- Быть готовым к использованию в виде system prompt.
- Должен быть написан на русском

📌 Ответ строго в JSON:
{
  "prompt": "..."
}
"""},
            {"role": "user", "content": description}
        ]
    )

    result_text = response.choices[0].message.content
    try:
        new_data = json.loads(result_text)
    except json.JSONDecodeError:
        new_data = {"prompt": result_text}

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = {}
    else:
        existing_data = {}

    existing_data["prompt"] = new_data["prompt"]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    return existing_data


# === Генерация рекомендаций и задач ===
def ask_health_recommendations(description: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "system",
                "content": """
Ты медицинский ассистент. Получив подробное описание состояния человека с ОВЗ, ты:

1. Кратко формулируешь текстовые рекомендации по уходу.
2. Генерируешь список ежедневных задач в формате JSON.

⚠️ Строго следуй этим правилам:
- Каждая задача должна содержать поле \"time\" в формате \"HH:MM\".
- Никогда не используй абстрактные формулировки.
- Если время неизвестно — предположи.
- Поле \"done\" — всегда false.
- Поле \"recurring\" — true или false.
- Ответ только в JSON!

📌 Пример:
{
  "text": "Краткие рекомендации...",
  "tasks": [
    {
      "title": "Дать лекарства",
      "time": "10:00",
      "done": false,
      "recurring": true
    }
  ]
}
"""
            },
            {"role": "user", "content": description}
        ]
    )

    response_text = completion.choices[0].message.content
    try:
        result = json.loads(response_text)
        tasks = result.get("tasks", [])
        save_tasks_to_json(tasks)

        return result
    except json.JSONDecodeError as e:
        print("❌ Ошибка парсинга JSON:", e)
        print("Ответ:", response_text)
        return None
'''