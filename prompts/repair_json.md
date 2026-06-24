Ты — JSON-валидатор. Исправь следующий JSON, чтобы он соответствовал требуемой структуре.

Проблемы:
- JSON невалидный
- Отсутствуют обязательные поля
- Неправильные типы данных
- Содержит Markdown-разметку

Верни только исправленный JSON без комментариев, без Markdown.

Требуемая структура:

{
  "title": "string",
  "subtitle": "string",
  "language": "string",
  "age": number,
  "grade": "string",
  "topic": "string",
  "pack_type": "string",
  "difficulty": "string",
  "parent_instruction": "string",
  "pages": [
    {
      "page_number": number,
      "page_type": "string",
      "title": "string",
      "instruction": "string",
      "tasks": [
        {
          "type": "string",
          "question": "string",
          "options": ["string"],
          "answer_space": true,
          "answer": "string"
        }
      ]
    }
  ],
  "answers": [
    {
      "page_number": number,
      "answers": ["string"]
    }
  ]
}

Исходный JSON:
{{raw_json}}
