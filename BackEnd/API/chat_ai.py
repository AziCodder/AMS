'''from openai import OpenAI
import os
import json

os.environ['OPENAI_API_KEY'] = "API-TOKEN"

client = OpenAI()


def ask_health_question(user_input: str):
    try:
        with open("../../database/user_data.json", "r", encoding="utf-8") as f:
            user_data = json.load(f)
        prompt = user_data.get("prompt", "")
    except Exception as e:
        prompt = ""

    full_prompt = f"""
    Всегда отвечай на русском.
    Пациент: {prompt}

    Далее пользователь задаёт вопрос:
    "{user_input}"

    Интерпретируй симптомы или медицинские вопросы и выдай предположительный диагноз, рекомендации или подходящего врача. Всегда отвечай строго в JSON формате.

    # Формат ответа (обязательно):
    {{
      "response_type": "diagnosis" или "advice",
      "text": "Рекомендации или совет по медицинскому запросу.",
      "diagnosis": "Предполагаемый диагноз, если есть.",
      "doctor": "Рекомендуемый специалист, если нужен."
    }}

    Если вопрос не медицинский, укажи, что ты можешь отвечать только по медицинской части. Не забывай учитывать состояние пациента, описанное выше.
    Также при просьбе пользователя выдавай информацию о пациенте(имя, возраст, диагноз, особенности и тд)
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    message = completion.choices[0].message
    text = message.content

    try:
        response_dict = json.loads(text)
        return response_dict
    except Exception as e:
        print("Ошибка парсинга JSON:", e)
        print("Ответ модели:", text)
        return {
            "response_type": "advice",
            "text": "⚠️ Не удалось обработать ответ ИИ.",
            "diagnosis": "",
            "doctor": ""
        }
'''